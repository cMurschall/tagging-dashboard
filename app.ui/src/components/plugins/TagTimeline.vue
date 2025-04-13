<template>

    <div ref="containerRef" style="width: 100%; height: 100%;">
        <Transition name="fade" mode="out-in">

            <div v-if="showMenu">
                <div class="p-3">
                    <h4>Known Tag Categories</h4>
                    <BRow class="mb-3">
                        <!-- New Category Form -->
                        <div class="mb-3 d-flex align-items-center gap-2">
                            <input v-model="newTagCategoryName" class="form-control" style="max-width: 250px;"
                                placeholder="New category name" />
                            <BButton variant="success" @click="addTagCategory" :disabled="!newTagCategoryName.trim()">
                                Add
                            </BButton>
                        </div>
                    </BRow>

                    <BRow class="mb-3">
                        <BCol cols="6">
                            <!-- Category List -->
                            <BListGroup>
                                <BListGroupItem v-for="(category, index) in availableTagCategories" :key="category.id"
                                    class="d-flex justify-content-between align-items-center">
                                    {{ category.name }}
                                    <BButton size="sm"
                                        :style="{ backgroundColor: categoryColors[index % categoryColors.length] }"
                                        @click="deleteTagCategory(category)">Delete</BButton>
                                </BListGroupItem>
                            </BListGroup>
                        </BCol>
                    </BRow>
                </div>
            </div>
            <div v-else class="d-flex flex-column" style="height: 100%;">
                <!-- Flex container for a single-row layout -->
                <div class="d-flex align-items-center flex-wrap gap-1">

                    <BButton v-for="(category, index) in allCategories" :key="category" :style="{
                        backgroundColor: categoryColors[index % categoryColors.length],
                        border: 'none',
                        color: '#fff'
                    }" @click="toggleTag(category)">
                        {{ toggleState[category] ? 'Stop ' : 'Start ' }}'{{ category }}'</BButton>

                </div>


                <Chart ref=" chartRef" :option="chartOption" :style="{ width: '100%', height: '80%' }"
                    :autoresize="{ throttle: 100 }" @click="handleOnChartClick" />

                <div v-if="activeLabel" class="mt-1">

                    <!-- Flex container for a single-row layout -->
                    <div class="d-flex align-items-center flex-wrap gap-1">

                        <h5 class="mb-0 me-2">Edit Label: {{ activeLabel.label_id }}</h5>


                        <!-- Start Time -->
                        <label for="startTime" class="mb-0">Start:</label>
                        <input id="startTime" type="number" class="form-control" style="width: 100px;"
                            v-model="formData.start" />

                        <!-- End Time -->
                        <label for="endTime" class="mb-0">End:</label>
                        <input id="endTime" type="number" class="form-control" style="width: 100px;"
                            v-model="formData.end" />

                        <!-- Category -->
                        <label for="category" class="mb-0">Category:</label>
                        <input id="category" type="text" class="form-control" style="width: 150px;"
                            v-model="formData.category" />


                        <!-- Notes -->
                        <label for="notes" class="mb-0">Notes:</label>
                        <input id="notes" type="text" class="form-control" style="width: 150px;"
                            v-model="formData.category" />


                        <!-- Buttons -->
                        <BButton variant="primary" @click="onSaveLabel">Save</BButton>
                        <BButton variant="danger" @click="onDeleteLabel">Delete</BButton>
                        <BButton variant="secondary" @click="onCancelEdit">Cancel</BButton>
                    </div>
                </div>


            </div>

        </Transition>
    </div>


</template>

<script setup lang="ts">
import { ref, onMounted, reactive, inject, onUnmounted, computed } from 'vue';
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
import { useToastController, BButton, BTable, BRow, BCol } from "bootstrap-vue-next";

import { useVideoControl } from '../../composables/useVideoControl';
import { Tag, TagCategory } from '../../../services/restclient';
import { safeFetch, TagApiClient as client, TestDriveProjectInfo } from '../../services/utilities';
import { Observable, Subscription } from '../../observable';



echarts.use([
    CustomChart,
    TooltipComponent,
    GridComponent,
    DataZoomComponent,
    MarkLineComponent,
    MarkPointComponent,
    CanvasRenderer,
]);

const { show: showToast } = useToastController();
const { seekTo } = useVideoControl();


// Inject the function from the parent
const setCardTitle = inject('setCardTitle') as (title: string) => void;


type PluginState = {

}




interface TagTimelineProps {
    showMenu: boolean;
    id: string;
    pluginState?: PluginState;

    projectInfo?: TestDriveProjectInfo,
}


const props = withDefaults(defineProps<TagTimelineProps>(), {
    showMenu: false, // Default value for showMenu

    id: '', // Default value for id
    pluginState: () => ({

    }),

});

const pluginState = ref<PluginState>(structuredClone(props.pluginState));

const simulationTimeObservable = inject<Observable<number>>('simulationTimeObservable');
if (!simulationTimeObservable) {
    throw new Error('simulationTimeObservable not provided');
}


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
        fill: getColorByCategory(parseInt(category)),
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

const allCategories = computed(() => {
    const uniqueCategories = new Set([
        ...availableTags.value.map((label) => label.category),
        ...availableTagCategories.value.map((t) => t.name),
    ].filter(x => x !== undefined && x !== null && x !== ''));
    const categories = Array.from(uniqueCategories);

    categories.forEach((category, index) => {
        toggleState.value[category!] = true; // Initialize toggle state for each category
    });


    return categories as string[];
});


const getChartOption = (): EChartsOption => {
    const labels = availableTags.value;


    const minDataTime = props.projectInfo?.testDriveDataInfo?.dataSimulationTimeStartS ?? 0;
    const maxDataTime = props.projectInfo?.testDriveDataInfo?.dataSimulationTimeEndS ?? 0;

    const minVideoTime = props.projectInfo?.testDriveVideoInfo?.videoSimulationTimeEndS ?? 0;
    const maxVideoTime = props.projectInfo?.testDriveVideoInfo?.videoSimulationTimeEndS ?? 0;


    let minLabelTime = labels[0]?.label_start_time ?? 0;
    let maxLabelTime = labels[0]?.label_end_time ?? 0;

    labels.forEach((label) => {
        minLabelTime = Math.min(minLabelTime, label.label_start_time);
        maxLabelTime = Math.max(maxLabelTime, label.label_end_time);
    });

    const minTime = Math.min(minDataTime, minVideoTime, minLabelTime);
    const maxTime = Math.max(maxDataTime, maxVideoTime, maxLabelTime);






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
            // {
            //     type: 'slider',
            //     xAxisIndex: 0,
            //     filterMode: 'weakFilter',
            //     startValue: minTime,
            //     endValue: maxTime,
            // },
        ],
        grid: {
            left: '5%',
            right: '1%',
            bottom: 0,
            top: 0,
            containLabel: true, // Ensure category labels are within the grid
        },
        xAxis: {
            type: 'value',
            min: minTime,
            max: maxTime + timePadding,
            axisLabel: {
                formatter: (value: number) => `${value.toFixed(0)}s`,
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
            data: [...allCategories.value] as string[], // Use the extracted unique categories
            axisLabel: { interval: 0 },
            splitLine: { show: true },
            inverse: true
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
                        color: 'red',
                        type: 'dashed',
                        width: 2,
                    },
                    data: [
                        { xAxis: currentSimulationTime }, // Placeholder, will be updated
                    ],
                    tooltip: {
                        formatter: (params: any) => {

                            const time = params.value as number;
                            return `${time.toFixed(2)}s`;
                        },
                    },
                    animation: false,
                },
            },
        ],
    };
};



const availableTags = ref<TimeLabel[]>([]);
const availableTagCategories = ref<TagCategory[]>([]);


// --- Category Form State ---
const newTagCategoryName = ref('');
const editId = ref<number | null>(null);
const editName = ref('');

// --- Start Edit ---
const startEditTagCategory = (category: TagCategory) => {
    editId.value = category.id ?? null;
    editName.value = category.name ?? '';
}



// --- Cancel Edit ---
const cancelEdit = () => {
    editId.value = null;
    editName.value = '';
}

// --- Add Category ---
const addTagCategory = async () => {
    const trimmed = newTagCategoryName.value.trim();
    if (!trimmed) return;

    const [error, response] = await safeFetch(() => client.addTagCategoryApiV1TagCategoryPost({
        createNewTagCategoryPayload: {
            name: trimmed,
        }
    }));
    if (error) {
        console.error('Error adding category:', error);
        showToast?.({
            props: {
                title: `Error adding category: ${trimmed}`,
                body: error.message,
                value: 2500,
                variant: 'danger',
                pos: 'top-end',

            }
        });
        return;
    }

    if (response && response.categories) {

        // find difference between the two arrays and add the new ones to the availableTagCategories
        const newCategories = response.categories.filter((c: TagCategory) => !availableTagCategories.value.some((existing: TagCategory) => existing.id === c.id));
        availableTagCategories.value.push(...newCategories);

        showToast?.({
            props: {
                title: `Category added: ${trimmed}`,
                body: `Category ${trimmed} has been added.`,
                value: 2500,
                variant: 'success',
                pos: 'top-end',

            }
        });

        newTagCategoryName.value = '';
    } else {
        console.warn('No category found or unexpected response structure.');
    }

}


// --- Delete Category ---
const deleteTagCategory = async (category: TagCategory) => {
    const index = availableTagCategories.value.findIndex(c => c.id === category.id);
    if (index === -1) return; // Category not found

    const item = availableTagCategories.value[index];
    if (!item || item.id == undefined) return; // Category not found

    const [error, response] = await safeFetch(() => client.deleteTagCategoryApiV1TagCategoryCategoryIdDelete({
        categoryId: parseInt(item.id?.toString() ?? '-1'),
    }));
    if (error) {
        console.error('Error deleting category:', error);
        showToast?.({
            props: {
                title: `Error deleting category: ${item.name}`,
                body: error.message,
                value: 2500,
                variant: 'danger',
                pos: 'top-end',

            }
        });
        return;
    }


    // Remove the category from the availableTagCategories
    availableTagCategories.value.splice(index, 1);

    showToast?.({
        props: {
            title: `Category deleted: ${item.name}`,
            body: `Category ${item.name} has been deleted.`,
            value: 2500,
            variant: 'success',
            pos: 'top-end',

        }
    });
}



// --- Save Edit ---
const saveEditTagCategory = (category: TagCategory) => {
    // nothing to do.
}



// A reactive state for toggle status, one per category
const toggleState = ref<Record<string, boolean>>({});


// Toggle function: toggles state for a category
const toggleTag = (category: string) => {
    toggleState.value[category] = !toggleState.value[category];
    console.log(`${category} has been ${toggleState.value[category] ? 'started' : 'stopped'}`);
    // Insert additional logic for handling the tag state here.
}

const startNewTag = (category: string) => {
    // Set state that a new tag is being created for the given category.
    console.log("Starting new tag for category:", category);
};

const stopNewTag = (category: string) => {

    // Set state that the new tag creation is stopped.
    console.log("Stopping new tag for category:", category);
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
        const index = availableTags.value.findIndex(l => l.label_id === activeLabel.value?.label_id);
        if (index !== -1) {
            availableTags.value[index].label_start_time = formData.start;
            availableTags.value[index].label_end_time = formData.end;
            availableTags.value[index].category = formData.category;


            chartOption.value = getChartOption();
        }
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



let subscription: Subscription | null = null;

const currentSimulationTime = ref(0);

onMounted(async () => {

    await loadProjectTags()
    await loadProjectTagCategories();
    chartOption.value = getChartOption();

    subscription = simulationTimeObservable.subscribe((time) => {
        currentSimulationTime.value = time;
        // setCardTitle(`Player: ${time}`);
    });
});

onUnmounted(() => {
    subscription?.unsubscribe();
});


</script>