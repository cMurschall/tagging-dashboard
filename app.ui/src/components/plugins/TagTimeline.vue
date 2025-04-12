<template>
    <Chart ref="chartRef" :option="chartOption" :style="{ width: '100%', height: '100%' }"
        :autoresize="{ throttle: 100 }" />


</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
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

import { useVideoControl } from '../../composables/useVideoControl';
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
    value?: any;
}



const sampleLabels: TimeLabel[] = [
    { label_id: 'l1', category: 'Alert', label_start_time: 10, label_end_time: 10, value: 'System restarted' },
    { label_id: 'l2', category: 'Maintenance', label_start_time: 20, label_end_time: 40, value: 'DB Backup' },
    { label_id: 'l3', category: 'Warning', label_start_time: 30, label_end_time: 35, value: 'High CPU Load' },
    { label_id: 'l4', category: 'Alert', label_start_time: 50, label_end_time: 50, value: 'Disk Full' },
    { label_id: 'l5', category: 'Info', label_start_time: 15, label_end_time: 80, value: 'User Activity Spike' },
    { label_id: 'l6', category: 'Maintenance', label_start_time: 40, label_end_time: 45, value: 'Patch Deployment' },
];


const chartRef = ref<typeof Chart | null>(null);
const chartOption = ref<EChartsOption>({});

const categoryColors: Record<string, string> = {
    Alert: '#ff4d4f', // Red
    Maintenance: '#1890ff', // Blue
    Warning: '#faad14', // Orange
    Info: '#52c41a', // Green
    Default: '#bfbfbf', // Grey for unknown categories
};


function getColorByCategory(categoryIndex: number): string {
    // get index from categoryColors
    const category = Object.keys(categoryColors)[categoryIndex];
    return categoryColors[category] || categoryColors.Default;

}


// The core rendering logic for the custom series
function renderLabelItem(params: CustomSeriesRenderItemParams, api: CustomSeriesRenderItemAPI): echarts.CustomSeriesRenderItemReturn {

    console.log("api:", api);


    const startTime = api.value(0) as number;
    const endTime = api.value(1) as number;
    const category = api.value(2) as string;
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
            }
            : undefined;
    }
}

const getChartOption = (labels: TimeLabel[]): EChartsOption => {
    let minTime = labels[0]?.label_start_time ?? 0;
    let maxTime = labels[0]?.label_end_time ?? 0;
    const categories = [...new Set(labels.map((label) => label.category))]; // Extract unique categories

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
                    label.value,
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

const handleOnChartClick = (params: any) => {

    // const chart = chartRef.value;
    // if (!chart) return;


    // const pointInPixel = [params.event.offsetX, params.event.offsetY];
    // const pointInGrid = chart.convertFromPixel({ xAxisIndex: 0 }, pointInPixel);
    // const time = pointInGrid[0];

    // // Call your seekTo function
    // // seekTo(time);

    // // Update the markLine
    // const updatedOption = chart.getOption();
    // updatedOption.series[0].markLine.data = [{ xAxis: time }];
    // chart.setOption(updatedOption);
};

onMounted(() => {
    chartOption.value = getChartOption(sampleLabels);
});
</script>