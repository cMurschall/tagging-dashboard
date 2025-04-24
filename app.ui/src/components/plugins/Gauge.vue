<template>
  <div ref="containerRef" style="width: 100%; height: 100%;">
    <Transition name="fade" mode="out-in">
      <div v-if="showMenu">
        <BRow class="mb-2">
          <BCol cols="12">
            <h4>Gauge Options</h4>
          </BCol>
        </BRow>
        <BRow class="mb-2">
          <BCol cols="12">
            <FilterableSelect v-model="pluginState.selectedColumn" :options="availableColumns"
              :getLabel="(item: ColumnInfo) => item.name" placeholder="Select Columns:" />
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
              <BFormInput v-model="pluginState.gaugeFormat" type="text" style="font-family: monospace ;" />
            </BFormGroup>
          </BCol>
          <BCol cols="6">
            <BFormGroup label="Math js converter:">
              <BFormInput v-model="pluginState.gaugeConverter" type="text" style="font-family: monospace ;" />
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
import { ref, onMounted, onUnmounted, inject, watch } from "vue";
import VChart from "vue-echarts";
import { use } from "echarts/core";
import { GaugeChart } from "echarts/charts";
import { SVGRenderer } from "echarts/renderers";
import { TimeseriesDataPoint } from "../../managers/dataManager";
import { EmptySubscription, Subscription } from "../../observable";
import { safeFetch, PlayerApiClient as client, formatWithTemplate, transformMathJsValue, IDENTITY_EXPRESSION, useObservable } from "../../services/utilities";
import { BCol, BFormGroup, BRow, BFormInput } from "bootstrap-vue-next";
import { ColumnInfo } from "../../../services/restclient";
import { SetCardTitleFn } from "../../plugins/AppPlugins";
import { PluginServices } from "../../managers/pluginManager";
import FilterableSelect from "./../FilterableSelect.vue";

use([GaugeChart, SVGRenderer]);



// Inject the function from the parent
const setCardTitle = inject<SetCardTitleFn>('setCardTitle') ?? (() => { });

const pluginService = inject<PluginServices>('pluginService');
if (!pluginService) {
  throw new Error('Plugin service not found!');
}


type PluginState = {
  gaugeMin: number;
  gaugeMax: number;

  gaugeCountSplits: number;
  gaugeColor: string;

  gaugeFormat: string;
  gaugeConverter: string | null;

  selectedColumn: ColumnInfo | null;
}




const showMenu =useObservable(pluginService.showMenu$);

const pluginState = ref<PluginState>({
  gaugeMin: 0,
  gaugeMax: 100,
  gaugeCountSplits: 10,
  gaugeColor: "#007bff",
  gaugeFormat: "{value:F2}",
  gaugeConverter: `${IDENTITY_EXPRESSION} * 1`,

  selectedColumn: null,
});

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
      data: [{ value: -1 }],
    },
  ],
});

defineExpose({ gaugeOption });



const containerRef = ref(null);
const chartRef = ref<typeof VChart | null>(null);

const availableColumns = ref<ColumnInfo[]>([]);


let resizeObserver: ResizeObserver | null = null;
let subscription: Subscription = EmptySubscription;



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
    await pluginService.getDataManager().initialize([newValue.selectedColumn.name]);
    // gaugeOption.value.series[0].data[0].name = newVal.selectedColumn.name;
    setCardTitle(newValue.selectedColumn.name);

    lastSelectedColumn = newValue.selectedColumn;
  }


  // update =the new plugin state
  pluginService.savePluginState(newValue);

}, { deep: true });





onMounted(async () => {

  pluginState.value = pluginService.getPluginState() as PluginState|| pluginState.value;

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
    console.log('Initializing selected column:', pluginState.value.selectedColumn.name);
    await pluginService.getDataManager().initialize([pluginState.value.selectedColumn.name]);
    setCardTitle(pluginState.value.selectedColumn.name);
  } else {
    setCardTitle('No column selected');
  }

  subscription = pluginService.getDataManager().measurement$.subscribe((measurements: TimeseriesDataPoint) => {

    let x = measurements.values[pluginState.value.selectedColumn?.name ?? ''];

    // check if the value is a number and not an array
    if (typeof x !== 'number') {
      console.warn('Value is not a number:', x);
      return;
    }

    if (pluginState.value.gaugeConverter) {
      x = transformMathJsValue(x, pluginState.value.gaugeConverter);
    }


    chartRef.value?.setOption({
      series: [
        {
          data: [{ value: x }],
        },
      ]
    })



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

    availableColumns.value = numericColumns; //.map(x => ({ text: x.name, value: x }));

  }
  if (error) {
    console.error('Error loading columns:', error);
  }
}


</script>
