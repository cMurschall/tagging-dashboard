<template>
  <div ref="containerRef" style="width: 100%; height: 100%;">
    <Transition name="fade" mode="out-in">
      <div v-if="showMenu" class="p-3">

        <BRow class="mb-3">
          <BCol cols="12">
            <BFormGroup label="Select Primary Y Axis Column (Required):">

              <FilterableSelect v-model="pluginState.selectedYColumnLeft" :options="availableColumns"
                :getLabel="(item) => item.name" placeholder="Select column:" />
            </BFormGroup>

            {{ pluginState.selectedYColumnLeft }}

          </BCol>
        </BRow>
        <BRow class="mb-3">
          <BCol cols="12">
            <BFormGroup label="Primary Y Axis Expression:">
              <BlurUpdateInput v-model="pluginState.yAxisExpressionLeft" type="text" autocomplete="off"
                :placeholder="defaultExpressionHint" />
            </BFormGroup>
          </BCol>
        </BRow>



        <BRow class="mb-3">
          <BCol cols="12">
            <BFormGroup label="Select Secondary Y Axis Column (Optional):">
              <!-- <BFormSelect v-model="pluginState.selectedYColumnRight" :options="filteredColumns" select-size="3" /> -->
              <FilterableSelect v-model="pluginState.selectedYColumnRight" :options="availableColumns"
                :getLabel="(item) => item.name" placeholder="Select column:" />
            </BFormGroup>

            {{ pluginState.selectedYColumnRight }}
          </BCol>
        </BRow>
        <BRow class="mb-3">
          <BCol cols="12">
            <BFormGroup label="Secondary Y Axis Expression:">
              <BlurUpdateInput v-model="pluginState.yAxisExpressionRight" type="text" autocomplete="off"
                :placeholder="defaultExpressionHint" />
            </BFormGroup>
          </BCol>
        </BRow>
      </div>

      <Chart v-else ref="chartRef" :option="chartOption" :style="{ width: '100%', height: '100%' }"
        @zr:click="handleVChartClick" :autoresize="{ throttle: 100 }"
        @legendselectchanged="handleVChartSelectChanged" />
    </Transition>
  </div>
</template>

<script setup lang="ts">
import Chart from "vue-echarts";
import { ref, onMounted, onUnmounted, inject, watch } from "vue";
import {  getTimestampStatistics, clamp, transformMathJsValue,
  IDENTITY_EXPRESSION,
  useObservable
} from "../../core/utilities/utilities";
import { BCol, BFormGroup, BRow } from "bootstrap-vue-next";
import { ColumnInfo } from "../../../services/restclient";
// import { useVideoControl } from './../../composables/useVideoControl';
import FilterableSelect from './../FilterableSelect.vue';
import BlurUpdateInput from './../BlurUpdateInput.vue';
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
import { TimeseriesTable, TimeseriesDataPoint, TimestampStatistics } from "@/types/data";
import { Subscription, EmptySubscription } from "@/types/observable";
import { PluginServices } from "@/types/plugin";

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


const pluginService = inject<PluginServices>('pluginService');
if (!pluginService) {
  throw new Error('Plugin service not found!');
}


type PluginState = {
  selectedYColumnLeft: ColumnInfo | null;
  selectedYColumnRight: ColumnInfo | null;
  yAxisExpressionLeft: string;
  yAxisExpressionRight: string;
}


const showMenu = useObservable(pluginService.showMenu$);

const pluginState = ref<PluginState>({
  selectedYColumnLeft: null,
  selectedYColumnRight: null,
  yAxisExpressionLeft: IDENTITY_EXPRESSION,
  yAxisExpressionRight: IDENTITY_EXPRESSION,
});

// --- Reactive State ---
const containerRef = ref<HTMLDivElement | null>(null);
const chartRef = ref<typeof Chart | null>(null);
// const searchQuery = ref('');
const availableColumns = ref<ColumnInfo[]>([]);

const defaultExpressionHint = `Enter expression (use '${IDENTITY_EXPRESSION}')`;


let currentTimestampStatistics: TimestampStatistics | null = null;
let subscription: Subscription = EmptySubscription;




// --- ECharts Option ---

const chartOption = ref<EChartsOption>({
  legend: {
    orient: 'vertical',
    right: 10,
    show: true,
  },
  xAxis: [{
    scale: true,
    axisLabel: {
      formatter: (value: number) => (value).toFixed(0) + 's'
    }
  }],
  yAxis: [{
    scale: true
  }, {
    scale: true,
    position: 'right' // Align the second y-axis to the right
    // Add any other specific styling for the right y-axis here
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
      z: 100, // make sure it's on top
      zlevel: 2,
      invisible: true, // start as invisible
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
      large: true,
      zlevel: 1,
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
      large: true,
      yAxisIndex: 1,
      zlevel: 1,
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

const getLeftSeries = () => {
  const series = chartOption.value.series as SeriesOption[];
  return series[0];
};
const getRightSeries = () => {
  const series = chartOption.value.series as SeriesOption[];
  return series[1];
};

const handleVChartClick = (params: ElementEvent) => {

  if (!params.target) {

    const chart = chartRef.value;
    if (!chart) return;


    const [x, _] = chart.convertFromPixel({ seriesIndex: 0 }, [params.offsetX, params.offsetY]);
    pluginService.getVideoControl().seekTo(x); // Call the seekTo function with the x value
  }
};

let selectedSeries: Record<string, boolean> = {};
const handleVChartSelectChanged = (params: any) => {

  selectedSeries = params.selected;
  console.log("SelectionChanged:", selectedSeries);
};


const updateChartData = (table: TimeseriesTable) => {
  console.log("Updating chart data from TimeseriesTable...");


  // Store the current data table so we can later find the first and last timestamps more easily
  currentTimestampStatistics = getTimestampStatistics(table);

  // Check if the table and required column data exist
  if (!table || !table.timestamps || !table.scalarValues) {
    console.warn("updateChartData called with invalid table data.");
    return;
  }

  // Get selected column names
  const primaryColName = pluginState.value?.selectedYColumnLeft?.name;
  const secondaryColName = pluginState.value?.selectedYColumnRight?.name;


  const primaryValues = primaryColName ? table.scalarValues[primaryColName] : undefined;
  const secondaryValues = secondaryColName ? table.scalarValues[secondaryColName] : undefined;

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

    // add the x value to the data array
    const xIndex = i * 2;
    const YIndex = xIndex + 1;
    if (primaryValues) {
      primaryData[xIndex] = table.timestamps[i];
    }
    if (secondaryValues) {
      secondaryData[xIndex] = table.timestamps[i];
    }

    // add the y value to the data array
    if (primaryValues) {
      if (pluginState.value.yAxisExpressionLeft) {
        primaryData[YIndex] = transformMathJsValue(primaryValues[i], pluginState.value.yAxisExpressionLeft);
      } else {
        primaryData[YIndex] = primaryValues[i]
      }
    }
    if (secondaryValues) {
      if (pluginState.value.yAxisExpressionRight) {
        secondaryData[YIndex] = transformMathJsValue(secondaryValues[i], pluginState.value.yAxisExpressionRight);
      } else {
        secondaryData[YIndex] = secondaryValues[i]
      }
    }
  }


  // Update the chart options with the processed data
  const leftData = primaryValues ? primaryData : new Float64Array(0);
  const rightData = secondaryValues ? secondaryData : new Float64Array(0);
  getLeftSeries().data = leftData;
  getRightSeries().data = rightData;



  // Update axis names based on selections
  getLeftSeries().name = primaryColName ? `${primaryColName}` : '';
  getRightSeries().name = secondaryColName ? `${secondaryColName}` : '';


  console.log(`Processed data points - Primary: ${primaryData ? primaryData.length : 0}, Secondary: ${secondaryData.length}`);
};

// --- Watchers ---
watch(pluginState, async (newValue) => {

  const hasLeftColumn = !!newValue.selectedYColumnLeft;
  const hasRightColumn = !!newValue.selectedYColumnRight;


  if (!hasLeftColumn) {
    getLeftSeries().data = new Float64Array(0);
  }
  if (!hasRightColumn) {
    getRightSeries().data = new Float64Array(0);
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
    selectedSeries[newValue.selectedYColumnLeft.name] = true;
  }
  if (newValue.selectedYColumnRight) {
    columnsToInitialize.push(newValue.selectedYColumnRight.name);
    selectedSeries[newValue.selectedYColumnRight.name] = true;
  }


  await pluginService.getDataManager().initialize(columnsToInitialize);

  // generate title based on selected columns
  let title = `Timestamp vs ${columnsToInitialize.join(' & ')}`;
  pluginService.cardTitle$.next(title);

  const allMeasurements = pluginService.getDataManager().getAllMeasurements();
  updateChartData(allMeasurements);

  pluginService.savePluginState(newValue);

}, { deep: true, immediate: true });


// --- Lifecycle Hooks ---
onMounted(async () => {

  // Set the default plugin state if not provided
  pluginState.value = pluginService.getPluginState() as PluginState || pluginState.value;

  await loadColumns();



  const columnsToInit = []
  if (pluginState.value.selectedYColumnLeft) {
    columnsToInit.push(pluginState.value.selectedYColumnLeft.name);
  }
  if (pluginState.value.selectedYColumnRight) {
    columnsToInit.push(pluginState.value.selectedYColumnRight.name);
  }

  if (columnsToInit.length != 0) {
    await pluginService.getDataManager().initialize(columnsToInit);
    const initialMeasurements = pluginService.getDataManager().getAllMeasurements();
    updateChartData(initialMeasurements);

    let title = `Timestamp vs ${columnsToInit.join(' & ')}`;

    pluginService.cardTitle$.next(title);
  }




  // Subscribe to live data updates
  subscription = pluginService.getDataManager().measurement$.subscribe((measurement: TimeseriesDataPoint) => {
    const vChartsRef = chartRef.value;
    if (!vChartsRef) { return; }



    const isLive = pluginService.getProjectInfo()?.isLive
    if (isLive) {


      const leftColumnName = pluginState.value?.selectedYColumnLeft?.name ?? '';
      const rightColumnName = pluginState.value?.selectedYColumnRight?.name ?? '';
      if (!leftColumnName && !rightColumnName) {
        return; // No columns selected, ignore update
      }

      if (leftColumnName) {
        const newPoint = [measurement.timestamp, measurement.values[leftColumnName]];
        try {
          chartRef.value?.chart.appendData([
            {
              seriesIndex: 0,
              data: [newPoint],
            },
          ]);
        } catch (error) {
          console.error("Error appending data to chart:", error);
        }
      }
      if (rightColumnName) {
        const newPoint = [measurement.timestamp, measurement.values[rightColumnName]];
        chartRef.value?.chart.appendData([
          {
            seriesIndex: 1,
            data: [newPoint],
          },
        ]);
      }


      return; // Ignore updates if not live
    }


    // check if new timestamp is in the range of the first series. if yes put point on the first series
    if (!currentTimestampStatistics || currentTimestampStatistics?.count == 0) {
      return;
    }


    const firstTimestamp = currentTimestampStatistics.min;
    const lastTimestamp = currentTimestampStatistics.max;

    const leftColumnName = pluginState.value?.selectedYColumnLeft?.name ?? '';
    const rightColumnName = pluginState.value?.selectedYColumnRight?.name ?? '';

    const isLeftSelected = selectedSeries[leftColumnName] ?? false;
    const isRightSelected = selectedSeries[rightColumnName] ?? false;



    const seriesIndex = isLeftSelected ? 0 : (isRightSelected ? 1 : -1);
    if (seriesIndex === -1) return; // No series selected


    const xValue = clamp(measurement.timestamp, firstTimestamp, lastTimestamp);

    let yValue = 0;

    if (isLeftSelected || isRightSelected) {
      const columnName = isLeftSelected ? leftColumnName : rightColumnName;
      const expression = isLeftSelected
        ? pluginState.value.yAxisExpressionLeft
        : pluginState.value.yAxisExpressionRight;

      const v = measurement.values[columnName] ?? 0;
      if (typeof v === 'number') {
        yValue = v
      }

      if (expression) {
        yValue = transformMathJsValue(yValue, expression);
      }
    }




    const [x, y] = vChartsRef.convertToPixel({ seriesIndex: seriesIndex }, [xValue, yValue]);

    const zr = vChartsRef.chart.getZr();
    const el = zr.storage.getDisplayList().find((el: any) => el.id == 'highlight-point');

    if (el) {
      el.attr({ position: [x, y], invisible: false });
    }



  });
});

onUnmounted(() => {
  subscription?.unsubscribe();
});

const loadColumns = async () => {
  console.log("Loading columns...");

  var columns = await pluginService.getDataManager().getAvailableColumnNames();
  const numericalColumns = columns.filter(c => c.type == "scalar").map(c => {
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
