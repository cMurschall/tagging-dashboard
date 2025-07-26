<template>
  <div ref="containerRef" style="width: 100%; height: 100%;">
    <Transition name="fade" mode="out-in">
      <div v-if="showMenu" class="p-3">

        <BRow class="mb-3">
          <BCol cols="12">
            <BFormGroup label="Select Column (Required):">
              <FilterableSelect v-model="pluginState.selectedColumn" :options="availableColumns"
                :getLabel="(item) => item.name" placeholder="Select column:" />
            </BFormGroup>
          </BCol>
        </BRow>
      </div>

      <Chart v-else ref="componentChartRef" :option="componentChartOption" :style="{ width: '100%', height: '100%' }"
        @zr:click="handleVChartClick" :autoresize="{ throttle: 100 }" />

    </Transition>
  </div>
</template>

<script setup lang="ts">
import Chart from "vue-echarts";
import { ref, onMounted, onUnmounted, inject, watch } from "vue";
import { isNullOrUndefined, useObservable } from "../../core/utilities/utilities";
import { BCol, BFormGroup, BRow } from "bootstrap-vue-next";
import { ColumnInfo } from "../../../services/restclient";
// import { useVideoControl } from '../../composables/useVideoControl';
import FilterableSelect from "./../FilterableSelect.vue";
import { use } from 'echarts/core'
import { ScatterChart } from 'echarts/charts'
import {
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  TitleComponent,
  GraphicComponent,
  TooltipComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { ComposeOption, ElementEvent } from 'echarts/core'
import type { ScatterSeriesOption } from 'echarts/charts'
import type {
  LegendComponentOption,
  GridComponentOption,
  DataZoomComponentOption,
  GraphicComponentOption,
  TooltipComponentOption
} from 'echarts/components'
import { PluginServices } from "@/types/plugin";
import { EmptySubscription, Subscription } from "@/types/observable";
import { TimeseriesTable, TimeseriesDataPoint } from "@/types/data";
// import { Scatter3DChart, Scatter3DSeriesOption } from 'echarts-gl/charts';
// import { Grid3DComponent } from 'echarts-gl/components';
use([
  TitleComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  GraphicComponent,
  TooltipComponent,
  ScatterChart,
  CanvasRenderer,
  // Scatter3DChart,
  // Grid3DComponent
])

type EChartsOption = ComposeOption<
  | LegendComponentOption
  | GridComponentOption
  | DataZoomComponentOption
  | GraphicComponentOption
  | TooltipComponentOption
  | ScatterSeriesOption
// | Scatter3DSeriesOption
>


const pluginService = inject<PluginServices>('pluginService');
if (!pluginService) {
  throw new Error('Plugin service not found!');
}

const showMenu = useObservable(pluginService.showMenu$);

type PluginState = {
  selectedColumn: ColumnInfo | null;
}



const pluginState = ref<PluginState>({
  selectedColumn: null,
});

// --- Reactive State ---
const containerRef = ref<HTMLDivElement | null>(null);
const componentChartRef = ref<typeof Chart | null>(null);
const availableColumns = ref<ColumnInfo[]>([]);



let subscription: Subscription = EmptySubscription;


// --- ECharts Option ---




const componentChartOption = ref<EChartsOption>({
  tooltip: {
    trigger: 'axis'
  },
  xAxis: {
    type: 'value',
    name: 'Time'
  },
  yAxis: {
    type: 'value',
    name: 'Component Value'
  },
  series: []
});

// --- Methods ---

const buildMultiGridVectorChart = (table: TimeseriesTable): any => {
  const firstVectorKey = Object.keys(table.vectorValues)[0];
  const vectors = table.vectorValues[firstVectorKey];

  if (!vectors || vectors.length === 0) {
    console.warn("No vector data available");
    return;
  }

  const numComponents = vectors.length;

  const grids = [];
  const xAxes = [];
  const yAxes = [];
  const dataSeries = [];
  const titles = [];

  const gridHeight = 100 / numComponents;

  for (let i = 0; i < numComponents; i++) {
    grids.push({
      top: `${i * gridHeight + 5}%`,
      height: `${gridHeight - 10}%`,
      containLabel: true,
    });

    xAxes.push({
      type: 'value',
      scale: true,
      gridIndex: i,
      axisLabel: {
        show: i === numComponents - 1, // only bottom axis
      },
      name: i === numComponents - 1 ? 'Timestamp' : '',
      nameLocation: 'middle',
      nameGap: 30,
    });

    yAxes.push({
      type: 'value',
      scale: true,
      gridIndex: i,
    });

    const componentData = new Float64Array(table.timestamps.length * 2);
    for (let j = 0; j < table.timestamps.length; j++) {
      componentData[j * 2] = table.timestamps[j]; // x
      componentData[j * 2 + 1] = vectors[i][j];    // y
    }

    dataSeries.push({
      id: `Series${i}`,
      name: `Component ${i + 1}`,
      type: 'scatter',
      xAxisIndex: i,
      yAxisIndex: i,
      data: componentData,
      dimensions: ['x', 'y'],
      symbolSize: 3,
      itemStyle: {
        opacity: 0.8,
      },
      large: true,
      showSymbol: false,
      zlevel: 0,
      z: 2      // Standard z for series
    });

    titles.push({
      top: `${i * gridHeight + 2}%`,
      left: 'center',
      text: `Component ${i}`,
      textStyle: { fontSize: 12 },
    });

  }


  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'line',
        link: { xAxisIndex: 'all' }, // sync x-axes
      },
      lineStyle: {
        color: 'red',
        width: 1
      },
    },
    grid: grids,
    xAxis: xAxes,
    yAxis: yAxes,
    series: dataSeries,
    dataZoom: [
      {
        type: 'slider',
        xAxisIndex: Array.from({ length: numComponents }, (_, i) => i),
        height: 20,
        bottom: 0,
      },
      {
        type: 'inside',
        xAxisIndex: Array.from({ length: numComponents }, (_, i) => i),
      }
    ],
    graphic: table.timestamps.length > 0
      ? Array.from({ length: numComponents }, (_, i) => ({
        id: `highlight-point-${i}`,
        type: 'circle',
        zlevel: 1 + i,
        z: 10,
        shape: { r: 5 },
        style: { fill: 'red' },
        // Use `coord` to position it using data coords
        // This will be updated later
        position: [0, 0],
        // Initial invisible (or start at [x0, y0])
        invisible: true,
        coordSystem: 'cartesian2d',
        xAxisIndex: i,
        yAxisIndex: i,
      }))
      : [],
  };
}



const handleVChartClick = (params: ElementEvent) => {

  if (!params.target) {

    const chart = componentChartRef.value;
    if (!chart) return;


    const [x, _] = chart.convertFromPixel({ seriesIndex: 0 }, [params.offsetX, params.offsetY]);
    pluginService.getVideoControl().seekTo(x); // Call the seekTo function with the x value
  }
};

// --- Watchers ---
watch(pluginState, async (newValue) => {
  if (isNullOrUndefined(newValue.selectedColumn?.name)) {
    return;
  }


  const columnsToInitialize = [newValue.selectedColumn?.name];


  await pluginService.getDataManager().initialize(columnsToInitialize);

  // generate title based on selected columns
  let title = `Timestamp vs ${columnsToInitialize.join(' & ')}`;
  pluginService.cardTitle$.next(title);

  const allMeasurements = pluginService.getDataManager().getAllMeasurements();

  componentChartOption.value = buildMultiGridVectorChart(allMeasurements);

  pluginService.savePluginState(newValue);

}, { deep: true, immediate: true });


// --- Lifecycle Hooks ---
onMounted(async () => {

  pluginState.value = pluginService.getPluginState() as PluginState || pluginState.value;

  await loadColumns();



  const columnsToInit = []
  if (pluginState.value.selectedColumn) {
    columnsToInit.push(pluginState.value.selectedColumn.name);
  }

  if (columnsToInit.length != 0) {
    await pluginService.getDataManager().initialize(columnsToInit);
    const allMeasurements = pluginService.getDataManager().getAllMeasurements();
    componentChartOption.value = buildMultiGridVectorChart(allMeasurements);
    let title = `${columnsToInit.join(' & ')}`;

    pluginService.cardTitle$.next(title);
  }




  // Subscribe to live data updates
  subscription = pluginService.getDataManager().measurement$.subscribe((measurement: TimeseriesDataPoint) => {




    const chart = componentChartRef.value;
    if (!chart) return;

    const vector = measurement.values[pluginState.value.selectedColumn?.name ?? ''];
    // console.log("Received new measurement:", vector);


    if (!vector || !Array.isArray(vector) || vector.length === 0) {
      console.warn("No vector data available");
      return;
    }

    const newTimestamp = measurement.timestamp;
    const numComponents = vector.length;



    const zr = chart.chart.getZr();
    for (let i = 0; i < numComponents; i++) {
      const [x, y] = chart.convertToPixel({ seriesIndex: i }, [newTimestamp, vector[i]]);

      const el = zr.storage.getDisplayList().find((el: any) => el.id == `highlight-point-${i}`);
      if (el) {

        el.attr({ position: [x, y], invisible: false });
      }

    }


  });
});

onUnmounted(() => {
  subscription?.unsubscribe();
});

const loadColumns = async () => {
  console.log("Loading columns...");

  var columns = await pluginService.getDataManager().getAvailableColumnNames();
  const numericalColumns = columns.filter(c => c.type == "vector").map(c => {
    return {
      name: c.name,
      type: c.type,
    } as ColumnInfo;
  });
  availableColumns.value = numericalColumns;

};




</script>

<style scoped>
/* Add transition styles */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Ensure form groups have some spacing */
.b-form-group {
  margin-bottom: 1rem;
}

/* Style select boxes */
.b-form-select {
  max-height: 150px;
  /* Limit height of multi-select */
}

/* Minor padding for the menu container */
.p-3 {
  padding: 1rem;
}

/* Ensure chart takes full height when visible */
.v-chart {
  width: 100%;
  height: 100%;
  min-height: 300px;
  /* Ensure chart has a minimum height */
}
</style>
