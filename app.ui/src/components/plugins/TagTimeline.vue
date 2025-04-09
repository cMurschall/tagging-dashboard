<template>
    <div ref="chartContainer" style="width: 100%; height: 400px;"></div>


</template>

<script lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import * as echarts from 'echarts/core';
import { CustomChart } from 'echarts/charts';
import {
    TooltipComponent,
    GridComponent,
    DataZoomComponent,
    MarkLineComponent, // Added for potential instantaneous markers
    MarkPointComponent // Added for potential instantaneous markers
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import type { EChartsOption, CustomSeriesRenderItemAPI, CustomSeriesRenderItemParams } from 'echarts';
import type { ECElementEvent } from 'echarts/types/src/util/types';


import { useVideoControl } from '../../composables/useVideoControl';
import gridManager from '../../managers/gridItemManager';


echarts.use([
    CustomChart,
    TooltipComponent,
    GridComponent,
    DataZoomComponent,
    MarkLineComponent,
    MarkPointComponent,
    CanvasRenderer
]);


const { seekTo } = useVideoControl()

type PluginState = {
}

const isPluginState = (obj: any): obj is PluginState => {
    return typeof obj === 'object' && 'counter' in obj;
};



// --- Data Structures ---
interface TimeLabel {
    label_id: string;
    category: string;
    label_start_time: number; // Unix timestamp (milliseconds)
    label_end_time: number;   // Unix timestamp (milliseconds) - same as start for instantaneous
    value?: any; // Optional additional data for tooltip
}

const sampleLabels: TimeLabel[] = [
    { label_id: 'l1', category: 'Alert', label_start_time: 1678886400000, label_end_time: 1678886400000, value: 'System restarted' }, // Instantaneous
    { label_id: 'l2', category: 'Maintenance', label_start_time: 1678890000000, label_end_time: 1678893600000, value: 'DB Backup' }, // Range
    { label_id: 'l3', category: 'Warning', label_start_time: 1678891800000, label_end_time: 1678892400000, value: 'High CPU Load' }, // Range
    { label_id: 'l4', category: 'Alert', label_start_time: 1678895000000, label_end_time: 1678895000000, value: 'Disk Full' }, // Instantaneous
    { label_id: 'l5', category: 'Info', label_start_time: 1678888200000, label_end_time: 1678897200000, value: 'User Activity Spike' }, // Long Range
    { label_id: 'l6', category: 'Maintenance', label_start_time: 1678893600000, label_end_time: 1678894200000, value: 'Patch Deployment' }, // Short Range, same category as l2
];


const chartContainer = ref<HTMLDivElement | null>(null);
let chartInstance: echarts.ECharts | null = null;


const categoryColors: Record<string, string> = {
    'Alert': '#ff4d4f', // Red
    'Maintenance': '#1890ff', // Blue
    'Warning': '#faad14', // Orange
    'Info': '#52c41a', // Green
    'Default': '#bfbfbf' // Grey for unknown categories
};

function getColorByCategory(category: string): string {
    return categoryColors[category] || categoryColors['Default'];
}
// The core rendering logic for the custom series
function renderLabelItem(params: CustomSeriesRenderItemParams, api: CustomSeriesRenderItemAPI): echarts.CustomSeriesRenderItemReturn {
    // `params.dataIndex` is the index of the label in our data array
    // `api.value(0)` gets the first value (label_start_time) from the data item
    // `api.value(1)` gets the second value (label_end_time) from the data item
    // `api.value(2)` gets the third value (category) from the data item
    // `api.value(3)` gets the fourth value (label_id) - useful for identification
    // `api.value(4)` gets the fifth value (value) - for tooltip

    const startTime = api.value(0) as number;
    const endTime = api.value(1) as number;
    const category = api.value(2) as string;
    // const labelId = api.value(3) as string; // Available if needed
    const isInstantaneous = startTime === endTime;

    // Convert time values to x-coordinates on the chart
    const startPoint = api.coord([startTime, params.encode?.y?.[0] ?? 0]); // Using y=0 as baseline for coord calculation
    const endPoint = api.coord([endTime, params.encode?.y?.[0] ?? 0]);




    // Fixed height for the label bars/markers
    const barHeight = 20;
    // Y-position calculation - place items vertically stacked within the band
    // We use `params.dataIndexInside` to get a somewhat stable vertical offset,
    // but this isn't perfect for preventing all overlaps if ranges are dense.
    // A more robust approach might involve pre-calculating non-overlapping tracks.
    const chartHeight = 400; // Get the height of the grid
    const yPosition = chartHeight - (params.dataIndexInside % 5 + 1) * (barHeight + 5); // Simple stacking


    const rectShape = echarts.graphic.clipRectByRect(
        {
            // Define the shape boundaries based on calculated coordinates
            x: startPoint[0],
            y: yPosition,
            width: endPoint[0] - startPoint[0],
            height: barHeight
        },
        {
            // Define the clipping area (the chart's grid area)
            x: params.coordSys.x
            y: params.coordSys.y,
            width: params.coordSys.width,
            height: params.coordSys.height
        }
    );
    // Style based on category
    const itemStyle = {
        fill: getColorByCategory(category),
        // stroke: '#333', // Optional border
        // lineWidth: 1
    };

    if (isInstantaneous) {
        // --- Option 1: Draw a vertical line for instantaneous events ---
        // return {
        //   type: 'line',
        //   shape: {
        //     x1: startPoint[0],
        //     y1: params.coordSys.y, // Top of grid
        //     x2: startPoint[0],
        //     y2: params.coordSys.y + params.coordSys.height // Bottom of grid
        //   },
        //   style: {
        //     stroke: getColorByCategory(category),
        //     lineWidth: 2
        //   }
        // };
        // --- Option 2: Draw a small symbol (e.g., diamond) ---
        return {
            type: 'polygon',
            shape: {
                points: [
                    [startPoint[0], yPosition + barHeight / 2 - 5], // Top point
                    [startPoint[0] + 5, yPosition + barHeight / 2], // Right point
                    [startPoint[0], yPosition + barHeight / 2 + 5], // Bottom point
                    [startPoint[0] - 5, yPosition + barHeight / 2]  // Left point
                ]
            },
            style: itemStyle
        };

    } else {
        // Draw a rectangle for range labels
        return rectShape ? { // Check if rectShape is not null (not entirely clipped)
            type: 'rect',
            transition: ['shape'], // Animate shape changes
            shape: rectShape,
            style: itemStyle
        } : undefined; // Return undefined if the shape is completely outside the view
    }
}


const getChartOption = (labels: TimeLabel[]): EChartsOption => {
    // Find the min and max time for the x-axis range
    let minTime = labels.length > 0 ? labels[0].label_start_time : Date.now();
    let maxTime = labels.length > 0 ? labels[0].label_end_time : Date.now();
    labels.forEach(label => {
        if (label.label_start_time < minTime) minTime = label.label_start_time;
        if (label.label_end_time > maxTime) maxTime = label.label_end_time;
    });

    // Add some padding to the time range
    const timePadding = (maxTime - minTime) * 0.05; // 5% padding

    return {
        tooltip: {
            trigger: 'item', // Trigger tooltip when hovering over an item
            formatter: (params: any) => { // Use 'any' for simplicity, or define a specific type
                const data = params.value as (number | string | object)[];
                const startTime = new Date(data[0] as number).toLocaleString();
                const endTime = new Date(data[1] as number).toLocaleString();
                const category = data[2] as string;
                const details = data[4] ? `<br/>Details: ${data[4]}` : ''; // Access the 'value' field

                if (data[0] === data[1]) { // Instantaneous
                    return `<b>${category}</b><br/>Time: ${startTime}${details}`;
                } else { // Range
                    return `<b>${category}</b><br/>Start: ${startTime}<br/>End: ${endTime}${details}`;
                }
            }
        },
        dataZoom: [ // Allow zooming and panning along the time axis
            {
                type: 'slider', // Slider at the bottom
                xAxisIndex: 0,
                filterMode: 'weakFilter', // Allows seeing items outside the current range slightly
                height: 20,
                bottom: 10,
                start: 0,
                end: 100,
                handleIcon: 'path://M10.7,11.9H9.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4h1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,21.6H6.7v-1.4h6.6V21.6z',
                handleSize: '80%',
                labelFormatter: (value: number) => new Date(value).toLocaleString() // Format labels on dataZoom slider
            },
            {
                type: 'inside', // Allow zooming with mouse wheel/touchpad
                xAxisIndex: 0,
                filterMode: 'weakFilter'
            }
        ],
        grid: {
            left: '5%', // Add some left padding for y-axis labels if needed
            right: '5%',
            bottom: 50, // Space for dataZoom slider
            top: 30 // Space for title or other elements if added
        },
        xAxis: {
            type: 'time', // Use time axis
            min: minTime - timePadding,
            max: maxTime + timePadding,
            axisLabel: {
                formatter: (value: number) => new Date(value).toLocaleTimeString() // Format time labels
            },
            splitLine: { // Add vertical grid lines for better readability
                show: true,
                lineStyle: {
                    color: '#e0e0e0',
                    type: 'dashed'
                }
            }
        },
        yAxis: {
            // We don't really need a meaningful y-axis scale here,
            // as we are manually positioning items.
            // We can hide it or use it for categories if needed.
            show: false, // Hide the y-axis line and labels
            // --- Alternative: Categorical Y-Axis (more complex positioning needed in renderItem) ---
            // type: 'category',
            // data: ['Alert', 'Maintenance', 'Warning', 'Info'], // Define categories
            // axisLabel: { interval: 0 }, // Show all labels
            // splitLine: { show: true }
        },
        series: [
            {
                type: 'custom',
                name: 'Labels', // Name for the series (shows in legend if enabled)
                renderItem: renderLabelItem, // The custom rendering function
                itemStyle: { // Default item style (can be overridden in renderItem)
                    opacity: 0.8
                },
                encode: {
                    // Map data dimensions to axes. We primarily use time for x.
                    // We don't map directly to y, as positioning is manual in renderItem.
                    x: [0, 1], // Use label_start_time and label_end_time for x-axis positioning
                    // y: 2, // If using categorical y-axis, map category here
                    tooltip: [0, 1, 2, 4] // Include these fields in tooltip data (start, end, category, value)
                },
                // Map data fields to the renderItem function's api.value() indices
                // Order: [label_start_time, label_end_time, category, label_id, value]
                data: labels.map(label => [
                    label.label_start_time,
                    label.label_end_time,
                    label.category,
                    label.label_id,
                    label.value
                ])
            }
        ]
    };
};

// --- Lifecycle Hooks ---
onMounted(() => {
    if (chartContainer.value) {
        chartInstance = echarts.init(chartContainer.value);
        // Use sample data initially, or data from props if available
        // const dataToRender = props.labels || sampleLabels;
        const dataToRender = sampleLabels;
        chartInstance.setOption(getChartOption(dataToRender));

        // Optional: Add resize listener
        window.addEventListener('resize', handleResize);
    }
});

onBeforeUnmount(() => {
    if (chartInstance) {
        chartInstance.dispose();
    }
    window.removeEventListener('resize', handleResize);
});

// --- Watch for Data Changes (if using props) ---
// watch(() => props.labels, (newLabels) => {
//   if (chartInstance && newLabels) {
//     chartInstance.setOption(getChartOption(newLabels), { notMerge: true }); // Use notMerge to clear previous data
//   }
// }, { deep: true });

// --- Resize Handler ---
function handleResize() {
    chartInstance?.resize();
}

</script>