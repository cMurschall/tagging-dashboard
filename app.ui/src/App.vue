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
                <aside class="col-md-2 col-sm-3 bg-light p-3 border-end d-flex flex-column">
                    <LeftSideBar />
                </aside>

                <!-- Main Content -->
                <main class="col-md-8 col-sm-6 p-3 d-flex flex-column">
                    <h2>Is Project loaded; {{ projectStore.isProjectLoaded }}</h2>
                    <VideoPlayer
                     v-if="projectStore.isProjectLoaded"
                     :videoSource="projectStore.loadedProject?.videoPath" 
                     :thumbnailSource="projectStore.loadedProject?.videoSpritePath"/>

                </main>

                <!-- Right Sidebar -->
                <aside class="col-md-2 col-sm-3 bg-light p-3 border-start d-flex flex-column">
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
import { onMounted } from 'vue';
import { getProjectStore } from './stores/projectStore';
import LeftSideBar from './components/LeftSideBar.vue';
import VideoPlayer from './components/VideoPlayer.vue';

// Initialize the store
const projectStore = getProjectStore();

onMounted(async () => {
    await projectStore.initializeStore();
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
</style>
