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
                    <MainGrid />


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
import { onMounted, markRaw, watch } from 'vue';
import { getProjectStore } from './stores/projectStore';
import { useGridStore } from './stores/gridStore';

import LeftSideBar from './components/LeftSideBar.vue';
import VideoPlayer from './components/VideoPlayer.vue';
import MainGrid from './components/MainGrid.vue';
import { TestDriveVideoInfo } from './services/Utilities';

// Initialize the store
const projectStore = getProjectStore();
const gridStore = useGridStore();

gridStore.setComponentMap({
        VideoPlayer: markRaw(VideoPlayer),
    });



onMounted(async () => {
    await projectStore.initializeStore();

    // gridStore.addNewItem({
    //     component: 'LeftSideBar',
    //     x: 0,
    //     y: 0,
    //     w: 3,
    //     h: 12,
    //     id: 'left-sidebar',
    //     title: 'Left Sidebar'
    // });
});


watch(
    () => projectStore.loadedProject,
    (newProject, oldProject) => {
        console.log('loadedProject changed from', oldProject, 'to', newProject);
        if (newProject) {
            gridStore.addNewItem<{ videoInfo: TestDriveVideoInfo }>({
                component: 'VideoPlayer',
                x: 3,
                y: 0,
                w: 6,
                h: 7,
                id: 'video-player',
                title: 'Video Player',
                props: {
                    videoInfo: projectStore.loadedProject?.testDriveVideoInfo || {}
                }
            });
        } else {
            console.info('The project was unloaded.');
            gridStore.removeItemById('video-player')
        }
    }
);

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
