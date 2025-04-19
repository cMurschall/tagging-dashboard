<template>
    <div id="app" class="d-flex flex-column min-vh-100">
        <BToastOrchestrator />
        <!-- Header -->
        <header class="bg-primary text-white p-2">
            <h1 class="text-center">Tagging Dashboard</h1>
        </header>

        <!-- Main Layout -->
        <div class="container-fluid flex-grow-1 d-flex">
            <div class="row flex-grow-1 w-100 align-items-stretch">
                <!-- Left Sidebar -->
                <aside class="col-2 bg-light mt-3 border-end d-flex flex-column" style="overflow-y: auto;">
                    <LeftSideBar />
                </aside>

                <!-- Main Content -->
                <main class="col-10  d-flex flex-column mb-4">

                    <!-- Toolbar -->
                    <div class="toolbar d-flex align-items-center justify-content-start p-2 bg-light border-bottom">
                        <ToolBar />
                    </div>

                    <!-- Main Grid -->
                    <MainGrid ref="mainGrid" class="flex-grow-1" />
                </main>
                <!-- Right Sidebar -->
                <aside v-if="false" class="col-2 bg-light mt-3 border-start d-flex flex-column"
                    style="overflow-y: auto;">
                    <h5>Tags</h5>
                    <ul class="list-unstyled">
                        <!-- Singuläre Ereignisse -->
                        <li><button class="btn btn-outline-primary btn-sm w-100 mb-1">Gefahrenbremsung</button></li>
                        <li><button class="btn btn-outline-primary btn-sm w-100 mb-1">Rotes Licht überfahren</button>
                        </li>
                        <li><button class="btn btn-outline-primary btn-sm w-100 mb-1">Beinahe-Kollision</button></li>
                        <li><button class="btn btn-outline-primary btn-sm w-100 mb-1">Starke Lenkbewegung</button></li>
                        <li><button class="btn btn-outline-primary btn-sm w-100 mb-1">Plötzliches Hindernis</button>
                        </li>

                        <!-- Dauerhafte Ereignisse mit Start- und Stop-Button -->
                        <li class="mb-2">
                            <span class="d-block fw-bold">Überholvorgang</span>
                            <div class="d-flex flex-column">
                                <button class="btn btn-outline-success btn-sm w-100 mb-1">Start</button>
                                <button class="btn btn-outline-danger btn-sm w-100">Stop</button>
                            </div>
                        </li>
                        <li class="mb-2">
                            <span class="d-block fw-bold">Verlassen der Fahrspur</span>
                            <div class="d-flex flex-column">
                                <button class="btn btn-outline-success btn-sm w-100 mb-1">Start</button>
                                <button class="btn btn-outline-danger btn-sm w-100">Stop</button>
                            </div>
                        </li>
                        <li class="mb-2">
                            <span class="d-block fw-bold">Handy-Nutzung</span>
                            <div class="d-flex flex-column">
                                <button class="btn btn-outline-success btn-sm w-100 mb-1">Start</button>
                                <button class="btn btn-outline-danger btn-sm w-100">Stop</button>
                            </div>
                        </li>
                        <li class="mb-2">
                            <span class="d-block fw-bold">Unaufmerksamkeit</span>
                            <div class="d-flex flex-column">
                                <button class="btn btn-outline-success btn-sm w-100 mb-1">Start</button>
                                <button class="btn btn-outline-danger btn-sm w-100">Stop</button>
                            </div>
                        </li>
                        <li class="mb-2">
                            <span class="d-block fw-bold">Fehlgeschlagener Spurwechsel</span>
                            <div class="d-flex flex-column">
                                <button class="btn btn-outline-success btn-sm w-100 mb-1">Start</button>
                                <button class="btn btn-outline-danger btn-sm w-100">Stop</button>
                            </div>
                        </li>
                        <li class="mb-2">
                            <span class="d-block fw-bold">Überhöhte Geschwindigkeit</span>
                            <div class="d-flex flex-column">
                                <button class="btn btn-outline-success btn-sm w-100 mb-1">Start</button>
                                <button class="btn btn-outline-danger btn-sm w-100">Stop</button>
                            </div>
                        </li>
                        <li class="mb-2">
                            <span class="d-block fw-bold">Straßenglätte erkannt</span>
                            <div class="d-flex flex-column">
                                <button class="btn btn-outline-success btn-sm w-100 mb-1">Start</button>
                                <button class="btn btn-outline-danger btn-sm w-100">Stop</button>
                            </div>
                        </li>
                        <li class="mb-2">
                            <span class="d-block fw-bold">Tunnelsituation</span>
                            <div class="d-flex flex-column">
                                <button class="btn btn-outline-success btn-sm w-100 mb-1">Start</button>
                                <button class="btn btn-outline-danger btn-sm w-100">Stop</button>
                            </div>
                        </li>
                        <li class="mb-2">
                            <span class="d-block fw-bold">Kurvenfahrt mit hoher Geschwindigkeit</span>
                            <div class="d-flex flex-column">
                                <button class="btn btn-outline-success btn-sm w-100 mb-1">Start</button>
                                <button class="btn btn-outline-danger btn-sm w-100">Stop</button>
                            </div>
                        </li>
                        <li class="mb-2">
                            <span class="d-block fw-bold">Starker Regen oder schlechte Sicht</span>
                            <div class="d-flex flex-column">
                                <button class="btn btn-outline-success btn-sm w-100 mb-1">Start</button>
                                <button class="btn btn-outline-danger btn-sm w-100">Stop</button>
                            </div>
                        </li>
                    </ul>
                </aside>

            </div>
        </div>

        <!-- Footer -->
        <footer class="bg-dark text-white text-center p-1">
            <p>© 2025 Christian Murschall</p>
        </footer>
    </div>
</template>

<script setup lang="ts">
import { onMounted, markRaw, ref, onUnmounted, watch, toRaw } from 'vue';
import { useProjectStore } from './stores/projectStore';

import ToolBar from './components/menu/ToolBar.vue';
import LeftSideBar from './components/LeftSideBar.vue';
import MainGrid from './components/MainGrid.vue';


import VideoPlayer from './components/plugins/VideoPlayer.vue';
import ListView from './components/plugins/ListView.vue';
import Gauge from './components/plugins/Gauge.vue';
import ScatterPlot from './components/plugins/ScatterPlot.vue';
import TestGridItem from './components/plugins/TestGridItem.vue';
import TagTimeline from './components/plugins/TagTimeline.vue';

import gridItemManager, { GridManagerItem } from './managers/gridItemManager';
import layoutManager from './managers/layoutManager';
import { EmptySubscription, Subscription } from './observable';
import { BToastOrchestrator, useToastController } from 'bootstrap-vue-next';
import pluginManager from './managers/pluginManager';
import { TestDriveProjectInfo } from './services/utilities';


const { show: showToast } = useToastController();

const mainGrid = ref<typeof MainGrid | null>(null);


// Initialize the store
const projectStore = useProjectStore();



gridItemManager.setComponentMap({
    ListView: () => markRaw(ListView),
    VideoPlayer: () => markRaw(VideoPlayer),
    Gauge: () => markRaw(Gauge),
    ScatterPlot: () => markRaw(ScatterPlot),
    TestGridItem: () => markRaw(TestGridItem),
    TagTimeline: () => markRaw(TagTimeline),
});

const availableLayouts = ref<string[]>([]);
const layoutsData = ref<Record<string, GridManagerItem[]>>({});
let subscription: Subscription = EmptySubscription;

watch(() => projectStore.loadedProject, (newProject) => {
    if (!newProject) {
        pluginManager.setCurrentProject(undefined);
        return;
    }
    const rawProject = toRaw(newProject);
    const clonedProject = JSON.parse(JSON.stringify(rawProject)) as TestDriveProjectInfo;
    pluginManager.setCurrentProject(clonedProject);
}, { immediate: true });


onMounted(async () => {

    await projectStore.initializeStore();
    subscription = layoutManager.layouts$.subscribe((layouts) => {
        layoutsData.value = layouts;
        availableLayouts.value = Object.keys(layouts);
    });

    pluginManager.setShowToast(showToast);

});



onUnmounted(() => {
    subscription.unsubscribe();
});



</script>

<style scoped>
/* Ensure header and footer stick appropriately while the main content grows */
#app {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    height: 100%;
}

header {
    position: sticky;
    top: 0;

}

footer {
    margin-top: auto;
}

.row {
    height: 100%;
}

aside {
    height: 100%;
}


.main-grid {
    height: 100%;
    border: 10px solid lime;
}
</style>
