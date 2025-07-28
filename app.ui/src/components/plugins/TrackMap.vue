<template>
  <div ref="containerRef" style="width: 100%; height: 100%;">
    <Transition name="fade" mode="out-in">
      <div v-if="showMenu">
        <BRow class="mb-2">
          <BCol cols="12">
            <h4>Map Options</h4>
          </BCol>
        </BRow>
        <BRow>
          <BCol cols="6">
            <BFormGroup label="Select Z values column:">
              <FilterableSelect v-model="pluginState.selectedYColumn" :options="availableColumns"
                :getLabel="(item) => item.name" placeholder="Select column:" />
            </BFormGroup>
          </BCol>


          <BCol cols="6">

            <label for="mapSelect" class="form-label">Select Map:</label>
            <BFormSelect id="mapSelect" v-model="selectedMap">
              <option value="Cruden World">Cruden World</option>
              <option value="Empty">Empty</option>
            </BFormSelect>
          </BCol>
        </BRow>

        <BRow>
          <BCol cols="6">
            <label for="skipEveryNth" class="form-label mb-0">Skip every nth route point:</label>
            <BFormInput id="skipEveryNth" type="number" v-model="pluginState.skipEveryNth" size="sm"
              class="input-width-100" />
          </BCol>
        </BRow>

      </div>
    </Transition>

    <VChart ref="chartRef" :option="mapOption" :style="{ width: '100%', height: '100%' }" />

  </div>
</template>


<script setup lang="ts">
import { ref, onMounted, onUnmounted, inject, watch } from "vue";
import VChart from "vue-echarts";
import * as echarts from 'echarts/core';
import { use } from "echarts/core";
import { ScatterChart, EffectScatterChart } from "echarts/charts";
import { GeoComponent, VisualMapComponent, GraphicComponent, DataZoomComponent } from "echarts/components";
import { SVGRenderer, CanvasRenderer } from "echarts/renderers";
import { GeoJSONSourceInput } from "echarts/types/src/coord/geo/geoTypes.js";
import { useObservable } from "../../core/utilities/utilities";
import { ColumnInfo } from "../../../services/restclient";
import { PluginServices } from "@/types/plugin";
import { TimeseriesDataPoint } from "@/types/data";
import { EmptySubscription, Subscription } from "@/types/observable";

import cw2 from '@/assets/maps/cw2.json';



use([ScatterChart,
  EffectScatterChart,
  GeoComponent,
  VisualMapComponent,
  GraphicComponent,
  DataZoomComponent,
  CanvasRenderer]);




const selectedMap = ref<'Cruden World' | 'Empty'>('Cruden World');
echarts.registerMap('Cruden World', cw2 as GeoJSONSourceInput);
echarts.registerMap('Empty', {
  type: 'FeatureCollection',
  features: []
});

const pluginService = inject<PluginServices>('pluginService');
if (!pluginService) {
  throw new Error('Plugin service not found!');
}


type PluginState = {
  selectedYColumn: ColumnInfo | null;
  skipEveryNth: number;
}

// x, y, speed, time
const positionValues: [number, number, number, number][] = [];

const showMenu = useObservable(pluginService.showMenu$);

const pluginState = ref<PluginState>({
  selectedYColumn: null,
  skipEveryNth: 100
});


// Default gauge options
const mapOption = ref({
  xAxis: {
    type: 'value',
    show: false,
    nameLocation: 'middle',
    nameGap: 25,
    axisLine: { onZero: false }
  },
  yAxis: {
    type: 'value',
    show: false,
    nameLocation: 'middle',
    nameGap: 35,
    axisLine: { onZero: false }
  },
  dataZoom: [
    {
      type: 'inside',
      xAxisIndex: 0,
      yAxisIndex: 0
    },
  ],
  series: [
    {
      name: 'Track',
      type: 'scatter',
      coordinateSystem: 'geo',
      symbolSize: 2,
      data: [[]]
    }
  ]
});

const containerRef = ref(null);
const chartRef = ref<typeof VChart | null>(null);

const availableColumns = ref<ColumnInfo[]>([]);


watch(selectedMap, () => {
  updateChartOptions();
});


let resizeObserver: ResizeObserver | null = null;
let subscription: Subscription = EmptySubscription;



let lastSelectedColumn: ColumnInfo | null = null;

watch(pluginState, async (newValue) => {


  const selectedColumnUpdated = newValue.selectedYColumn != lastSelectedColumn;

  // check if the selected column is different from the old value
  if (selectedColumnUpdated && newValue.selectedYColumn) {
    await pluginService.getDataManager().initialize(['car0_vehicle_pos', newValue.selectedYColumn.name]);

    const title = `Map: ${selectedMap.value} with z-values: ${newValue.selectedYColumn.name}`;
    pluginService.cardTitle$.next(title);

    lastSelectedColumn = newValue.selectedYColumn;
    await loadData();
  }


  updateChartOptions();

  // update =the new plugin state
  pluginService.savePluginState(newValue);

}, { deep: true });





onMounted(async () => {

  pluginState.value = pluginService.getPluginState() as PluginState || pluginState.value;

  await loadColumns();

  if (!pluginState.value.selectedYColumn) {
    pluginState.value.selectedYColumn = availableColumns.value.find(c => c.name === 'car0_velocity') || null;
  }

  // Listen to resize events
  // Create a ResizeObserver to watch the container element
  if (containerRef.value) {
    resizeObserver = new ResizeObserver(() => {
      console.log("Resizing chart...");
      if (chartRef.value) {
        chartRef.value.resize();
      }
    });
    resizeObserver.observe(containerRef.value);
  }

  // check if we have a selected column
  await loadData();
  updateChartOptions();

  subscription = pluginService.getDataManager().measurement$.subscribe((measurements: TimeseriesDataPoint) => {
    const vChartsRef = chartRef.value;
    if (!vChartsRef) { return; }

    const pos = measurements.values['car0_vehicle_pos'] as number[];
    const xValue = pos[0];
    const yValue = pos[1];



    // Convert logical coordinates → pixel space
    const pixel = vChartsRef.convertToPixel({ seriesIndex: 0 }, [xValue, yValue]);
    if (!pixel || !Array.isArray(pixel)) return;

    const zr = vChartsRef.chart.getZr();
    const el = zr.storage.getDisplayList().find((el: any) => el.id === 'highlight-point');

    if (el) {
      el.attr({
        position: pixel,
        invisible: false
      });
    }


  });

  // Register click event
  chartRef.value?.chart.on('click', (params: any) => {

    const { dataIndex, value, componentType } = params;
    console.log('Track point clicked:', { dataIndex, value });

    pluginService.getVideoControl().seekTo(value[3]);


  });



});

onUnmounted(() => {

  // Disconnect the observer when the component is unmounted
  if (resizeObserver && containerRef.value) {
    resizeObserver.unobserve(containerRef.value);
    resizeObserver.disconnect();
  }
  subscription?.unsubscribe();
});



const loadColumns = async () => {

  var columns = await pluginService.getDataManager().getAvailableColumnNames();
  const numericalColumns = columns.filter(c => c.type == "scalar").map(c => {
    return {
      name: c.name,
      type: c.type,
    } as ColumnInfo;
  });
  availableColumns.value = numericalColumns;
}

const loadData = async () => {
  const selectedColumn = pluginState.value.selectedYColumn?.name ?? 'car0_velocity';
  await pluginService.getDataManager().initialize([selectedColumn, 'car0_vehicle_pos']);


  const data = pluginService.getDataManager().getAllMeasurements();


  const time = data.timestamps;
  const x = data.vectorValues["car0_vehicle_pos"][0]
  const y = data.vectorValues["car0_vehicle_pos"][1]
  const speed = data.scalarValues[selectedColumn];

  // Clear previous data
  positionValues.length = 0;
  for (let i = 0; i < x.length && i < speed.length; i++) {
    positionValues.push([x[i], y[i], speed[i], time[i]]);
  }
};

const updateChartOptions = () => {
  const boundingCoords = getBoundingCoords(positionValues.map(p => [p[0], p[1]]));

  const skipEveryNth = Math.max(pluginState.value.skipEveryNth, 1);
  const zValues = positionValues.length != 0 ? positionValues.map(p => p[2]) : [0];



  chartRef.value?.setOption({
    graphic: [
      {
        id: 'highlight-point',
        type: 'circle',
        shape: {
          cx: 0,
          cy: 0,
          r: 5,
        },
        style: {
          fill: 'red',
        },
        z: 100,
        zlevel: 2,
        invisible: true
      }
    ],

    geo: {
      map: selectedMap.value,
      roam: true,
      boundingCoords: selectedMap.value === 'Empty' ? boundingCoords : undefined,
      itemStyle: {
        areaColor: '#e0ffff',
        borderColor: '#aaa',
        borderWidth: 1
      },
      emphasis: {
        itemStyle: { areaColor: '#2a6a9b' },
        label: { show: true, color: '#fff' }
      }
    },
    visualMap: {
      type: 'continuous',
      min: Math.min(...zValues),
      max: Math.max(...zValues),
      dimension: 2,
      orient: 'vertical',
      right: 10,
      top: 20,
      calculable: true,
      inRange: {
        color: ['#00bcd4', '#8bc34a', '#ffc107']
      },
      formatter: (value: number) => "",
      text: [
        `${Math.max(...zValues).toFixed(1)}`,
        `${Math.min(...zValues).toFixed(1)}`
      ]
    },
    series: [
      {
        name: 'Track',
        type: 'scatter',
        coordinateSystem: 'geo',
        symbolSize: 8,
        data: positionValues.filter((_, index) => index % skipEveryNth === 0)
      },
      {
        name: 'Current Point',
        type: 'effectScatter',
        coordinateSystem: 'geo',
        data: [],
        symbolSize: 12,
        itemStyle: { color: 'red' },
        rippleEffect: { scale: 4, brushType: 'stroke' },
        zlevel: 10
      }
    ]
  }, true); // true for merge
};

const getBoundingCoords = (data: [number, number][]) => {
  if (data.length === 0) {
    return [[0, 0], [1, 1]];
  }
  const xs = data.map(p => p[0]);
  const ys = data.map(p => p[1]);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  return [[minX, minY], [maxX, maxY]];
};

</script>
