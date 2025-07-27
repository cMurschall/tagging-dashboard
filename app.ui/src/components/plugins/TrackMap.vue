<template>
  <div ref="containerRef" style="width: 100%; height: 100%;">
    <Transition name="fade" mode="out-in">
      <div v-if="showMenu">

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
import { useObservable } from "../../core/utilities/utilities";
import { ColumnInfo } from "../../../services/restclient";
import { PluginServices } from "@/types/plugin";
import { TimeseriesDataPoint } from "@/types/data";
import { EmptySubscription, Subscription } from "@/types/observable";

import cw2 from '@/assets/cw2.json';


use([ScatterChart, EffectScatterChart, GeoComponent, VisualMapComponent, GraphicComponent, DataZoomComponent, SVGRenderer]);



echarts.registerMap('Cruden World', cw2);
echarts.registerMap('empty', {
  type: 'FeatureCollection',
  features: []
});

const pluginService = inject<PluginServices>('pluginService');
if (!pluginService) {
  throw new Error('Plugin service not found!');
}


type PluginState = {

  selectedColumn: ColumnInfo | null;
}


const positionWithSpeed: [number, number, number, number][] = [];

const showMenu = useObservable(pluginService.showMenu$);

const pluginState = ref<PluginState>({
  selectedColumn: null,
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
    // {
    //   type: 'slider',
    //   xAxisIndex: 0
    // },
    // {
    //   type: 'slider',
    //   yAxisIndex: 0
    // }
  ],
  geo: {
    map: 'Cruden World', // Use the registered map name
    roam: true, // Enable zooming and panning

    itemStyle: {
      areaColor: '#e0ffff', // Default area color
      borderColor: '#aaa',  // Border color of regions
      borderWidth: 1
    },
    emphasis: { // Style when hovering over a region
      itemStyle: {
        areaColor: '#2a6a9b'
      },
      label: {
        show: true,
        color: '#fff'
      }
    }
  },
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


let resizeObserver: ResizeObserver | null = null;
let subscription: Subscription = EmptySubscription;



let lastSelectedColumn: ColumnInfo | null = null;

watch(pluginState, async (newValue) => {


  const selectedColumnUpdated = newValue.selectedColumn != lastSelectedColumn;

  // check if the selected column is different from the old value
  if (selectedColumnUpdated && newValue.selectedColumn) {
    await pluginService.getDataManager().initialize([newValue.selectedColumn.name]);
    // gaugeOption.value.series[0].data[0].name = newVal.selectedColumn.name;
    pluginService.cardTitle$.next(newValue.selectedColumn.name);

    lastSelectedColumn = newValue.selectedColumn;
  }


  // update =the new plugin state
  pluginService.savePluginState(newValue);

}, { deep: true });





onMounted(async () => {

  pluginState.value = pluginService.getPluginState() as PluginState || pluginState.value;

  await loadColumns();
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
  await pluginService.getDataManager().initialize(['car0_vehicle_pos', 'car0_velocity']);


  const data = pluginService.getDataManager().getAllMeasurements();


  const time = data.timestamps;
  const x = data.vectorValues["car0_vehicle_pos"][0]
  const y = data.vectorValues["car0_vehicle_pos"][1]
  const speed = data.scalarValues["car0_velocity"];

  for (let i = 0; i < x.length && i < speed.length; i += 10) {
    positionWithSpeed.push([x[i], y[i], speed[i], time[i]]);
  }

  chartRef.value?.setOption({
    visualMap: {
      type: 'continuous',
      min: Math.min(...speed),
      max: Math.max(...speed),
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
        `${Math.max(...speed).toFixed(1)} m/s`,
        `${Math.min(...speed).toFixed(1)} m/s`
      ]
    },
    series: [
      {
        name: 'Track',
        type: 'scatter',
        coordinateSystem: 'geo',
        symbolSize: 8,
        data: positionWithSpeed
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
  });

  subscription = pluginService.getDataManager().measurement$.subscribe((measurements: TimeseriesDataPoint) => {
    const vChartsRef = chartRef.value;
    if (!vChartsRef) { return; }

    const xValue = measurements['values']['car0_vehicle_pos'][0];
    const yValue = measurements['values']['car0_vehicle_pos'][1];



    // Convert logical coordinates → pixel space
    const pixel = vChartsRef.convertToPixel({ seriesIndex: 0 }, [xValue, yValue]);

    if (!pixel) return;

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
    const time = positionWithSpeed[dataIndex][3];

    pluginService.getVideoControl().seekTo(time);


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


</script>
