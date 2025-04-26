<template>
    <div style="width : 100%" class="d-flex flex-row justify-content-start align-items-center">
        <BDropdown text="Add Plugin" class="me-2" :disable="projectStore.isProjectLoaded">
            <BDropdownGroup header="Build in">

                <BDropdownItem v-for="plugin in internalPlugins" :key="plugin.name"
                    :disabled="!projectStore.isProjectLoaded" @click="handleInternalPlugin(plugin)">Add {{ plugin.displayName
                    }}</BDropdownItem>
            </BDropdownGroup>

            <BDropdownGroup header="Externals" v-if="externalPlugins.length > 0">
                <BDropdownItem v-for="plugin in externalPlugins" :key="plugin.id"
                    :disabled="!projectStore.isProjectLoaded" @click="handleExternalPlugin(plugin)">Add {{ plugin.name
                    }}</BDropdownItem>
            </BDropdownGroup>


            <BDropdownGroup header="For testing">
                <BDropdownItem @click="handleAddTestGridItem">Add Test</BDropdownItem>
            </BDropdownGroup>


        </BDropdown>


        <BDropdown text="Layout" class="me-2">

            <BDropdownItem :disabled="!projectStore.isProjectLoaded" @click="openSaveLayoutModal">Save Current Layout
            </BDropdownItem>
            <!-- <BDropdownItem @click="openRenameLayoutModal">Rename Layout</BDropdownItem> -->
            <BDropdownDivider />


            <li>
                <h6 class="dropdown-header">Stored Layouts</h6>
            </li>


            <BDropdownItem :disabled="!projectStore.isProjectLoaded" v-for="layout in availableLayouts" :key="layout">
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



        <div class="ms-auto text-end pe-2">
            <div class="fw-semibold text-muted">Simulation time</div>
            <div class="fs-5">{{ currentSimulationTimeSecond.toFixed(2) }}s</div>
        </div>

    </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

import { EmptySubscription, Subscription } from '../../observable';
import { getGridManager } from './../../managers/gridItemManager';
import { getLayoutManager, StoredLayoutItem } from './../../managers/layoutManager';

import { ExternalPluginManifest, InternalPluginManifest, getPluginManager } from '../../managers/pluginManager';
import { useProjectStore } from './../../stores/projectStore';
import { BModal, BFormInput, BFormSelect, BButton, BDropdown, BDropdownItem, BDropdownDivider, BDropdownGroup } from 'bootstrap-vue-next';

// Initialize the store
const projectStore = useProjectStore();

const currentSimulationTimeSecond = ref(0);


const availableLayouts = ref<string[]>([]);
const newLayoutName = ref<string>('');
const overwriteLayoutName = ref<string | null>(null);


const renameLayoutName = ref<string>('');
const selectedLayoutToRename = ref<string | null>(null);

const showSaveLayoutModal = ref(false);
const showRenameLayoutModal = ref(false);



const layoutsData = ref<Record<string, StoredLayoutItem[]>>({});
let layoutSubscription: Subscription = EmptySubscription;
let simulationTimeSubscription: Subscription = EmptySubscription;

const externalPlugins = ref<ExternalPluginManifest[]>([]);
const internalPlugins = ref<InternalPluginManifest[]>([]);




const handleAddTestGridItem = () => {
    getPluginManager().showPlugin('TestGridItem', {});
};

const handleExternalPlugin = (plugin: ExternalPluginManifest) => {
    getPluginManager().showPlugin(plugin.id, {});
};

const handleInternalPlugin = (plugin: InternalPluginManifest) => {
    getPluginManager().showPlugin(plugin.name, {});
};



onMounted(async () => {
    // Fetch the initial layout data when the component is mounted
    availableLayouts.value = getLayoutManager().getLayoutNames();
    layoutSubscription = getLayoutManager().layouts$.subscribe((layouts) => {
        layoutsData.value = layouts;
        availableLayouts.value = Object.keys(layouts);
    });

    simulationTimeSubscription = getPluginManager().simulationTimeObservable.subscribe((time) => {
        currentSimulationTimeSecond.value = time;
    });

    externalPlugins.value = getPluginManager().getExternalPlugins();
    internalPlugins.value = getPluginManager().getInternalPlugins();

});

onUnmounted(() => {
    // Clean up subscriptions when the component is unmounted
    layoutSubscription.unsubscribe();
    simulationTimeSubscription.unsubscribe();
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

    const existingNames = Object.keys(getLayoutManager().getLayoutNames());
    const defaultLayoutName = getNextAvailableLayoutName(existingNames);

    const layoutName = newLayoutName || updateLayoutName || defaultLayoutName;
    const items = getGridManager().getGridItems().map(item => ({ ...item }));
    getLayoutManager().saveLayout(layoutName, items);
};


const handleRestoreLayout = (layoutName: string) => {

    getGridManager().removeAllItems();

    const layoutToRestore = getLayoutManager().getLayout(layoutName);
    if (!layoutToRestore) {
        console.error(`Layout "${layoutName}" not found.`);
        return;
    }

    for (const item of layoutToRestore) {

        getPluginManager().restorePlugin({
            component: item.component,
            x: item.x,
            y: item.y,
            w: item.w,
            h: item.h,
            id: item.id,
            title: item.title,
        }, item.pluginState);
    }
};

const handleDeleteLayout = (layoutName: string) => {
    getLayoutManager().removeLayout(layoutName);
    availableLayouts.value = getLayoutManager().getLayoutNames();
};

const handleRenameSelectedLayout = () => {
    if (selectedLayoutToRename.value && renameLayoutName.value) {
        getLayoutManager().renameLayout(selectedLayoutToRename.value, renameLayoutName.value);
        selectedLayoutToRename.value = null;
        renameLayoutName.value = '';
        showRenameLayoutModal.value = false;
    }
};

</script>

<style scoped>
/* Optional: Add any component-specific styles here */
</style>