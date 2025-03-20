<template>
  <div ref="containerRef" style="width: 100%; height: 100%;">
    <VChart ref="chartRef" :option="gaugeOption" :style="{ width: '100%', height: '100%' }" />
  </div>
</template>


<script setup lang="ts">
import { ref, onMounted, defineProps, defineExpose, onUnmounted, toRaw, inject } from "vue";
import VChart from "vue-echarts";
import { use } from "echarts/core";
import { GaugeChart } from "echarts/charts";
import { CanvasRenderer } from "echarts/renderers";
import { IDataManager } from "../managers/iDataManager";
import { Subscription } from "../observable";

use([GaugeChart, CanvasRenderer]);


interface GaugeProps {
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


// Create a reference for the chart instance
const containerRef = ref(null);
const chartRef = ref(null);
let resizeObserver: ResizeObserver | null = null;



let subscription: Subscription | undefined;

const dataManager = inject<IDataManager>('dataManager');
if (!dataManager) {
  throw new Error('dataManager not provided');
}

onMounted(() => {
  // Listen to resize events
  // Create a ResizeObserver to watch the container element
  if (containerRef.value) {
    resizeObserver = new ResizeObserver(() => {
      if (chartRef.value) {
        chartRef.value.resize();
      }
    });
    resizeObserver.observe(containerRef.value);
  }


  subscription = dataManager.measurement$.subscribe((measurement: number) => {
    console.log("New gauge measurement:", measurement);
    gaugeOption.value.series[0].data[0].value = measurement;
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

defineExpose({ gaugeOption });
</script>
