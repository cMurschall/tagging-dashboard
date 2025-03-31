<template>
  <div ref="containerRef" style="width: 100%; height: 100%;">
    <Transition name="fade" mode="out-in">
      <div v-if="showMenu">
        <BRow>
          <BCol cols="12">
            <div rule=group>
              <label for="column-filter-query">"Search Columns:"</label>
              <BFormInput onfocus="this.value=''" id="column-filter-query" v-model="searchQuery" type="text"
                autocomplete="off" placeholder="Search columns..." />
            </div>
          </BCol>
        </BRow>
        <BRow>
          <BCol cols="12">
            <BFormGroup label="Select Y Axis Column:">
              <BFormSelect v-model="selectedYColumn" :options="filteredColumns" select-size="3" />
            </BFormGroup>
          </BCol>
        </BRow>
        <BRow>
          <BCol cols="12">
            <BFormGroup label="Y Axis Expression:">
              <BFormInput v-model="yAxisExpression" type="text" autocomplete="off"
                placeholder="Enter Y Axis Expression" />
            </BFormGroup>
          </BCol>
        </BRow>
      </div>
      <VChart v-else ref="chartRef" :option="chartOption" :style="{ width: '100%', height: '100%' }" @zr:click="handleVChartClick"/>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import VChart from "vue-echarts";
import { ref, onMounted, onUnmounted, inject, computed, watch } from "vue";
import { ECElementEvent, ElementEvent, use } from "echarts/core";
import { ScatterChart, LineChart } from "echarts/charts";
import { CanvasRenderer } from "echarts/renderers";
import { GridComponent , TooltipComponent } from 'echarts/components';
import { IDataManager, TimeseriesDataPoint } from "../../managers/iDataManager";
import { Subscription } from "../../observable";
import { safeFetch, PlayerApiClient as client } from "../../services/Utilities";
import { BCol, BFormGroup, BFormSelect, BRow, BFormInput } from "bootstrap-vue-next";
import { ColumnInfo } from "../../../services/restclient";

import * as math from 'mathjs'

import { useVideoControl } from './../../composables/useVideoControl';



use([ScatterChart, CanvasRenderer, GridComponent, LineChart, TooltipComponent ]);

// Inject the function from the parent
const setCardTitle = inject('setCardTitle') as (title: string) => void;
const { seekTo } = useVideoControl()


interface ScatterPlotProps {
  width?: number;
  height?: number;
  showMenu?: boolean,
}

interface BFormSelectColumnInfo {
  text: string;
  value: ColumnInfo;
}

// Define component props
const props = defineProps<ScatterPlotProps>();

// Default chart options
const chartOption = ref({
  grid: {
    left: '10%',
    right: '10%',
    bottom: '15%',
    top: '10%',
  },
  xAxis: {
    scale: true
  },
  yAxis: {
    scale: true
  },
  series: [
    {
      type: 'scatter',
      data: [[0, 0]],
      symbolSize: 3,
    },
    { // Series to highlight the current data point
      type: 'scatter',
      data: [[0, 0]],
      symbolSize: 10,
      itemStyle: {
        color: 'red', // Highlight color
      },
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
        formatter: (params: any) => {
            const xValue = params[0].value[0];
            const yValue = params[0].value[1];
            return `Time: ${xValue.toFixed(1)} s<br/>${selectedYColumn.value?.name}: ${yValue}`;
        }
    }

});


 const handleVChartClick = (params: ElementEvent) => {
  const chart = chartRef.value;
  if (!chart) return;

  const [x, y] = chart.convertFromPixel({ seriesIndex: 0 }, [params.offsetX, params.offsetY]);
  console.log(`Clicked at axis coordinates: X = ${x}, Y = ${y}`);

  seekTo(x); // Call the seekTo function with the x value
  
 }

defineExpose({ chartOption });

const containerRef = ref(null);
const chartRef = ref<typeof VChart | null>(null);

const searchQuery = ref('');
const selectedYColumn = ref<ColumnInfo | null>(null);
const availableColumns = ref<BFormSelectColumnInfo[]>([]);

const yAxisExpression = ref<string>('y'); // Default expression

let resizeObserver: ResizeObserver | null = null;
let subscription: Subscription | undefined;

const dataManager = inject<IDataManager>('dataManager');
if (!dataManager) {
  throw new Error('dataManager not provided');
}

const filteredColumns = computed(() => {
  return availableColumns.value.filter((c) => c.text.toLowerCase().includes(searchQuery.value.toLowerCase()));
});

const updateChartData = (measurements: TimeseriesDataPoint[]) => {
  if (!selectedYColumn.value) {
    return;
  }

  const data = measurements
    .filter((m) => m.timestamp > 0)
    .map((m) => [m.timestamp, m.values[selectedYColumn.value!.name]]);

  // Data sampling
  const maxDataPoints = 2000; // Maximum number of points to display
  let sampledData = data;
  if (data.length > maxDataPoints) {
    const sampleInterval = Math.floor(data.length / maxDataPoints);
    sampledData = [];
    for (let i = 0; i < data.length; i += sampleInterval) {
      sampledData.push(data[i]);
    }
  }
  const transformed = sampledData.map((d) => [
    d[0],
    transformValue(d[1], yAxisExpression.value),
  ]);
  chartOption.value.series[0].data = transformed;
  chartOption.value.series[1].data = [];
};



const transformValue = (value: number, expression: string) => {
  try {
    const scope = { y: value };
    return math.evaluate(expression, scope);
  } catch (error) {
    console.error('Error evaluating expression:', error);
    return value; // Return original value on error
  }
};

watch([selectedYColumn, yAxisExpression], async ([newYColumn]) => {
  if (newYColumn) {
    await dataManager.initialize([newYColumn.name]);
    setCardTitle(`Timestamp vs ${newYColumn.name}`);
    const allMeasurements = dataManager.getAllMeasurements();
    updateChartData(allMeasurements);
  }
});

onMounted(async () => {
  await loadColumns();

  // Listen to resize events
  if (containerRef.value) {
    resizeObserver = new ResizeObserver(() => {
      console.log("Resizing chart...");
      if (chartRef.value) {
        chartRef.value.resize();
      }
    });
    resizeObserver.observe(containerRef.value);
  }

  subscription = dataManager.measurement$.subscribe((measurements: TimeseriesDataPoint) => {
    chartOption.value.series[1].data = [[
      measurements.timestamp,
      transformValue(measurements.values[selectedYColumn.value!.name], yAxisExpression.value)
    ]];

  });
});

onUnmounted(() => {
  if (resizeObserver && containerRef.value) {
    resizeObserver.unobserve(containerRef.value);
    resizeObserver.disconnect();
  }
  subscription?.unsubscribe();
});

const loadColumns = async () => {
  const [error, response] = await safeFetch(() => client.getDataApiV1PlayerColumnsGet());
  if (response) {
    const numericColumns = response.columns.filter((c: any) => c.type.includes('int') || c.type.includes('float'));
    availableColumns.value = numericColumns.map(x => ({ text: x.name, value: x }));

    const preSelectedColumn = numericColumns.filter(c => c.name == 'car0_velocity_vehicle');
    if (preSelectedColumn.length > 0) {

      selectedYColumn.value = preSelectedColumn[0];
    }


  }
  if (error) {
    console.error('Error loading columns:', error);
  }
}



</script>