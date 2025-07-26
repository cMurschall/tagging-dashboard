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
                    </BCol>
                </BRow>




                <BRow class="mb-3">
                    <BCol cols="12">
                        <BFormGroup label="Select Secondary Y Axis Column (Optional):">
                            <FilterableSelect v-model="pluginState.selectedYColumnRight" :options="availableColumns"
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

            <Chart v-else ref="chartRef" :option="chartOption" :style="{ width: '100%', height: '100%' }"
                @zr:click="handleVChartClick" :autoresize="{ throttle: 100 }" />
        </Transition>
    </div>
</template>

<script setup lang="ts">
import Chart from "vue-echarts";
import { ref, onMounted, onUnmounted, inject, watch } from "vue";
import { IDENTITY_EXPRESSION, transformMathJsValue, useObservable } from "../../core/utilities/utilities";
import { BCol, BFormGroup, BRow, BFormInput } from "bootstrap-vue-next";
import { ColumnInfo } from "../../../services/restclient";
import FilterableSelect from "./../FilterableSelect.vue";
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
import { TimeseriesDataPoint } from "@/types/data";
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
    retentionMinutes: number;

}

const showMenu = useObservable(pluginService.showMenu$);

const pluginState = ref<PluginState>({
    selectedYColumnLeft: null,
    selectedYColumnRight: null,
    yAxisExpressionLeft: IDENTITY_EXPRESSION,
    yAxisExpressionRight: IDENTITY_EXPRESSION,
    retentionMinutes: 4, // Default retention time in minutes
});

// --- Reactive State ---
const containerRef = ref<HTMLDivElement | null>(null);
const chartRef = ref<typeof Chart | null>(null);

const availableColumns = ref<ColumnInfo[]>([]);


let subscription: Subscription = EmptySubscription;


// --- Computed Properties ---

const leftSeriesData = ref<number[][]>([]);
const rightSeriesData = ref<number[][]>([]);


// --- ECharts Option ---

const chartOption = ref<EChartsOption>({
    legend: {
        orient: 'vertical',
        right: 10,
        show: true,
    },
    xAxis: [
        {
            scale: true,
            type: 'value',
            position: 'bottom',
        }
    ],
    yAxis: [
        {
            type: 'value',
            scale: true,
            position: 'left'
        },
        {
            type: 'value',
            scale: true,
            position: 'right' // Align the second y-axis to the right
        }
    ],
    series: [
        {
            id: 'SeriesA',
            name: 'A',
            type: 'scatter',
            data: leftSeriesData.value,
            symbolSize: 3,
            itemStyle: {
                opacity: 0.8
            },
            large: true,
            yAxisIndex: 0,
            xAxisIndex: 0,
        },
        {
            id: 'SeriesB',
            name: 'B',
            type: 'scatter',
            data: rightSeriesData.value,
            symbolSize: 3,
            itemStyle: {
                opacity: 0.8
            },
            large: true,
            yAxisIndex: 1
        },
    ],
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
        // noting to do
    }
};

let selectedSeries: Record<string, boolean> = {};
const handleVChartSelectChanged = (params: any) => {

    selectedSeries = params.selected;
    console.log("SelectionChanged:", selectedSeries);
};


// --- Watchers ---
watch(pluginState, async (newValue) => {

    const hasLeftColumn = !!newValue.selectedYColumnLeft;
    const hasRightColumn = !!newValue.selectedYColumnRight;

    const primaryColName = newValue.selectedYColumnLeft?.name;
    const secondaryColName = newValue.selectedYColumnRight?.name;

    const columnsToInitialize = [];
    if (newValue.selectedYColumnLeft && primaryColName) {
        columnsToInitialize.push(primaryColName);
        selectedSeries[primaryColName] = true;
    }
    if (newValue.selectedYColumnRight && secondaryColName) {
        columnsToInitialize.push(secondaryColName);
        selectedSeries[secondaryColName] = true;
    }



    if (!hasLeftColumn) {
        leftSeriesData.value = [];
    }
    if (!hasRightColumn) {
        rightSeriesData.value = [];
    }


    const manager = pluginService.getDataManager();
    await manager.initialize(columnsToInitialize);


    // generate title based on selected columns
    let title = `Timestamp vs ${columnsToInitialize.join(' & ')} (live)`;
    pluginService.cardTitle$.next(title);

    pluginService.savePluginState(newValue);

    // Update axis names based on selections
    getLeftSeries().name = primaryColName ? primaryColName : '';
    getRightSeries().name = secondaryColName ? secondaryColName : '';

}, { deep: true, immediate: true });

let flushTimer: ReturnType<typeof setInterval> | null = null;

// --- Lifecycle Hooks ---
onMounted(async () => {

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

        let title = `Timestamp vs ${columnsToInit.join(' & ')} (live) `;

        pluginService.cardTitle$.next(title);
    }

    let lastTimestamp = 0;
    let leftBuffer: number[][] = [];
    let rightBuffer: number[][] = [];
    const flushIntervalMs = 250;


    // Set up interval to filter data and update chart
    flushTimer = setInterval(() => {
        const chart = chartRef.value?.chart; // Get the underlying chart instance if needed
        if (!chart && !chartRef.value?.updateOptions) { // Check if chart or update method exists
            console.warn("Chart instance or updateOptions not available for update.");
            return;
        }

        const leftColumnName = pluginState.value?.selectedYColumnLeft?.name ?? '';
        const rightColumnName = pluginState.value?.selectedYColumnRight?.name ?? '';
        if (!leftColumnName && !rightColumnName) return;


        const retentionSeconds = 60 * (pluginState.value.retentionMinutes ?? 4);
        const xMin = lastTimestamp - retentionSeconds; // Earliest simulation time to keep

        leftBuffer = leftBuffer.filter(([ts]) => ts >= xMin);
        getLeftSeries().data = leftBuffer;


        rightBuffer = rightBuffer.filter(([ts]) => ts >= xMin);
        getRightSeries().data = rightBuffer;


    }, flushIntervalMs);


    // Subscribe to live data updates
    subscription = pluginService.getDataManager().measurement$.subscribe(
        (measurement: TimeseriesDataPoint) => {
            const leftColumnName = pluginState.value?.selectedYColumnLeft?.name ?? '';
            const rightColumnName = pluginState.value?.selectedYColumnRight?.name ?? '';
            if (!leftColumnName && !rightColumnName) return;

            lastTimestamp = measurement.timestamp;


            // Buffer left value
            if (leftColumnName) {
                let yLeft = measurement.values[leftColumnName];
                if (typeof yLeft === 'number' && !isNaN(yLeft)) {
                    if (pluginState.value.yAxisExpressionLeft) {
                        yLeft = transformMathJsValue(yLeft, pluginState.value.yAxisExpressionLeft);
                    }
                    // leftBuffer.push([measurement.timestamp, yLeft]);
                    // const filtered = leftBuffer.filter(([ts]) => ts >= xMin);
                    // leftBuffer = filtered;
                    leftBuffer.push([measurement.timestamp, yLeft]);

                }
            }

            // Buffer right value
            if (rightColumnName) {
                let yRight = measurement.values[rightColumnName];

                if (typeof yRight === 'number' && !isNaN(yRight)) {
                    if (pluginState.value.yAxisExpressionRight) {
                        yRight = transformMathJsValue(yRight, pluginState.value.yAxisExpressionRight);
                    }

                    // const filtered = rightBuffer.filter(([ts]) => ts >= xMin);
                    // rightBuffer = filtered;
                    rightBuffer.push([measurement.timestamp, yRight]);
                }
            }
        }
    );
});

onUnmounted(() => {
    subscription?.unsubscribe();
    if (flushTimer) {
        clearInterval(flushTimer);
        flushTimer = null;
    }
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