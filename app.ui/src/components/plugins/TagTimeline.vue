<template>
    <Chart ref="chartRef" :option="chartOption" :style="{ width: '100%', height: '80%' }"
        :autoresize="{ throttle: 100 }" @click="handleOnChartClick" />

    <!-- The editor form goes below (visible if we have an activeLabel) -->
    <div v-if="activeLabel" class="mt-1">

        <!-- Flex container for a single-row layout -->
        <div class="d-flex align-items-center flex-wrap gap-1">

            <h5 class="mb-0 me-2">Edit Label: {{ activeLabel.label_id }}</h5>


            <!-- Start Time -->
            <label for="startTime" class="mb-0">Start:</label>
            <input id="startTime" type="number" class="form-control" style="width: 100px;" v-model="formData.start" />

            <!-- End Time -->
            <label for="endTime" class="mb-0">End:</label>
            <input id="endTime" type="number" class="form-control" style="width: 100px;" v-model="formData.end" />

            <!-- Category -->
            <label for="category" class="mb-0">Category:</label>
            <input id="category" type="text" class="form-control" style="width: 150px;" v-model="formData.category" />


            <!-- Notes -->
            <label for="notes" class="mb-0">Notes:</label>
            <input id="notes" type="text" class="form-control" style="width: 150px;" v-model="formData.category" />


            <!-- Buttons -->
            <BButton variant="primary" @click="onSaveLabel">Save</BButton>
            <BButton variant="danger" @click="onDeleteLabel">Delete</BButton>
            <BButton variant="secondary" @click="onCancelEdit">Cancel</BButton>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import Chart from 'vue-echarts';

import * as echarts from 'echarts/core';
import { CustomChart } from 'echarts/charts';
import {
    TooltipComponent,
    GridComponent,
    DataZoomComponent,
    MarkLineComponent,
    MarkPointComponent,
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import type { EChartsOption, CustomSeriesRenderItemAPI, CustomSeriesRenderItemParams } from 'echarts';
import { BButton } from "bootstrap-vue-next";
import { useVideoControl } from '../../composables/useVideoControl';
import { Tag, TagCategory } from '../../../services/restclient';
import { safeFetch, TagApiClient as client } from '../../services/utilities';
// import gridManager from '../../managers/gridItemManager'; // Assuming this is not directly used for chart logic

echarts.use([
    CustomChart,
    TooltipComponent,
    GridComponent,
    DataZoomComponent,
    MarkLineComponent,
    MarkPointComponent,
    CanvasRenderer,
]);

const { seekTo } = useVideoControl();



// TimeLabel interface remains the same
interface TimeLabel {
    label_id: string;
    category: string;
    label_start_time: number; //  seconds
    label_end_time: number;   //  seconds
    note?: any;
}





const chartRef = ref<typeof Chart | null>(null);
const chartOption = ref<EChartsOption>({});


const categoryColors = [
    '#0072B2', // blue
    '#E69F00', // orange
    '#009E73', // green
    '#F0E442', // yellow
    '#56B4E9', // sky blue
    '#D55E00', // vermillion (reddish orange)
    '#CC79A7', // purple-pink
    '#999999', // gray
    '#000000', // black
    '#8DD3C7', // teal
    '#FB8072', // salmon
    '#80B1D3', // light blue
];


function getColorByCategory(categoryIndex: number): string {

    return categoryColors[categoryIndex] || categoryColors[categoryColors.length - 1]; // default to last color if not found

}


// The core rendering logic for the custom series
function renderLabelItem(params: CustomSeriesRenderItemParams, api: CustomSeriesRenderItemAPI): echarts.CustomSeriesRenderItemReturn {

    console.log("api:", api);


    const startTime = api.value(0) as number;
    const endTime = api.value(1) as number;
    const category = api.value(2) as string;
    const labelId = api.value(3) as string;


    const isInstantaneous = startTime === endTime;

    const startPoint = api.coord([startTime, api.value(2)]); // Use category value for y-coordinate
    const endPoint = api.coord([endTime, api.value(2)]);

    const barHeight = 20;
    const yPosition = startPoint[1] - barHeight / 2; // Center the bar vertically on the category

    const rectShape = echarts.graphic.clipRectByRect(
        {
            x: startPoint[0],
            y: yPosition,
            width: endPoint[0] - startPoint[0],
            height: barHeight,
        },
        {
            x: params.coordSys.x,
            y: params.coordSys.y,
            width: params.coordSys.width,
            height: params.coordSys.height,
        }
    );

    const itemStyle = {
        fill: getColorByCategory(category),
    };

    if (isInstantaneous) {
        return {
            type: 'polygon',
            shape: {
                points: [
                    [startPoint[0], yPosition + barHeight / 2 - 5],
                    [startPoint[0] + 5, yPosition + barHeight / 2],
                    [startPoint[0], yPosition + barHeight / 2 + 5],
                    [startPoint[0] - 5, yPosition + barHeight / 2],
                ],
            },
            style: itemStyle,
        };
    } else {
        return rectShape
            ? {
                type: 'rect',
                transition: ['shape'],
                shape: rectShape,
                style: itemStyle,
                id: labelId,
            }
            : undefined;
    }
}

const getChartOption = (): EChartsOption => {


    const labels = availableTags.value;
    let minTime = labels[0]?.label_start_time ?? 0;
    let maxTime = labels[0]?.label_end_time ?? 0;
    //const categories = [...new Set(labels.map((label) => label.category))]; // Extract unique categories
    const uniqueCategories = new Set( [...labels.map((label) => label.category), ...availableTagCategories.value.map(t => t.name)  ]);
    const categories = Array.from(uniqueCategories).sort((a, b) => b.localeCompare(a)); // Sort categories alphabetically


    labels.forEach((label) => {
        minTime = Math.min(minTime, label.label_start_time);
        maxTime = Math.max(maxTime, label.label_end_time);
    });

    const timePadding = (maxTime - minTime) * 0.05;

    return {
        tooltip: {
            trigger: 'item',
            formatter: (params: any) => {
                const data = params.value as (number | string | object)[];
                const startTime = `${data[0]}s`;
                const endTime = `${data[1]}s`;
                const category = data[2] as string;
                const details = data[4] ? `<br/>Details: ${data[4]}` : '';

                if (data[0] === data[1]) {
                    return `<b>${category}</b><br/>Time: ${startTime}${details}`;
                } else {
                    return `<b>${category}</b><br/>Start: ${startTime}<br/>End: ${endTime}${details}`;
                }
            },
        },
        dataZoom: [
            {
                type: 'inside',
                xAxisIndex: 0,
                filterMode: 'weakFilter',
            },
        ],
        grid: {
            left: '5%',
            right: '5%',
            bottom: 50,
            top: 30,
            containLabel: true, // Ensure category labels are within the grid
        },
        xAxis: {
            type: 'value',
            min: minTime - timePadding,
            max: maxTime + timePadding,
            axisLabel: {
                formatter: (value: number) => `${value}s`,
            },
            splitLine: {
                show: true,
                lineStyle: {
                    color: '#e0e0e0',
                    type: 'dashed',
                },
            },
        },
        yAxis: {
            type: 'category',
            data: categories, // Use the extracted unique categories
            axisLabel: { interval: 0 },
            splitLine: { show: true },
        },
        series: [
            {
                type: 'custom',
                name: 'Labels',
                renderItem: renderLabelItem,
                itemStyle: {
                    opacity: 0.8,
                },
                encode: {
                    x: [0, 1], // label_start_time, label_end_time
                    y: 2,     // category
                    tooltip: [0, 1, 2, 4], // start, end, category, value
                },
                data: labels.map((label) => [
                    label.label_start_time,
                    label.label_end_time,
                    label.category,
                    label.label_id,
                    label.note,
                ]),
                markLine: {
                    symbol: 'none',
                    label: { show: false },
                    lineStyle: {
                        color: '#000',
                        type: 'solid',
                        width: 2,
                    },
                    data: [
                        { xAxis: 0 }, // Placeholder, will be updated
                    ],
                },
            },
        ],
    };
};


const activeLabel = ref<TimeLabel | null>(null);

// This object tracks whatever the user types in the "edit" form
const formData = reactive({
    start: 0,
    end: 0,
    category: '',
});

const setFormData = (label: TimeLabel) => {
    formData.start = label.label_start_time;
    formData.end = label.label_end_time;
    formData.category = label.category;
}

const handleOnChartClick = (params: any) => {
    if (params.componentType === 'series' && params.componentSubType === 'custom') {
        // Identify the clicked label

        // const startTime = params.value[0] as number;
        // const endTime = params.value[1] as number;
        // const category = params.value[2] as string;
        const labelId = params.value[3] as string;


        // Find the label in your `labels` array
        const found = availableTags.value.find(l => l.label_id === labelId);
        if (found) {
            activeLabel.value = { ...found };
            setFormData(found);
        }
    } else {
        // Clicked somewhere else, optionally clear active label
        // activeLabel.value = null;
    }
}

const onSaveLabel = () => {
    if (activeLabel.value) {
        activeLabel.value.label_start_time = formData.start;
        activeLabel.value.label_end_time = formData.end;
        activeLabel.value.category = formData.category;
        chartOption.value = getChartOption();
    }
}

const onDeleteLabel = () => {
    if (activeLabel.value) {
        const index = availableTags.value.findIndex(l => l.label_id === activeLabel.value?.label_id);
        if (index !== -1) {
            availableTags.value.splice(index, 1);
            chartOption.value = getChartOption();
        }
    }
}

const onCancelEdit = () => {
    activeLabel.value = null;
    setFormData({ label_id: '', category: '', label_start_time: 0, label_end_time: 0 });
}

const availableTagCategories = ref<TagCategory[]>([]); // Assuming the type of categories is any, adjust as needed

const loadProjectTagCategories = async () => {
    console.log("Loading Categories...");
    const [error, response] = await safeFetch(() => client.getAllTagCategoriesApiV1TagCategoryAllGet());
    if (response && response.categories) {
        availableTagCategories.value = response.categories;

    } else if (error) {
        console.error('Error loading columns:', error);
    } else {
        console.warn('No columns found or unexpected response structure.');
    }
};

const availableTags = ref<TimeLabel[]>([]); // Assuming the type of categories is any, adjust as needed

const loadProjectTags = async () => {
    console.log("Loading Tags...");
    const [error, response] = await safeFetch(() => client.getAllTagsApiV1TagAllGet());
    if (response && response.tags) {
        availableTags.value = response.tags.map((tag: Tag) => ({
            label_id: tag.id?.toString() ?? '',
            category: tag.category,
            label_start_time: tag.timestampStartS,
            label_end_time: tag.timestampEndS,
            note: tag.notes,
        })) as TimeLabel[]; // Cast to TimeLabel type

        console.log("Tags loaded:", availableTags.value);

    } else if (error) {
        console.error('Error loading columns:', error);
    } else {
        console.warn('No columns found or unexpected response structure.');
    }
};

const sampleLabels: TimeLabel[] = [
    { label_id: 'l1', category: 'Alert', label_start_time: 10, label_end_time: 10, note: 'System restarted' },
    { label_id: 'l2', category: 'Maintenance', label_start_time: 20, label_end_time: 40, note: 'DB Backup' },
    { label_id: 'l3', category: 'Warning', label_start_time: 30, label_end_time: 35, note: 'High CPU Load' },
    { label_id: 'l4', category: 'Alert', label_start_time: 50, label_end_time: 50, note: 'Disk Full' },
    { label_id: 'l5', category: 'Info', label_start_time: 15, label_end_time: 80, note: 'User Activity Spike' },
    { label_id: 'l6', category: 'Maintenance', label_start_time: 40, label_end_time: 45, note: 'Patch Deployment' },
];



onMounted(async () => {
    availableTags.value = sampleLabels;
    await loadProjectTags()
    await loadProjectTagCategories();
    chartOption.value = getChartOption();
});
</script>