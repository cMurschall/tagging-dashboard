<template>
    <div ref="containerRef" style="width: 100%; height: 100%;">
        <Transition name="fade" mode="out-in">
            <div v-if="showMenu" class="p-3">
                <BRow class="mb-3">
                    <BCol cols="12">
                        <div role="group">
                            <label for="column-filter-query">Search Columns:</label>
                            <BFormInput id="column-filter-query" v-model="searchQuery" type="text" autocomplete="off"
                                placeholder="Filter available columns..." />
                        </div>
                    </BCol>
                </BRow>

                <BRow class="mb-3">
                    <BCol cols="12">
                        <BFormGroup label="Select Primary Y Axis Column (Required):">
                            <BFormSelect v-model="pluginState.selectedYColumnLeft" :options="filteredColumns"
                                select-size="3" required />
                        </BFormGroup>
                    </BCol>
                </BRow>




                <BRow class="mb-3">
                    <BCol cols="12">
                        <BFormGroup label="Select Secondary Y Axis Column (Optional):">
                            <BFormSelect v-model="pluginState.selectedYColumnRight" :options="filteredColumns"
                                select-size="3" />
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
import { ref, onMounted, onUnmounted, inject, computed, watch, toRaw } from "vue";
import { TimeseriesDataPoint } from "../../managers/dataManager";
import { EmptySubscription, Subscription } from "../../observable";
import { safeFetch, PlayerApiClient as client, IDENTITY_EXPRESSION, transformMathJsValue } from "../../services/utilities";
import { BCol, BFormGroup, BFormSelect, BRow, BFormInput } from "bootstrap-vue-next";
import { ColumnInfo } from "../../../services/restclient";



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
import { SetCardTitleFn } from "../../plugins/AppPlugins";
import { PluginServices } from "../../managers/pluginManager";

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


const setCardTitle = inject<SetCardTitleFn>('setCardTitle') ?? (() => { });

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


// --- Component Props ---
interface ScatterPlotProps {
    showMenu: boolean;

    id: string;
    pluginState?: PluginState;

}
const props = withDefaults(defineProps<ScatterPlotProps>(), {
    showMenu: false, // Default value for showMenu

    id: '', // Default value for id
    pluginState: () => ({
        selectedYColumnLeft: null,
        selectedYColumnRight: null,
        yAxisExpressionLeft: '',
        yAxisExpressionRight: '',
        retentionMinutes: 4, // Default retention time in minutes
    }),
});

const pluginState = ref<PluginState>(structuredClone(props.pluginState));

// --- Reactive State ---
const containerRef = ref<HTMLDivElement | null>(null);
const chartRef = ref<typeof Chart | null>(null);
const searchQuery = ref('');
const availableColumns = ref<BFormSelectColumnInfo[]>([]);

const defaultExpressionHint = `Enter expression (use '${IDENTITY_EXPRESSION}')`;



let subscription: Subscription = EmptySubscription;


interface BFormSelectColumnInfo {
    text: string;
    value: ColumnInfo | null;
    disabled?: boolean;
}

// --- Computed Properties ---


const filteredColumns = computed(() => {
    const noneOption: BFormSelectColumnInfo = { text: '(None - Single Axis)', value: null };
    return [
        noneOption,
        ...availableColumns.value
            .filter(c => c.text.toLowerCase().includes(searchQuery.value.toLowerCase()))
    ];
});


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
            data: [],
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
            data: [],
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
        getLeftSeries().data = [];
    }
    if (!hasRightColumn) {
        getLeftSeries().data = [];
    }


    const manager = pluginService.getDataManager();
    await manager.initialize(columnsToInitialize);


    // generate title based on selected columns
    let title = `Timestamp vs ${columnsToInitialize.join(' & ')} (live)`;
    setCardTitle(title);

    pluginService.savePluginState(props.id, toRaw(newValue));

    // Update axis names based on selections
    getLeftSeries().name = primaryColName ? primaryColName : '';
    getRightSeries().name = secondaryColName ? secondaryColName : '';

}, { deep: true, immediate: true });

let flushTimer: ReturnType<typeof setInterval> | null = null;

// --- Lifecycle Hooks ---
onMounted(async () => {
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

        setCardTitle(title);
    }

    const leftBuffer: number[][] = [];
    const rightBuffer: number[][] = [];
    const flushIntervalMs = 250;
    let flushTimer: ReturnType<typeof setInterval> | null = null;

    flushTimer = setInterval(() => {
        const chart = chartRef.value?.chart;
        if (!chart) return;

        const payload: { seriesIndex: number; data: number[][] }[] = [];

        function prepare(buffer: number[][], seriesIndex: number) {
            const valid = buffer.filter(([x, y]) =>
                typeof x === 'number' && typeof y === 'number' && !isNaN(x) && !isNaN(y)
            );

            if (valid.length === 1) {
                valid.push([...valid[0]]);
            }

            if (valid.length >= 2) {
                payload.push({ seriesIndex, data: valid });
            }

            buffer.length = 0;
        }

        prepare(leftBuffer, 0);
        prepare(rightBuffer, 1);

        try {
            for (const p of payload) {
                chart.appendData(p);
            }
            chartRef.value?.resize();
        } catch (err) {
            console.error("appendData failed:", err);
        }

        const nowSec = Date.now() / 1000;
        const xMin = nowSec - (60 * pluginState.value.retentionMinutes); // 240 seconds ago);

    }, flushIntervalMs);


    // Subscribe to live data updates
    // Subscribe to live data updates
    subscription = pluginService.getDataManager().measurement$.subscribe(
        (measurement: TimeseriesDataPoint) => {
            const leftColumnName = pluginState.value?.selectedYColumnLeft?.name ?? '';
            const rightColumnName = pluginState.value?.selectedYColumnRight?.name ?? '';
            if (!leftColumnName && !rightColumnName) return;

            // Buffer left value
            if (leftColumnName) {
                let yLeft = measurement.values[leftColumnName];
                if (typeof yLeft === 'number' && !isNaN(yLeft)) {
                    if (pluginState.value.yAxisExpressionLeft) {
                        yLeft = transformMathJsValue(yLeft, pluginState.value.yAxisExpressionLeft);
                    }
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
                    rightBuffer.push([measurement.timestamp, yRight]);
                }
            }
        }
    );
});

onUnmounted(() => {
    subscription?.unsubscribe();
    subscription = EmptySubscription;
    if (flushTimer) {
        clearInterval(flushTimer);
        flushTimer = null;
    }
});

const loadColumns = async () => {
    console.log("Loading columns...");
    const [error, response] = await safeFetch(() => client.getDataApiV1PlayerColumnsGet());
    if (response && response.columns) {
        const numericColumns = response.columns.filter((c: any) =>
            c.type.includes('int') || c.type.includes('float') || c.type.includes('double')
        );
        availableColumns.value = numericColumns.map((x: ColumnInfo) => ({ text: x.name, value: x }));
        console.log(`Loaded ${availableColumns.value.length} numeric columns.`);

    } else if (error) {
        console.error('Error loading columns:', error);
    } else {
        console.warn('No columns found or unexpected response structure.');
    }
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