<template>
    <div style="{width : 100%}" class="d-flex flex-row justify-content-start align-items-center">

        <BDropdown text="Add Plugin" class="me-2">
            <BDropdownItem @click="handleAddVideo">Add Video</BDropdownItem>
            <BDropdownItem @click="handleAddGauge">Add Gauge</BDropdownItem>
            <BDropdownItem @click="handleAddScatter">Add Chart</BDropdownItem>
            <BDropdownItem @click="handleAddList">Add List</BDropdownItem>
            <BDropdownItem @click="handleAddTagLine">Add Tag Line</BDropdownItem>
            <BDropdownDivider />
            <BDropdownItem @click="handleAddTestGridItem">Add Test</BDropdownItem>

        </BDropdown>


        <BDropdown text="Layout" class="me-2">

            <BDropdownItem @click="openSaveLayoutModal">Save Current Layout</BDropdownItem>
            <!-- <BDropdownItem @click="openRenameLayoutModal">Rename Layout</BDropdownItem> -->
            <BDropdownDivider />


            <li>
                <h6 class="dropdown-header">Stored Layouts</h6>
            </li>


            <BDropdownItem v-for="layout in availableLayouts" :key="layout">
                <span @click="handleRestoreLayout(layout)" style="cursor: pointer;">{{ layout }}</span>
                <div>
                    <BButton size="sm" variant="outline-primary" class="me-1" @click="handleRestoreLayout(layout)">
                        <!-- <font-awesome-icon icon="play-fill" /> -->
                        Activate
                    </BButton>

                    <BButton size="sm" variant="outline-secondary" @click="openRenameLayoutModal(layout)">
                        <!-- <font-awesome-icon icon="pencil" /> -->
                        Rename
                    </BButton>

                    <BButton size="sm" variant="outline-danger" @click="handleDeleteLayout(layout)">
                        <!-- <font-awesome-icon icon="trash" /> -->
                        Delete
                    </BButton>


                </div>
            </BDropdownItem>



            <BModal v-model="showSaveLayoutModal" title="Save Layout"
                @ok="handleSaveLayout(newLayoutName, overwriteLayoutName)">
                <div class="mb-3">
                    <label for="layoutName" class="form-label">Layout Name:</label>
                    <BFormInput id="layoutName" v-model="newLayoutName" placeholder="Enter layout name"></BFormInput>
                </div>
                <div v-if="availableLayouts.length > 0">
                    <label for="overwriteLayout" class="form-label">Overwrite Existing Layout (Optional):</label>
                    <BFormSelect id="overwriteLayout" v-model="overwriteLayoutName">
                        <option :value="null">-- Select Layout to Overwrite --</option>
                        <option v-for="layout in availableLayouts" :key="layout">{{ layout }}
                        </option>
                    </BFormSelect>
                </div>
            </BModal>

            <BModal v-model="showRenameLayoutModal" title="Rename Layout" @ok="handleRenameSelectedLayout">
                <div v-if="selectedLayoutToRename">
                    <div class="mb-3">
                        <label for="renameLayoutName" class="form-label">New Layout Name for "{{ selectedLayoutToRename
                            }}":</label>
                        <BFormInput id="renameLayoutName" v-model="renameLayoutName" placeholder="Enter new name">
                        </BFormInput>
                    </div>
                </div>
                <div v-else>
                    <p>Please select a layout to rename from the dropdown.</p>
                </div>
            </BModal>
        </BDropdown>

    </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { useProjectStore } from './../../stores/projectStore';
import { Observable } from '../../observable';
import { ApiDataManager } from './../../managers/apiDataManager';
import gridItemManager from './../../managers/gridItemManager';
import layoutManager, { StoredLayoutItem } from './../../managers/layoutManager';

const simulationTimeObservable = new Observable<number>(0);


const projectStore = useProjectStore();


const availableLayouts = ref<string[]>([]);
const newLayoutName = ref<string>('');
const overwriteLayoutName = ref<string | null>(null);


const renameLayoutName = ref<string>('');
const selectedLayoutToRename = ref<string | null>(null);

const showSaveLayoutModal = ref(false);
const showRenameLayoutModal = ref(false);



const layoutsData = ref<Record<string, StoredLayoutItem[]>>({});
let subscription: { unsubscribe: () => void } | null = null;



const handleAddTagLine = () => {
    gridItemManager.addNewItem({
        component: 'TagTimeline',
        x: 0,
        y: 0,
        w: 6,
        h: 7,
        noMove: true,
        id: 'tag-timeline',
        title: 'Tag Timeline',
        props: {
            // simulationTimeObservable
        },
        dependencies: {
            simulationTimeObservable
        }
    });
};



const handleAddVideo = () => {


    gridItemManager.addNewItem({
        component: 'VideoPlayer',
        x: 3,
        y: 0,
        w: 6,
        h: 7,
        noMove: true,
        id: 'video-player',
        title: 'Video Player',
        props: {
            videoInfo: projectStore.loadedProject?.testDriveVideoInfo || {},
            // simulationTimeObservable
        },
        dependencies: {
            simulationTimeObservable
        }
    });
};



const handleAddGauge = () => {
    const dataManager = new ApiDataManager();
    dataManager.subscribeToTimestamp(simulationTimeObservable);
    gridItemManager.addNewItem({
        component: 'Gauge',
        x: 0,
        y: 0,
        w: 3,
        h: 5,
        noMove: true,
        id: 'gauge-' + crypto.randomUUID(),
        title: '',
        props: {
        },
        dependencies: {
            dataManager
        }
    });
};

const handleAddList = () => {
    const dataManager = new ApiDataManager();
    dataManager.subscribeToTimestamp(simulationTimeObservable);
    gridItemManager.addNewItem({
        component: 'ListView',
        x: 0,
        y: 0,
        w: 3,
        h: 5,
        noMove: true,
        id: 'list-' + crypto.randomUUID(),
        title: '',
        props: {
        },
        dependencies: {
            dataManager
        }
    });
};


const handleAddScatter = () => {
    const dataManager = new ApiDataManager();
    dataManager.subscribeToTimestamp(simulationTimeObservable);
    gridItemManager.addNewItem({
        component: 'ScatterPlot',
        x: 0,
        y: 0,
        w: 7,
        h: 4,
        noMove: true,
        id: 'scatter-' + crypto.randomUUID(),
        title: '',
        props: {
        },
        dependencies: {
            dataManager
        }
    });
};

const handleAddTestGridItem = () => {
    const { x, y } = gridItemManager.suggestFreeSpace(5, 4);

    gridItemManager.addNewItem({
        component: 'TestGridItem',
        x: x,
        y: y,
        w: 5,
        h: 4,
        noMove: true,
        id: 'test-grid-item' + crypto.randomUUID(),
        title: 'Test Grid Item',
        props: {
        }
    });
};


onMounted(async () => {
    // Fetch the initial layout data when the component is mounted
    availableLayouts.value = layoutManager.getLayoutNames();
    subscription = layoutManager.layouts$.subscribe((layouts) => {
        layoutsData.value = layouts;
        availableLayouts.value = Object.keys(layouts);
    });
});



const openSaveLayoutModal = () => {
    newLayoutName.value = '';
    overwriteLayoutName.value = null;
    showSaveLayoutModal.value = true;
}


const openRenameLayoutModal = (selectedLayoutName: string) => {
    renameLayoutName.value = '';
    selectedLayoutToRename.value = selectedLayoutName;
    showRenameLayoutModal.value = true;
}




const handleSaveLayout = (newLayoutName: string | null, updateLayoutName: string | null) => {
    const getNextAvailableLayoutName = (existingNames: string[]): string => {
        let index = 1;
        while (existingNames.includes(`Layout ${index}`)) {
            index++;
        }
        return `Layout ${index}`;
    }

    const existingNames = Object.keys(layoutManager.getLayoutNames());
    const defaultLayoutName = getNextAvailableLayoutName(existingNames);

    const layoutName = newLayoutName || updateLayoutName || defaultLayoutName;
    const items = gridItemManager.getGridItems().map(item => ({ ...item }));
    layoutManager.saveLayout(layoutName, items);
};


const handleRestoreLayout = (layoutName: string) => {

    gridItemManager.removeAllItems();

    const layoutToRestore = layoutManager.getLayout(layoutName);
    if (!layoutToRestore) {
        console.error(`Layout "${layoutName}" not found.`);
        return;
    }

    for (const item of layoutToRestore) {



        let componentProps: any = {
            pluginState: item.pluginState,
        };

        let componentDependencies: any = {};

        if (item.component === 'VideoPlayer') {
            componentProps.videoInfo = projectStore.loadedProject?.testDriveVideoInfo || {};
            componentDependencies.simulationTimeObservable = simulationTimeObservable;
        } else {

            const dataManager = new ApiDataManager();

            dataManager.subscribeToTimestamp(simulationTimeObservable);
            componentDependencies.dataManager = dataManager;
        }



        gridItemManager.addNewItem({
            component: item.component,
            x: item.x,
            y: item.y,
            w: item.w,
            h: item.h,
            noMove: true,
            id: item.id,
            title: item.title,
            props: componentProps,
            dependencies: componentDependencies
        });


    }
};

const handleDeleteLayout = (layoutName: string) => {
    layoutManager.removeLayout(layoutName);
    availableLayouts.value = layoutManager.getLayoutNames();
};

const handleRenameSelectedLayout = () => {
    if (selectedLayoutToRename.value && renameLayoutName.value) {
        layoutManager.renameLayout(selectedLayoutToRename.value, renameLayoutName.value);
        selectedLayoutToRename.value = null;
        renameLayoutName.value = '';
        showRenameLayoutModal.value = false;
    }
};

</script>

<style scoped>
/* Optional: Add any component-specific styles here */
</style>