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


                <BRow class="mb-3">
                    <BCol cols="12">
                        <BFormGroup label="Data Retention (minutes):">
                            <BFormInput v-model="pluginState.retentionMinutes" type="number" min="0.1" step="0.5"
                                placeholder="4" />
                        </BFormGroup>
                    </BCol>
                </BRow>
            </div>

            <Chart v-else ref="componentChartRef" :option="componentChartOption"
                :style="{ width: '100%', height: '100%' }" :autoresize="{ throttle: 100 }" />
        </Transition>
    </div>
</template>

<script setup lang="ts">
import Chart from "vue-echarts";
import { ref, onMounted, onUnmounted, inject, watch } from "vue";
import { EmptySubscription, Subscription } from "../../observable";
import { safeFetch, PlayerApiClient as client, isNullOrUndefined, useObservable } from "../../core/utilities/utilities";
import { BCol, BFormGroup, BRow, BFormInput } from "bootstrap-vue-next";
import { ColumnInfo } from "../../../services/restclient";
import FilterableSelect from "./../FilterableSelect.vue";
import { use } from 'echarts/core';
import { ScatterChart } from 'echarts/charts';
import {
    LegendComponent,
    GridComponent,
    DataZoomComponent,
    TitleComponent,
    GraphicComponent,
    TooltipComponent
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import type { ComposeOption, ElementEvent } from 'echarts/core';
import type { ScatterSeriesOption } from 'echarts/charts';
import type {
    LegendComponentOption,
    GridComponentOption,
    DataZoomComponentOption,
    GraphicComponentOption,
    TooltipComponentOption,
} from 'echarts/components';
import { PluginServices } from "../../managers/pluginManager";
import { XAXisOption, YAXisOption } from "echarts/types/dist/shared";

use([
    TitleComponent,
    LegendComponent,
    GridComponent,
    DataZoomComponent,
    GraphicComponent,
    TooltipComponent,
    ScatterChart,
    CanvasRenderer,
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

const showMenu = useObservable(pluginService.showMenu$);

type PluginState = {
    selectedColumn: ColumnInfo | null;
    retentionMinutes: number;

}

const pluginState = ref<PluginState>({
    selectedColumn: null,
    retentionMinutes: 4
});

const containerRef = ref<HTMLDivElement | null>(null);
const componentChartRef = ref<typeof Chart | null>(null);
const availableColumns = ref<ColumnInfo[]>([]);
let subscription: Subscription = EmptySubscription;


interface DataPoint {
    timestamp: number;
    value: number[];
}

interface LiveData {
    key: string;
    dimension: number;
    data: DataPoint[];
}


const currentTable = ref<LiveData | null>(null);
let flushTimer: ReturnType<typeof setInterval> | null = null;
let lastTimestamp = 0;

const flushIntervalMs = 250; // How often to flush buffered points to chart
const retentionMinutes = 4;  // How long to keep points visible

const componentChartOption = ref<EChartsOption>({
    xAxis: [],
    yAxis: [],
    series: [],
    grid: [],
    // dataZoom: [],
    // graphic: []
});

const buildMultiGridVectorChart = (table: LiveData): any => {


    const numComponents = table.dimension;



    const gridHeight = 100 / numComponents;


    const gridOptions: GridComponentOption[] = []
    const xAxis: XAXisOption[] = []
    const yAxis: YAXisOption[] = []
    const series: ScatterSeriesOption[] = []

    for (let i = 0; i < numComponents; i++) {

        gridOptions.push({
            top: `${i * gridHeight + 5}%`,
            height: `${gridHeight - 10}%`,
            containLabel: true,
        });

        xAxis.push({
            type: 'value',
            scale: true,
            gridIndex: i,
            axisLabel: { show: i === numComponents - 1 },
            name: i === numComponents - 1 ? 'Timestamp' : '',
            nameLocation: 'middle',
            nameGap: 30,
        });

        yAxis.push({
            type: 'value',
            scale: true,
            gridIndex: i,
        });

        series.push({
            id: `Series${i}`,
            name: `Component ${i}`,
            type: 'scatter',
            xAxisIndex: i,
            yAxisIndex: i,
            data: [],
            symbolSize: 3,
            itemStyle: { opacity: 0.8 },
            large: true,
        });
    }

    componentChartOption.value = {
        grid: gridOptions,
        xAxis: xAxis,
        yAxis: yAxis,
        series: series,
        animation: false
    };
};

const updateMultiGridVectorChart = (table: LiveData): any => {


    const numComponents = table.dimension;



    const series: ScatterSeriesOption[] = []
    for (let i = 0; i < numComponents; i++) {

        const componentData = new Float64Array(table.data.length * 2);
        for (let j = 0; j < table.data.length; j++) {
            componentData[j * 2] = table.data[j].timestamp; // x
            componentData[j * 2 + 1] = table.data[j].value[i];    // y
        }


        series.push({
            id: `Series${i}`,
            name: `Component ${i}`,
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
            zlevel: 0,
            z: 2      // Standard z for series
        });
    }

    componentChartOption.value = {
        ...componentChartOption.value,
        series: series,
    };
}



watch(pluginState, async (newState) => {
    if (isNullOrUndefined(newState.selectedColumn?.name)) { return; }

    await pluginService.getDataManager().initialize([newState.selectedColumn.name]);
    pluginService.cardTitle$.next(`Live view: ${newState.selectedColumn.name}`);
    pluginService.savePluginState(newState);

    // Reset chart
    currentTable.value = null;



}, { deep: true, immediate: true });

onMounted(async () => {
    pluginState.value = pluginService.getPluginState() as PluginState || pluginState.value;
    await loadColumns();

    // Set up regular flush timer
    flushTimer = setInterval(() => {
        if (!currentTable.value) { return; }

        const retentionSeconds = 60 * (pluginState.value?.retentionMinutes ?? retentionMinutes);
        const xMin = lastTimestamp - retentionSeconds;

        // find index of last xMin in currentTable.data
        const index = currentTable.value.data.findIndex((point) => point.timestamp >= xMin);
        if (index !== -1) {
            currentTable.value.data = currentTable.value.data.slice(index);
        }

        // Update chart
        updateMultiGridVectorChart(currentTable.value);

    }, flushIntervalMs);

    // Subscribe to new measurements
    subscription = pluginService.getDataManager().measurement$.subscribe((measurement) => {
        // handleNewMeasurement(measurement);
        const chart = componentChartRef.value;
        if (!chart) return;

        const key = pluginState.value.selectedColumn?.name
        if (!key) { return; }

        const vector = measurement.values[key];
        if (!vector || !Array.isArray(vector)) {
            console.warn("No vector data available");
            return;
        }

        if (currentTable.value === null) {
            currentTable.value = {
                key: key,
                dimension: vector.length,
                data: [],
            }

            buildMultiGridVectorChart(currentTable.value);

        }
        lastTimestamp = measurement.timestamp;

        currentTable.value.data.push({
            timestamp: measurement.timestamp,
            value: vector,
        });
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
/* your original styles */
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}

.b-form-group {
    margin-bottom: 1rem;
}

.b-form-select {
    max-height: 150px;
}

.p-3 {
    padding: 1rem;
}

.v-chart {
    width: 100%;
    height: 100%;
    min-height: 300px;
}
</style>
