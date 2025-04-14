<template>

    <div ref="containerRef" class="full-size-container">
        <Transition name="fade" mode="out-in">

            <div v-if="showMenu">
                <div class="p-3">
                    <h4>Known Tag Categories</h4>
                    <BRow class="mb-3">
                        <!-- New Category Form -->
                        <div class="mb-3 d-flex align-items-center gap-2">
                            <input v-model="newTagCategoryName" class="form-control input-max-width-250"
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

                    <BButton v-for="(category, index) in allCategories" :key="category" class="category-button"
                        :class="['category-button', { 'is-recording': toggleState[category] }]"
                        :style="{ backgroundColor: categoryColors[index % categoryColors.length] }"
                        @click="toggleTag(category)">
                        {{ toggleState[category] ? 'Stop ' : 'Start ' }}'{{ category }}'</BButton>

                </div>


                <Chart ref=" chartRef" :option="chartOption" class="chart-dimensions" :autoresize="{ throttle: 100 }"
                    @click="handleOnChartClick" />

                <div v-if="selectedTag" class="mt-1">

                    <!-- Flex container for a single-row layout -->
                    <div class="d-flex align-items-center flex-wrap gap-2">
                        <h5 class="mb-0 me-2">Edit:</h5>

                        <!-- Start -->
                        <div class="d-flex align-items-center gap-1">
                            <label for="startTime" class="form-label mb-0">Start:</label>
                            <BFormInput id="startTime" type="number" v-model="formData.start" size="sm"
                                class="input-width-100" />
                        </div>

                        <!-- End -->
                        <div class="d-flex align-items-center gap-1">
                            <label for="endTime" class="form-label mb-0">End:</label>
                            <BFormInput id="endTime" type="number" v-model="formData.end" size="sm"
                                class="input-width-100" />
                        </div>

                        <!-- Category -->
                        <div class="d-flex align-items-center gap-1">
                            <label for="category" class="form-label mb-0">Category:</label>
                            <BFormSelect id="category" v-model="formData.category" :options="allCategories" size="sm"
                                class="select-width-150" />
                        </div>

                        <!-- Notes -->
                        <div class="d-flex align-items-center gap-1">
                            <label for="notes" class="form-label mb-0">Notes:</label>
                            <BFormInput id="notes" type="text" v-model="formData.note" size="sm"
                                class="input-width-250" />
                        </div>

                        <!-- Buttons -->
                        <BButton size="sm" variant="primary" @click="saveTag">Save</BButton>
                        <BButton size="sm" variant="danger" @click="deleteTag">Delete</BButton>
                        <BButton size="sm" variant="secondary" @click="onCancelEditLabel">Cancel</BButton>
                    </div>
                </div>


            </div>

        </Transition>
    </div>


</template>

<script setup lang="ts">
import { ref, onMounted, reactive, inject, onUnmounted, computed, watch } from 'vue';
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
import { BButton, BRow, BCol, BListGroup, BListGroupItem, BFormSelect, BFormInput } from "bootstrap-vue-next";

import { useVideoControl } from '../../composables/useVideoControl';
import { Tag, TagCategory } from '../../../services/restclient';
import { safeFetch, TagApiClient as client, TestDriveProjectInfo } from '../../services/utilities';
import { Observable, Subscription } from '../../observable';
import { SetCardTitleFn, ShowToastFn } from '../../plugins/AppPlugins';



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


// Inject the function from the parent
const setCardTitle = inject<SetCardTitleFn>('setCardTitle') ?? (() => { });
const showToast = inject<ShowToastFn>('showToast');

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


interface TagViewModel {
    id: string;
    category: string;
    startTime: number; //  seconds
    endTime: number;   //  seconds
    note?: any;
    isFloating: boolean;
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
function renderTagItem(params: CustomSeriesRenderItemParams, api: CustomSeriesRenderItemAPI): echarts.CustomSeriesRenderItemReturn {

    const startTime = api.value(0) as number;
    const endTime = api.value(1) as number;
    const category = api.value(2) as string;
    const labelId = api.value(3) as string;
    const note = api.value(4) as string;
    const isFloating = api.value(5) as unknown as boolean;


    const isInstantaneous = endTime - startTime < 2; // Check if the label is (almost) instantaneous

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
        opacity: isFloating ? 0.5 : 1,
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




const createChartOption = (): EChartsOption => {
    const labels = availableTags.value;


    const minDataTime = props.projectInfo?.testDriveDataInfo?.dataSimulationTimeStartS ?? 0;
    const maxDataTime = props.projectInfo?.testDriveDataInfo?.dataSimulationTimeEndS ?? 0;

    const minVideoTime = props.projectInfo?.testDriveVideoInfo?.videoSimulationTimeEndS ?? 0;
    const maxVideoTime = props.projectInfo?.testDriveVideoInfo?.videoSimulationTimeEndS ?? 0;


    let minLabelTime = labels[0]?.startTime ?? 0;
    let maxLabelTime = labels[0]?.endTime ?? 0;

    labels.forEach((label) => {
        minLabelTime = Math.min(minLabelTime, label.startTime);
        maxLabelTime = Math.max(maxLabelTime, label.endTime);
    });

    const minTime = Math.min(minDataTime, minVideoTime, minLabelTime);
    const maxTime = Math.max(maxDataTime, maxVideoTime, maxLabelTime);






    const timePadding = (maxTime - minTime) * 0.05;

    return {
        tooltip: [
            {
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
            // {
            //     trigger: 'axis', // Trigger tooltip on axis pointer move
            //     axisPointer: {
            //         axis: 'x', // Use x-axis pointer
            //         type: 'line', // Show a line axis pointer
            //         lineStyle: {
            //             color: 'red',
            //             width: 1
            //         },
            //         z: 100 // Ensure it's on top
            //     },
            // }
        ],
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
                renderItem: renderTagItem,
                itemStyle: {
                    opacity: 0.8,
                },
                encode: {
                    x: [0, 1], // label_start_time, label_end_time
                    y: 2,     // category
                    tooltip: [0, 1, 2, 4], // start, end, category, value
                },
                data: labels.map((label) => [
                    label.startTime,
                    label.endTime,
                    label.category,
                    label.id,
                    label.note,
                    label.isFloating
                ]),
                markPoint: {
                    symbol: 'circle',
                    symbolSize: 10,

                    silent: true,
                    label: {
                        show: false,
                    },
                    itemStyle: {
                        color: 'red',
                        opacity: 1,
                    },
                    z: 1,
                    data: [
                        {
                            xAxis: currentSimulationTime,
                            y: '90%',
                        }
                    ],
                    // Disable animation
                    animation: false,
                },
            },
        ],
    };
};



const availableTags = ref<TagViewModel[]>([]);
const availableTagCategories = ref<TagCategory[]>([]);



const allCategories = computed(() => {
    const uniqueCategories = new Set([
        ...availableTags.value.map((label) => label.category),
        ...availableTagCategories.value.map((t) => t.name),
    ].filter(x => x !== undefined && x !== null && x !== ''));
    const categories = Array.from(uniqueCategories);

    return categories as string[];
});


watch(allCategories, (newCategories, oldCategories) => {
    // Check if the new categories are different from the old ones
    if (newCategories.length === oldCategories.length && newCategories.every((cat, index) => cat === oldCategories[index])) {
        return; // No change in categories
    }
    // Update the toggle state for the new categories
    toggleState.value = {}; // Reset toggle state
    newCategories.forEach((category, index) => {
        toggleState.value[category] = false; // Initialize toggle state for each category
    });
},);



// --- Category Form State ---
const newTagCategoryName = ref('');

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
    if (toggleState.value[category]) {
        startNewTag(category);
    } else {
        stopNewTag(category);
    }
}

const startNewTag = (category: string) => {
    // Set state that a new tag is being created for the given category.
    console.log("Starting new tag for category:", category);
    // add floating tag to the chart

    const newTagId = 'tag_' + Math.random().toString(36)
    const newTag: TagViewModel = {
        id: newTagId,
        category: category,
        startTime: currentSimulationTime.value,
        endTime: currentSimulationTime.value,
        note: '',
        isFloating: true,
    };
    availableTags.value.push(newTag);
    chartOption.value = createChartOption();
};

const stopNewTag = async (category: string) => {

    // Set state that the new tag creation is stopped.
    console.log("Stopping new tag for category:", category);
    // find the floating tag in the chart
    const floatingTag = availableTags.value.find(tag => tag.category === category && tag.isFloating);
    if (floatingTag) {

        floatingTag.isFloating = false; // Mark it as not floating anymore

        const [error, response] = await safeFetch(() => client.addTagApiV1TagCreatePost({
            createTagPayload: {
                category: floatingTag.category,
                timestampStartS: floatingTag.startTime,
                timestampEndS: floatingTag.endTime,
                notes: floatingTag.note,
            }
        }));
        if (error) {
            console.error('Error adding tag:', error);
            showToast?.({
                props: {
                    title: `Error adding tag: ${floatingTag.category}`,
                    body: error.message,
                    value: 2500,
                    variant: 'danger',
                    pos: 'top-end',

                }
            });
            return;
        }
        if (response && response.tag) {
            floatingTag.id = response.tag.id?.toString() ?? floatingTag.id;


            showToast?.({
                props: {
                    title: `Tag added: ${floatingTag.category}`,
                    body: `Tag ${floatingTag.category} has been added.`,
                    value: 2500,
                    variant: 'success',
                    pos: 'top-end',

                }
            });
        } else {
            console.warn('No tag found or unexpected response structure.');
        }



    } else {
        console.warn("No floating tag found for category:", category);
    }
    // redraw the chart
    chartOption.value = createChartOption();
};




const selectedTag = ref<TagViewModel | null>(null);

// This object tracks whatever the user types in the "edit" form
const formData = reactive({
    start: 0,
    end: 0,
    category: '',
    note: '',
});

const setFormData = (label: TagViewModel) => {
    formData.start = label.startTime;
    formData.end = label.endTime;
    formData.category = label.category;
    formData.note = label.note ?? '';
}

const handleOnChartClick = (params: any) => {
    console.log("Clicked on chart:", params);
    if (params.componentType === 'series' && params.componentSubType === 'custom') {
        // Identify the clicked label

        const labelId = params.value[3] as string;


        // Find the label in your `labels` array
        const found = availableTags.value.find(l => l.id === labelId);
        if (found) {
            selectedTag.value = { ...found };
            setFormData(found);
        }
    }

    // else if(params.componentType === 'markLine') {
    //     seekTo( params.value); // Seek to the clicked time in the video
    // }

    else {
        // Clicked somewhere else, optionally clear active label
        // activeLabel.value = null;
    }
}

const saveTag = async () => {
    if (selectedTag.value) {
        const index = availableTags.value.findIndex(l => l.id === selectedTag.value?.id);
        if (index !== -1) {

            const [error, response] = await safeFetch(() => client.updateTagApiV1TagUpdateIdPut({
                id: availableTags.value[index].id,
                updateTagPayload: {
                    category: formData.category,
                    timestampStartS: formData.start,
                    timestampEndS: formData.end,
                    notes: formData.note,
                }
            }));

            if (error) {
                console.error('Error updating tag:', error);
                showToast?.({
                    props: {
                        title: `Error updating tag: ${formData.category}`,
                        body: error.message,
                        value: 2500,
                        variant: 'danger',
                        pos: 'top-end',

                    }
                });
            }
            else if (response && response.tag) {
                availableTags.value[index].id = response.tag.id?.toString() ?? availableTags.value[index].id;
                availableTags.value[index].startTime = formData.start;
                availableTags.value[index].endTime = formData.end;
                availableTags.value[index].category = formData.category;


                showToast?.({
                    props: {
                        title: `Tag updated: ${formData.category}`,
                        body: `Tag ${formData.category} has been updated.`,
                        value: 2500,
                        variant: 'success',
                        pos: 'top-end',

                    }
                });
            } else {
                console.warn('No tag found or unexpected response structure.');
            }

        }


        chartOption.value = createChartOption();
    }
}

const deleteTag = async () => {
    if (selectedTag.value) {
        const index = availableTags.value.findIndex(l => l.id === selectedTag.value?.id);
        if (index !== -1) {
            // availableTags.value.splice(index, 1);

            const [error, response] = await safeFetch(() => client.deleteTagApiV1TagDeleteIdDelete({
                id: availableTags.value[index].id
            }));
            if (error) {
                console.error('Error deleting tag:', error);
                showToast?.({
                    props: {
                        title: `Error deleting tag: ${selectedTag.value.category}`,
                        body: error.message,
                        value: 2500,
                        variant: 'danger',
                        pos: 'top-end',

                    }
                });
            } else if (response && response.success) {
                availableTags.value.splice(index, 1);
                showToast?.({
                    props: {
                        title: `Tag deleted: ${selectedTag.value.category} (${selectedTag.value.startTime}s - ${selectedTag.value.endTime}s)`,
                        body: `Tag ${selectedTag.value.category} has been deleted.`,
                        value: 2500,
                        variant: 'success',
                        pos: 'top-end',

                    }
                });
            } else {
                console.warn('No tag found or unexpected response structure.');
            }
        }
    }

    chartOption.value = createChartOption();
}

const onCancelEditLabel = () => {

    selectedTag.value = null;
    setFormData({ id: '', category: '', startTime: 0, endTime: 0, note: '', isFloating: false });
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
            id: tag.id?.toString() ?? '',
            category: tag.category,
            startTime: tag.timestampStartS,
            endTime: tag.timestampEndS,
            note: tag.notes,
            isFloating: false
        })) as TagViewModel[]; // Cast to TimeLabel type

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
    chartOption.value = createChartOption();

    subscription = simulationTimeObservable.subscribe((time) => {
        currentSimulationTime.value = time;
        // update all floating tags to the current time
        let chartNeedsUpdate = false;
        availableTags.value.forEach((tag) => {
            if (tag.isFloating) {
                tag.endTime = time;
                chartNeedsUpdate = true;
            }
        });
        // update the chart if any floating tags were updated
        if (chartNeedsUpdate) {
            chartOption.value = createChartOption();
        }
    });
});

onUnmounted(() => {
    subscription?.unsubscribe();
});


</script>

<style scoped>
/* Styles extracted from inline style attributes */
.full-size-container {
    width: 100%;
    height: 100%;
}

.input-max-width-250 {
    max-width: 250px;
}

.full-height {
    height: 100%;
}

.category-button {
    /* Static styles extracted from the dynamic :style binding */
    border: none;
    color: #fff;
    /* Background color remains dynamic via :style */
    transition: opacity 0.3s ease;
    /* Optional: Smoother transition if animation stops */
}

/* Define the animation */
@keyframes pulse-opacity {
    0% {
        opacity: 1;
    }

    50% {
        opacity: 0.6;
    }

    /* Adjust opacity for desired effect */
    100% {
        opacity: 1;
    }
}

/* Apply the animation to the button when the class is present */
.category-button.is-recording {
    animation: pulse-opacity 1.5s ease-in-out infinite;
    /* Adjust duration/timing as needed */
}

.chart-dimensions {
    /* Extracted from :style binding as values were static */
    width: 100%;
    height: 80%;
}

.input-width-100 {
    width: 100px;
}

.select-width-150 {
    width: 150px;
}

.input-width-250 {
    width: 250px;
}

/* Add fade transition styles if they weren't defined elsewhere */
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>