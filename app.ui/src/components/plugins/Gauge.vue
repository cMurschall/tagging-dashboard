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
          <BFormGroup label="Select Columns:">
            <BFormSelect v-model="selectedColumn" :options="filteredColumns" select-size="3" />
          </BFormGroup>
        </BCol>
      </BRow>
      <BRow>
        <BCol cols="6">
          <BFormGroup label="Minimum Value:">
            <BFormInput v-model="gaugeOption.series[0].min" type="number" />
          </BFormGroup>
        </BCol>
        <BCol cols="6">
          <BFormGroup label="Maximum Value:">
            <BFormInput v-model="gaugeOption.series[0].max" type="number" />
          </BFormGroup>
        </BCol>
      </BRow>

    </BCollapse>
    <VChart ref="chartRef" :option="gaugeOption" :style="{ width: '100%', height: '100%' }" />
  </div>
</template>


<script setup lang="ts">
import { ref, onMounted, defineProps, defineExpose, onUnmounted, inject, computed, watch } from "vue";
import VChart from "vue-echarts";
import { use } from "echarts/core";
import { GaugeChart } from "echarts/charts";
import { SVGRenderer } from "echarts/renderers";
import { IDataManager, TimeseriesDataPoint } from "../../managers/iDataManager";
import { Subscription } from "../../observable";
import { safeFetch, PlayerApiClient as client } from "../../services/Utilities";
import { BCol, BCollapse, BFormGroup, BFormSelect, BRow, BFormInput } from "bootstrap-vue-next";
import { ColumnInfo } from "../../../services/restclient";

use([GaugeChart, SVGRenderer]);



// Inject the function from the parent
const setCardTitle = inject('setCardTitle') as (title: string) => void;



interface GaugeProps {
  min?: number,
  max?: number,
  label?: string,
  width?: number,
  height?: number,
  color?: string,
}

interface BFormSelectColumnInfo {
  text: string;
  value: ColumnInfo;
}

// Define component props
const props = defineProps<GaugeProps>();

// Default gauge options
const gaugeOption = ref({
  series: [
    {
      type: "gauge",
      startAngle: 220,
      endAngle: -40,
      min: props.min ?? 0,
      max: props.max ?? 100,
      progress: { show: false },
      axisLine: {
        lineStyle: {
          width: 2,
          color: [[1, props.color ?? "#007bff"]],
        },
      },
      detail: {
        // color: "#fff",
        valueAnimation: false,
        formatter: (x: number) => x.toFixed(2),
        fontSize: 10
      },
      data: [{ value: -1, name: props.label ?? "" }],
    },
  ],
});

defineExpose({ gaugeOption });



const containerRef = ref(null);
const chartRef = ref<typeof VChart | null>(null);

const showColumns = ref(false);
const searchQuery = ref('');
const selectedColumn = ref<ColumnInfo | null>(null);
const availableColumns = ref<BFormSelectColumnInfo[]>([]);


let resizeObserver: ResizeObserver | null = null;
let subscription: Subscription | undefined;

const dataManager = inject<IDataManager>('dataManager');
if (!dataManager) {
  throw new Error('dataManager not provided');
}


const filteredColumns = computed(() => {
  return availableColumns.value.filter((c) => c.text.toLowerCase().includes(searchQuery.value.toLowerCase()));
});


watch(selectedColumn, async (newVal) => {
  console.log('Selected column:', newVal);
  if (newVal) {
    await dataManager.initialize([newVal.name]);
    // gaugeOption.value.series[0].data[0].name = newVal.name;
    setCardTitle(newVal.name);
  }
});

onMounted(async () => {

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


  subscription = dataManager.measurement$.subscribe((measurements: TimeseriesDataPoint) => {

    // check if measurements has our selected column name
    if (!selectedColumn.value || !measurements.values[selectedColumn.value.name]) {
      return;
    }
    // Use the gauge data.
    gaugeOption.value.series[0].data[0].value = measurements.values[selectedColumn.value?.name ?? '']

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
  const [error, response] = await safeFetch(() => client.getDataApiV1PlayerColumnsGet());
  if (response) {

    const numericColumns = response.columns.filter((c: any) => c.type.includes('int') || c.type.includes('float'));

    // console.log('Numeric Columns loaded', numericColumns);
    availableColumns.value = numericColumns.map(x => ({ text: x.name, value: x }));

    const preSelectedColumn = numericColumns.filter(c => c.name == 'car0_velocity_vehicle')
    if (preSelectedColumn.length > 0) {

      selectedColumn.value = preSelectedColumn[0];
    }
  }
  if (error) {
    console.error('Error loading columns:', error);
  }
}


</script>
