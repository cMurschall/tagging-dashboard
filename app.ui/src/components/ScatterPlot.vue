<template>
    <div ref="containerRef" style="width: 100%; height: 100%;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <div @click="showColumns = !showColumns" style="cursor: pointer;">
          <svg v-if="!showColumns" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
            fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
            class="feather feather-menu">
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
            class="feather feather-x">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </div>
      </div>
      <BCollapse v-model="showColumns">
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
              <BFormInput v-model="yAxisExpression" type="text" autocomplete="off" placeholder="Enter Y Axis Expression" />
            </BFormGroup>
          </BCol>
        </BRow>
      </BCollapse>
      <VChart ref="chartRef" :option="chartOption" :style="{ width: '100%', height: '100%' }" />
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, defineProps, defineExpose, onUnmounted, inject, computed, watch } from "vue";
  import VChart from "vue-echarts";
  import { use } from "echarts/core";
  import { ScatterChart } from "echarts/charts";
  import { CanvasRenderer } from "echarts/renderers";
  import { GridComponent } from 'echarts/components';
  import { IDataManager, TimeseriesDataPoint } from "./../managers/iDataManager";
  import { Subscription } from "./../observable";
  import { safeFetch, PlayerApiClient as client } from "./../services/Utilities";
  import { BCol, BCollapse, BFormGroup, BFormSelect, BRow, BFormInput } from "bootstrap-vue-next";
  import { ColumnInfo } from "../../services/restclient";

  import * as math from 'mathjs'
  
  use([ScatterChart, CanvasRenderer, GridComponent]);
  
  // Inject the function from the parent
  const setCardTitle = inject('setCardTitle') as (title: string) => void;
  
  interface ScatterPlotProps {
    width?: number;
    height?: number;
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
        data: [[0,0]],
        symbolSize: 3,
      },
      { // Series to highlight the current data point
        type: 'scatter',
        data: [[0,0]],
        symbolSize: 10,
        itemStyle: {
          color: 'red', // Highlight color
        },
      },
    ],
    // tooltip: {
    //       trigger: 'item',
    //       formatter: (params: any) => {
    //            if (Array.isArray(params.value)) {
    //       // Format the timestamp for better readability in the tooltip
    //               const date = new Date(params.value[0]);
    //               const formattedDate = date.toLocaleString();
    //               return `Timestamp: ${formattedDate}, Y: ${params.value[1]}`;
    //           }
    //           return "No data";
    //       }
    //   },
  });
  
  defineExpose({ chartOption });
  
  const containerRef = ref(null);
  const chartRef = ref<typeof VChart | null>(null);
  
  const showColumns = ref(false);
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
    .filter(m => m.timestamp > 0)
    .map(m => [m.timestamp, transformValue( m.values[selectedYColumn.value!.name], yAxisExpression.value  )]);

    
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
    chartOption.value.series[0].data = sampledData;
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
      // Use the latest measurement to update the chart
      // updateChartData([measurements]);
      console.log("New measurement:", {
        timestamp: measurements.timestamp,
        value: measurements.values[selectedYColumn.value!.name],
      });
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
          if(preSelectedColumn.length > 0){

            selectedYColumn.value = preSelectedColumn[0];
          }
  
  
    }
    if (error) {
      console.error('Error loading columns:', error);
    }
  }
  </script>
  