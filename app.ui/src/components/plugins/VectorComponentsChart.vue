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
        :autoresize="{ throttle: 100 }" />

    </Transition>
  </div>
</template>

<script setup lang="ts">
import Chart from "vue-echarts";
import { ref, onMounted, onUnmounted, inject, watch } from "vue";
import { TimeseriesDataPoint, TimeseriesTable } from "../../managers/dataManager";
import { EmptySubscription, Subscription } from "../../observable";
import { safeFetch, PlayerApiClient as client, isNullOrUndefined } from "../../services/utilities";
import { BCol, BFormGroup, BRow } from "bootstrap-vue-next";
import { ColumnInfo } from "../../../services/restclient";
import { useVideoControl } from '../../composables/useVideoControl';
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
// import { Scatter3DChart, Scatter3DSeriesOption } from 'echarts-gl/charts';
// import { Grid3DComponent } from 'echarts-gl/components';
import { SetCardTitleFn } from "../../plugins/AppPlugins";
import { PluginServices } from "../../managers/pluginManager";

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


const setCardTitle = inject<SetCardTitleFn>('setCardTitle') ?? (() => { });

const pluginService = inject<PluginServices>('pluginService');
if (!pluginService) {
  throw new Error('Plugin service not found!');
}



type PluginState = {
  selectedColumn: ColumnInfo | null;
}


// --- Component Props ---
interface ScatterPlotProps {
  showMenu: boolean;

  id: string;
  pluginState?: PluginState;

}
const props = withDefaults(defineProps<ScatterPlotProps>(), {
  showMenu: false, // Default value for showMenu

  id: '', // Default value for id
  pluginState: () => ({
    selectedColumn: null,
  }),
});

const pluginState = ref<PluginState>(JSON.parse(JSON.stringify(props.pluginState)));

// --- Reactive State ---
const containerRef = ref<HTMLDivElement | null>(null);

const threeDChartRef = ref<typeof Chart | null>(null);
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
  const series = [];
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

    series.push({
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
    series: series,
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
  };
}





// --- Watchers ---
watch(pluginState, async (newValue) => {
  if (isNullOrUndefined(newValue.selectedColumn?.name)) {
    return;
  }


  const columnsToInitialize = [newValue.selectedColumn?.name];


  await pluginService.getDataManager().initialize(columnsToInitialize);

  // generate title based on selected columns
  let title = `Timestamp vs ${columnsToInitialize.join(' & ')}`;
  setCardTitle(title);

  const allMeasurements = pluginService.getDataManager().getAllMeasurements();

  componentChartOption.value = buildMultiGridVectorChart(allMeasurements);

  pluginService.savePluginState(props.id, newValue);

}, { deep: true, immediate: true });


// --- Lifecycle Hooks ---
onMounted(async () => {
  await loadColumns();



  const columnsToInit = []
  if (pluginState.value.selectedColumn) {
    columnsToInit.push(pluginState.value.selectedColumn.name);
  }

  if (columnsToInit.length != 0) {
    await pluginService.getDataManager().initialize(columnsToInit);
    const initialMeasurements = pluginService.getDataManager().getAllMeasurements();
    // updateChartData(initialMeasurements);

    let title = `${columnsToInit.join(' & ')}`;

    setCardTitle(title);
  }




  // Subscribe to live data updates
  subscription = pluginService.getDataManager().measurement$.subscribe((measurement: TimeseriesDataPoint) => {
    const vChartsRef = threeDChartRef.value;
    if (!vChartsRef) { return; }

    console.log("Received new measurement:", measurement);



  });
});

onUnmounted(() => {
  subscription?.unsubscribe();
});

const loadColumns = async () => {
  console.log("Loading columns...");
  const [error, response] = await safeFetch(() => client.getDataApiV1PlayerColumnsGet());
  if (response && response.columns) {
    const multiDimensionalColumns = response.columns.filter((c: any) => c.type.includes('object'));
    availableColumns.value = multiDimensionalColumns;
    console.log(`Loaded ${availableColumns.value.length} multidimensional columns.`);

  } else if (error) {
    console.error('Error loading columns:', error);
  } else {
    console.warn('No columns found or unexpected response structure.');
  }
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
