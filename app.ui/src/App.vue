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
                <aside class="col-2 bg-light  mt-3 border-start d-flex flex-column">
                    <h5>Tags</h5>
                    <ul class="list-unstyled">
                        <li><a href="#">Link A</a></li>
                        <li><a href="#">Link B</a></li>
                        <li><a href="#">Link C</a></li>
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
import { onMounted, markRaw } from 'vue';
import { getProjectStore } from './stores/projectStore';
import { useGridStore } from './stores/gridStore';

import LeftSideBar from './components/LeftSideBar.vue';
import VideoPlayer from './components/VideoPlayer.vue';
import MainGrid from './components/MainGrid.vue';

// Initialize the store
const projectStore = getProjectStore();
const gridStore = useGridStore();

onMounted(async () => {
    await projectStore.initializeStore();

    gridStore.setComponentMap({
        VideoPlayer: markRaw(VideoPlayer),
    });

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
