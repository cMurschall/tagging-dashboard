<template>
  <div ref="containerRef" style="width: 100%; height: 100%;">
    <Transition name="fade" mode="out-in">
      <div v-if="showMenu" class="p-3">
        <BRow class="mb-3">
          <BCol cols="12">
            <div role="group">
              <label for="column-filter-query">Search Columns:</label>
              <BFormInput id="column-filter-query" v-model="searchQuery" type="text" autocomplete="off"
                placeholder="Filter available columns..." />
            </div>
          </BCol>
        </BRow>

        <BRow class="mb-3">
          <BCol cols="12">
            <BFormGroup label="Select Primary Y Axis Column (Required):">
              <BFormSelect v-model="pluginState.selectedYColumnLeft" :options="filteredColumns" select-size="3"
                required />
            </BFormGroup>
          </BCol>
        </BRow>
        <BRow class="mb-3">
          <BCol cols="12">
            <BFormGroup label="Primary Y Axis Expression (e.g., value * 2):">
              <BFormInput v-model="pluginState.yAxisExpressionLeft" type="text" autocomplete="off"
                placeholder="Enter expression (use 'value')" />
            </BFormGroup>
          </BCol>
        </BRow>



        <BRow class="mb-3">
          <BCol cols="12">
            <BFormGroup label="Select Secondary Y Axis Column (Optional):">
              <BFormSelect v-model="pluginState.selectedYColumnRight" :options="filteredColumns" select-size="3" />
            </BFormGroup>
          </BCol>
        </BRow>
        <BRow class="mb-3">
          <BCol cols="12">
            <BFormGroup label="Secondary Y Axis Expression (e.g., value / 10):">
              <BFormInput v-model="pluginState.yAxisExpressionRight" type="text" autocomplete="off"
                placeholder="Enter expression (use 'value')" />
            </BFormGroup>
          </BCol>
        </BRow>
      </div>

      <Chart v-else ref="chartRef" :option="chartOption" :style="{ width: '100%', height: '100%' }"
        @zr:click="handleVChartClick" :autoresize="{ throttle: 100 }" />
    </Transition>
  </div>
</template>

<script setup lang="ts">
import Chart from "vue-echarts";
import { ref, onMounted, onUnmounted, inject, computed, watch } from "vue";
import { DataManager, TimeseriesDataPoint, TimeseriesTable } from "../../managers/dataManager";
import { Subscription } from "../../observable";
import { safeFetch, PlayerApiClient as client, TimestampStatistics, getTimestampStatistics } from "../../services/utilities";
import { BCol, BFormGroup, BFormSelect, BRow, BFormInput } from "bootstrap-vue-next";
import { ColumnInfo } from "../../../services/restclient";
import { useVideoControl } from './../../composables/useVideoControl';



import { use } from 'echarts/core'
import { ScatterChart } from 'echarts/charts'
import {
  LegendComponent,
  GridComponent,
  DataZoomComponent,
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
import { SeriesOption } from "echarts";
import gridManager from "../../managers/gridItemManager";
import { SetCardTitleFn } from "../../plugins/AppPlugins";

use([
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  GraphicComponent,
  TooltipComponent,
  ScatterChart,
  CanvasRenderer
])

type EChartsOption = ComposeOption<
  | LegendComponentOption
  | GridComponentOption
  | DataZoomComponentOption
  | GraphicComponentOption
  | TooltipComponentOption
  | ScatterSeriesOption
>


const setCardTitle = inject<SetCardTitleFn>('setCardTitle') ?? (() => {});


const { seekTo } = useVideoControl();
const dataManager = inject<DataManager>('dataManager');
if (!dataManager) {
  throw new Error('dataManager not provided');
}


type PluginState = {
  selectedYColumnLeft: ColumnInfo | null;
  selectedYColumnRight: ColumnInfo | null;
  yAxisExpressionLeft: string;
  yAxisExpressionRight: string;
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
    selectedYColumnLeft: null,
    selectedYColumnRight: null,
    yAxisExpressionLeft: 'value',
    yAxisExpressionRight: 'value',
  }),
});

const pluginState = ref<PluginState>(structuredClone(props.pluginState));

// --- Reactive State ---
const containerRef = ref<HTMLDivElement | null>(null);
const chartRef = ref<typeof Chart | null>(null);
const searchQuery = ref('');
const availableColumns = ref<BFormSelectColumnInfo[]>([]);




let currentTimestampStatistics: TimestampStatistics | null = null;
let subscription: Subscription | null = null;


interface BFormSelectColumnInfo {
  text: string;
  value: ColumnInfo | null;
  disabled?: boolean;
}

// --- Computed Properties ---


const filteredColumns = computed(() => {
  const noneOption: BFormSelectColumnInfo = { text: '(None - Single Axis)', value: null };
  return [
    noneOption,
    ...availableColumns.value
      .filter(c => c.text.toLowerCase().includes(searchQuery.value.toLowerCase()))
  ];
});


// --- ECharts Option ---
const chartOption = ref<EChartsOption>({
  // title: {
  //   // text: "Chart Title",
  // },
  legend: {
    orient: 'vertical',
    right: 10,
    show: true,
  },
  xAxis: [{
    scale: true
  }],
  yAxis: [{
    scale: true
  }],
  dataZoom: [
    {
      type: 'inside',
    },
    {
      type: 'slider'
    }
  ],
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
      z: 10000, // make sure it's on top
      zlevel: 1,
    }
  ],
  series: [
    {
      id: 'SeriesA',
      name: 'A',
      type: 'scatter',
      data: new Float64Array(),
      dimensions: ['x', 'y'],
      symbolSize: 3,
      itemStyle: {
        opacity: 0.8
      },
      large: true
    },
    {
      id: 'SeriesB',
      name: 'B',
      type: 'scatter',
      data: new Float64Array(),
      dimensions: ['x', 'y'],
      symbolSize: 3,
      itemStyle: {
        opacity: 0.8
      },
      large: true
    },
  ],
  tooltip: {
    trigger: 'axis', // Trigger tooltip on axis pointer move
    axisPointer: {
      type: 'line', // Show a line axis pointer
      lineStyle: {
        color: 'red',
        width: 1
      },
      z: 100 // Ensure it's on top
    },
  },
  animation: false
});

// --- Methods ---
const handleVChartClick = (params: ElementEvent) => {

  const chart = chartRef.value;
  if (!chart) return;


  const [x, _] = chart.convertFromPixel({ seriesIndex: 0 }, [params.offsetX, params.offsetY]);
  seekTo(x); // Call the seekTo function with the x value
};


const updateChartData = (table: TimeseriesTable) => {
  console.log("Updating chart data from TimeseriesTable...");


  // Store the current data table so we can later find the first and last timestamps more easily
  currentTimestampStatistics = getTimestampStatistics(table);

  // Check if the table and required column data exist
  if (!table || !table.timestamps || !table.values) {
    console.warn("updateChartData called with invalid table data.");
    return;
  }

  // Get selected column names
  const primaryColName = pluginState.value?.selectedYColumnLeft?.name;
  const secondaryColName = pluginState.value?.selectedYColumnRight?.name;


  const primaryValues = primaryColName ? table.values[primaryColName] : undefined;
  const secondaryValues = secondaryColName ? table.values[secondaryColName] : undefined;

  // Initialize data arrays for ECharts series
  const primaryData: Float64Array = new Float64Array(table.timestamps.length * 2);
  const secondaryData: Float64Array = new Float64Array(table.timestamps.length * 2);


  // Ensure timestamp array and value arrays (if they exist) have the same length
  const len = table.timestamps.length;
  if (primaryValues && primaryValues.length !== len) {
    console.error(`Timestamp count (${len}) and primary column (${primaryColName}) value count (${primaryValues.length}) mismatch.`);
    // Optionally handle this error, e.g., by returning or trying to align data
    return; // Stop processing if lengths mismatch
  }
  if (secondaryValues && secondaryValues.length !== len) {
    console.error(`Timestamp count (${len}) and secondary column (${secondaryColName}) value count (${secondaryValues.length}) mismatch.`);
    // Optionally handle this error
    return; // Stop processing if lengths mismatch
  }

  // Iterate through timestamps and process data

  // Use a single loop to process both primary and secondary data
  for (let i = 0; i < len; i++) {
    if (primaryValues) {
      primaryData[i * 2] = table.timestamps[i];
    }
    if (secondaryValues) {
      secondaryData[i * 2] = table.timestamps[i];
    }

    if (primaryValues) {
      primaryData[i * 2 + 1] = primaryValues[i]
    }
    if (secondaryValues) {
      secondaryData[i * 2 + 1] = secondaryValues[i]
    }
  }


  // Update the chart options with the processed data
  const series = chartOption.value.series as SeriesOption[];
  series[0].data = primaryValues ? primaryData : new Float64Array(0);
  series[1].data = secondaryValues ? secondaryData : new Float64Array(0);


  // Update axis names based on selections
  series[0].name = primaryColName ? `${primaryColName}` : '';
  series[1].name = secondaryColName ? `${secondaryColName}` : '';

  // Show legend only if a secondary column is selected and has data
  // chartOption.value.legend.show = !!secondaryColName && secondaryData.length > 0;

  console.log(`Processed data points - Primary: ${primaryData ? primaryData.length : 0}, Secondary: ${secondaryData.length}`);
};

// --- Watchers ---
watch(pluginState, async (newValue) => {
  const series = chartOption.value.series as SeriesOption[];

  const hasLeftColumn = !!newValue.selectedYColumnLeft;
  const hasRightColumn = !!newValue.selectedYColumnRight;


  if (!hasRightColumn) {
    series[0].data = new Float64Array(0);
  }
  if (!hasRightColumn) {
    series[1].data = new Float64Array(0);
  }
  if (!hasLeftColumn && !hasRightColumn) {
    // clear hightlight point
    const zr = chartRef.value?.chart.getZr();
    const el = zr?.storage.getDisplayList().find((el: any) => el.id == 'highlight-point');
    if (el) {
      el.attr({ invisible: true });
    }

  }


  const columnsToInitialize = [];
  if (newValue.selectedYColumnLeft) {
    columnsToInitialize.push(newValue.selectedYColumnLeft.name);
  }
  if (newValue.selectedYColumnRight) {
    columnsToInitialize.push(newValue.selectedYColumnRight.name);
  }

  await dataManager.initialize(columnsToInitialize);

  // generate title based on selected columns
  let title = `Timestamp vs ${columnsToInitialize.join(' & ')}`;
  setCardTitle(title);

  const allMeasurements = dataManager.getAllMeasurements();
  updateChartData(allMeasurements);


  // update the gridmanager with the new plugin state
  gridManager.updateItemById(props.id, {
    pluginState: { ...newValue }
  });

}, { deep: true, immediate: true });


// --- Lifecycle Hooks ---
onMounted(async () => {
  await loadColumns();



  const columnsToInit = []
  if (pluginState.value.selectedYColumnLeft) {
    columnsToInit.push(pluginState.value.selectedYColumnLeft.name);
  }
  if (pluginState.value.selectedYColumnRight) {
    columnsToInit.push(pluginState.value.selectedYColumnRight.name);
  }

  if (columnsToInit.length != 0) {
    await dataManager.initialize(columnsToInit);
    const initialMeasurements = dataManager.getAllMeasurements();
    updateChartData(initialMeasurements);

    let title = `Timestamp vs ${columnsToInit.join(' & ')}`;

    setCardTitle(title);
  }




  // Subscribe to live data updates
  subscription = dataManager.measurement$.subscribe((measurement: TimeseriesDataPoint) => {

    // check if new timestamp is in the range of the first series. if yes put point on the first series
    if (!currentTimestampStatistics || currentTimestampStatistics?.count == 0) {
      return;
    }

    const firstTimestamp = currentTimestampStatistics.min;
    const lastTimestamp = currentTimestampStatistics.max;


    let xValue: number = 0
    let yValue: number = measurement.values[pluginState.value?.selectedYColumnLeft?.name ?? 0] ?? 0;

    if (measurement.timestamp < firstTimestamp) {
      xValue = firstTimestamp
    }
    else if (measurement.timestamp > lastTimestamp) {
      xValue = lastTimestamp;
    }
    else {
      xValue = measurement.timestamp;
    }

    const vChartsRef = chartRef.value;
    if (!vChartsRef) { return; }


    const [x, y] = vChartsRef.convertToPixel({ seriesIndex: 0 }, [xValue, yValue]);

    const zr = vChartsRef.chart.getZr();
    const el = zr.storage.getDisplayList().find((el: any) => el.id == 'highlight-point');

    if (el) {
      el.attr({ position: [x, y], invisible: false });
    }



  });
});

onUnmounted(() => {
  subscription?.unsubscribe();
  // // Clean up ResizeObserver
  // if (resizeObserver && containerRef.value) {
  //   resizeObserver.unobserve(containerRef.value);
  //   resizeObserver.disconnect();
  //   console.log("ResizeObserver disconnected");
  // }
  // resizeObserver = null;
});

const loadColumns = async () => {
  console.log("Loading columns...");
  const [error, response] = await safeFetch(() => client.getDataApiV1PlayerColumnsGet());
  if (response && response.columns) {
    const numericColumns = response.columns.filter((c: any) =>
      c.type.includes('int') || c.type.includes('float') || c.type.includes('double')
    );
    availableColumns.value = numericColumns.map((x: ColumnInfo) => ({ text: x.name, value: x }));
    console.log(`Loaded ${availableColumns.value.length} numeric columns.`);

    // const preSelectedColumn = numericColumns.find((c: ColumnInfo) => c.name === 'car0_velocity_vehicle');
    // if (preSelectedColumn) {
    //   selectedYColumnLeft.value = preSelectedColumn;
    //   console.log("Pre-selected primary column:", preSelectedColumn.name);
    // } else if (numericColumns.length > 0) {
    //   selectedYColumnLeft.value = numericColumns[0];
    //   console.log("Pre-selected primary column (fallback):", numericColumns[0].name);
    // }
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
