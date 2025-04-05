<template>
  <div ref="containerRef" style="width: 100%; height: 100%;">

    <!-- <div>{{ pluginState }}</div> -->
    <!-- <div>-----------</div> -->
    <!-- <div>{{ gaugeOption }}</div> -->
    <Transition name="fade" mode="out-in">
      <div v-if="showMenu">
        <BRow class="mb-2">
          <BCol cols="12">
            <h4>Gauge Options</h4>
          </BCol>
        </BRow>
        <BRow class="mb-2">
          <BCol cols="12">
            <div rule=group>
              <label for="column-filter-query">Filter Columns:</label>
              <BFormInput onfocus="this.value=''" id="column-filter-query" v-model="searchQuery" type="text"
                autocomplete="off" placeholder="Search columns..." />
            </div>
          </BCol>
        </BRow>
        <BRow class="mb-2">
          <BCol cols="12">
            <BFormGroup label="Select Columns:">
              <BFormSelect v-model="pluginState.selectedColumn" :options="filteredColumns" select-size="5" />
            </BFormGroup>
          </BCol>
        </BRow>
        <BRow class="mb-2">
          <BCol cols="6">
            <BFormGroup label="Minimum Value:">
              <BFormInput v-model="pluginState.gaugeMin" type="number" />
            </BFormGroup>
          </BCol>
          <BCol cols="6">
            <BFormGroup label="Maximum Value:">
              <BFormInput v-model="pluginState.gaugeMax" type="number" />
            </BFormGroup>
          </BCol>
        </BRow>

        <BRow class="mb-2">
          <BCol cols="6">
            <BFormGroup label="The number of split segments:">
              <BFormInput v-model="pluginState.gaugeCountSplits" type="number" />
            </BFormGroup>
          </BCol>
          <BCol cols="6">
            <BFormGroup label="Color:">
              <BFormInput v-model="pluginState.gaugeColor" type="color" />
            </BFormGroup>
          </BCol>
        </BRow>


        <BRow class="mb-2">
          <BCol cols="6">
            <BFormGroup label="Detail formatter:">
              <BFormInput v-model="pluginState.gaugeFormat" type="text" />
            </BFormGroup>
          </BCol>
          <BCol cols="6">
            <BFormGroup label="Math js converter:">
              <BFormInput v-model="pluginState.gaugeConverter" type="text" />
            </BFormGroup>
          </BCol>
        </BRow>
      </div>
    </Transition>
    <div v-if="!pluginState.selectedColumn">
      <h4>No data column selected. Open options to select.</h4>
    </div>
    <VChart v-else ref="chartRef" :option="gaugeOption" :style="{ width: '100%', height: '100%' }" />

  </div>
</template>


<script setup lang="ts">
import { ref, onMounted, onUnmounted, inject, computed, watch } from "vue";
import VChart from "vue-echarts";
import { use } from "echarts/core";
import { GaugeChart } from "echarts/charts";
import { SVGRenderer } from "echarts/renderers";
import { IDataManager, TimeseriesDataPoint } from "../../managers/iDataManager";
import { Subscription } from "../../observable";
import { safeFetch, PlayerApiClient as client, formatWithTemplate, transformMathJsValue } from "../../services/Utilities";
import { BCol, BFormGroup, BFormSelect, BRow, BFormInput } from "bootstrap-vue-next";
import { ColumnInfo } from "../../../services/restclient";
import gridManager from "../../managers/gridItemManager";

use([GaugeChart, SVGRenderer]);



// Inject the function from the parent
const setCardTitle = inject('setCardTitle') as (title: string) => void;

type PluginState = {
  gaugeMin: number;
  gaugeMax: number;

  gaugeCountSplits: number;
  gaugeColor: string;

  gaugeFormat: string;
  gaugeConverter: string | null;

  selectedColumn: ColumnInfo | null;
}



interface GaugeProps {
  showMenu?: boolean,
  id: string;
  pluginState?: PluginState;
}

interface BFormSelectColumnInfo {
  text: string;
  value: ColumnInfo;
}

// Define component props with default values
const props = withDefaults(defineProps<GaugeProps>(), {
  showMenu: false, // Default value for showMenu

  id: '', // Default value for id

  // Default values for properties within pluginState if pluginState is undefined
  pluginState: () => ({
    gaugeMin: 0,
    gaugeMax: 100,
    gaugeCountSplits: 10,
    gaugeColor: "#007bff",
    gaugeFormat: "{value:F2}",
    gaugeConverter: "value * 1",

    selectedColumn: null,
  }),
});


// Define 
const pluginState = ref<PluginState>(props.pluginState);

// Default gauge options
const gaugeOption = ref({
  series: [
    {
      type: "gauge",
      startAngle: 220,
      endAngle: -40,
      min: pluginState.value.gaugeMin ?? 0,
      max: pluginState.value.gaugeMax ?? 100,
      progress: { show: false },
      axisLine: {
        lineStyle: {
          width: 4,
          color: [[1, pluginState.value.gaugeColor ?? "#007bff"]],
        },
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        show: true,
        formatter: (value: number) => {
          if (Math.abs(value) > 1) {
            return value.toFixed(0);
          } else {
            return value.toFixed(2);
          }
        },
      },
      splitNumber: pluginState.value.gaugeCountSplits ?? 10,
      detail: {
        offsetCenter: [0, '60%'],
        valueAnimation: false,
        formatter: (x: number) => {
          if (pluginState.value.gaugeFormat) {
            return formatWithTemplate(x, pluginState.value.gaugeFormat);
          }
          return x.toString();
        },
        fontSize: 10
      },
      data: [{ value: -1, name: "" }],
    },
  ],
});

defineExpose({ gaugeOption });



const containerRef = ref(null);
const chartRef = ref<typeof VChart | null>(null);

const searchQuery = ref('');
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


let lastSelectedColumn: ColumnInfo | null = null;

watch(pluginState, async (newValue) => {

  // check if the new values are different from the old values
  if (newValue.gaugeMax !== gaugeOption.value.series[0].max) {
    gaugeOption.value.series[0].max = newValue.gaugeMax;
  }

  if (newValue.gaugeMin !== gaugeOption.value.series[0].min) {
    gaugeOption.value.series[0].min = newValue.gaugeMin;
  }
  if (newValue.gaugeCountSplits !== gaugeOption.value.series[0].splitNumber) {
    gaugeOption.value.series[0].splitNumber = newValue.gaugeCountSplits;
  }

  if (newValue.gaugeColor !== gaugeOption.value.series[0].axisLine.lineStyle.color[0][1]) {
    gaugeOption.value.series[0].axisLine.lineStyle.color[0][1] = newValue.gaugeColor;
  }


  const selectedColumnUpdated = newValue.selectedColumn != lastSelectedColumn;

  // check if the selected column is different from the old value
  if (selectedColumnUpdated && newValue.selectedColumn) {
    await dataManager.initialize([newValue.selectedColumn.name]);
    // gaugeOption.value.series[0].data[0].name = newVal.selectedColumn.name;
    setCardTitle(newValue.selectedColumn.name);

    lastSelectedColumn = newValue.selectedColumn;
  }
  // update the gridmanager with the new plugin state
  gridManager.updateItemById(props.id, {
    pluginState: { ...newValue }
  });
}, { deep: true });





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

  // check if we have a selected column
  if (pluginState.value.selectedColumn) {
    await dataManager.initialize([pluginState.value.selectedColumn.name]);
    // gaugeOption.value.series[0].data[0].name = pluginState.value.selectedColumn.name;
    setCardTitle(pluginState.value.selectedColumn.name);
  } else {
    setCardTitle('No column selected');
  }

  subscription = dataManager.measurement$.subscribe((measurements: TimeseriesDataPoint) => {
    console.log('Received measurements:', measurements);
    // check if measurements has our selected column name
    if (!pluginState.value.selectedColumn || !measurements.values[pluginState.value.selectedColumn.name]) {
      return;
    }
    // Use the gauge data.

    let x = measurements.values[pluginState.value.selectedColumn?.name ?? ''];
    if (pluginState.value.gaugeConverter) {
      x = transformMathJsValue(x, pluginState.value.gaugeConverter);
    }
    gaugeOption.value.series[0].data[0].value = x

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

    // const preSelectedColumn = numericColumns.filter(c => c.name == 'car0_velocity_vehicle')
    // if (preSelectedColumn.length > 0) {

    //   pluginState.value.selectedColumn = preSelectedColumn[0];
    // }
  }
  if (error) {
    console.error('Error loading columns:', error);
  }
}


</script>
