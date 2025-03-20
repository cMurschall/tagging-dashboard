<template>
    <VChart :option="gaugeOption" :style="{ width: `${width || 200}px`, height: `${height || 200}px` }" />
  </template>
  

<script setup lang="ts">
import { ref, watch, onMounted, defineProps, defineExpose, onUnmounted } from "vue";
import VChart from "vue-echarts";
import { use } from "echarts/core";
import { GaugeChart } from "echarts/charts";
import { CanvasRenderer } from "echarts/renderers";
import { IChartDataManager } from "../managers/IChartDataManager";
import { Subscription } from "../observable";

use([GaugeChart, CanvasRenderer]);


interface GaugeProps {
  dataManager: IChartDataManager,
  min?: number,
  max?: number,
  label?: string,
  width?: number,
  height?: number,
  color?: string,
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
      progress: { show: true },
      axisLine: {
        lineStyle: {
          width: 10,
          color: [[1, props.color ?? "#007bff"]],
        },
      },
      detail: { valueAnimation: true, formatter: "{value}" },
      data: [{ value: 0, name: props.label ?? "Gauge" }],
    },
  ],
});


let subscription: Subscription | undefined;

onMounted(() => {
  subscription = props.dataManager.measurement$.subscribe((measurement: number) => {
    gaugeOption.value.series[0].data[0].value = measurement;
  });
});

onUnmounted(() => {
  subscription?.unsubscribe();
});

defineExpose({ gaugeOption });
</script>

