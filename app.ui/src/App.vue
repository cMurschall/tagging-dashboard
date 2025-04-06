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
                <aside class="col-2 bg-light mt-3 border-end d-flex flex-column">
                    <LeftSideBar />
                </aside>

                <!-- Main Content -->
                <main class="col-8  d-flex flex-column">

                    <!-- Toolbar -->
                    <div class="toolbar d-flex align-items-center justify-content-start p-2 bg-light border-bottom">
                        <ToolBar />
                    </div>

                    <!-- Main Grid -->
                    <MainGrid ref="mainGrid" class="flex-grow-1" />
                </main>

                <!-- Right Sidebar -->
                <aside class="col-2 bg-light mt-3 border-start d-flex flex-column" style="overflow-y: auto;">
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
import { onMounted, markRaw, watch, ref } from 'vue';
import { useProjectStore } from './stores/projectStore';

import ToolBar from './components/menu/ToolBar.vue';
import LeftSideBar from './components/LeftSideBar.vue';
import MainGrid from './components/MainGrid.vue';
import { TestDriveVideoInfo } from './services/utilities';
import { Observable } from './observable';

import VideoPlayer from './components/plugins/VideoPlayer.vue';
import ListView from './components/plugins/ListView.vue';
import Gauge from './components/plugins/Gauge.vue';
import ScatterPlot from './components/plugins/ScatterPlot.vue';
import TestGridItem from './components/TestGridItem.vue';
import gridItemManager, { GridManagerItem } from './managers/gridItemManager';
import layoutManager from './managers/layoutManager';



const mainGrid = ref<typeof MainGrid | null>(null);


// Initialize the store
const projectStore = useProjectStore();






gridItemManager.setComponentMap({
    ListView: () => markRaw(ListView),
    VideoPlayer: () => markRaw(VideoPlayer),
    Gauge: () => markRaw(Gauge),
    ScatterPlot: () => markRaw(ScatterPlot),
    TestGridItem: () => markRaw(TestGridItem)
});

const availableLayouts = ref<string[]>([]);
const layoutsData = ref<Record<string, GridManagerItem[]>>({});
let subscription: { unsubscribe: () => void } | null = null;


onMounted(async () => {
    await projectStore.initializeStore();
    subscription = layoutManager.layouts$.subscribe((layouts) => {
        layoutsData.value = layouts;
        availableLayouts.value = Object.keys(layouts);
    });
});



// watch(
//     () => projectStore.loadedProject,
//     (newProject, oldProject) => {
//         console.log('loadedProject changed from', oldProject, 'to', newProject);
//         if (newProject) {

//             const simulationTimeObservable = new Observable<number>(0);

//             simulationTimeObservable.subscribe((time) => {
//                 // console.log('Simulation time:', time);
//                 projectStore.updateSimulationTime(time);
//             });

//             gridItemManager.addNewItem<{
//                 videoInfo: TestDriveVideoInfo,
//                 simulationTimeObservable: Observable<number>
//             }>({
//                 component: 'VideoPlayer',
//                 x: 3,
//                 y: 0,
//                 w: 6,
//                 h: 7,
//                 id: 'video-player',
//                 title: 'Video Player',
//                 props: {
//                     videoInfo: projectStore.loadedProject?.testDriveVideoInfo || {},
//                     simulationTimeObservable
//                 }
//             });
//         } else {
//             console.info('The project was unloaded.');
//             gridItemManager.removeAllItems();
//         }
//     }
// );

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
