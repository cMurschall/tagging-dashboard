<template>
    <div id="app" class="d-flex flex-column min-vh-100">
        <BToastOrchestrator />
        <!-- Header -->
        <header :class="['text-white p-2 d-flex justify-content-between align-items-center', headerClass]">
            <h1 class="mb-0 text-center flex-grow-1">Tagging Dashboard</h1>
            <div class="health-status text-end ms-3">
                <template v-if="healthCheckResult">
                    <div v-if="healthCheckResult.status === 'success'" class="small">
                        <div class="health-grid">
                            <div><strong>Status:</strong></div>
                            <div class="text-end">{{ (healthCheckResult.message as HealthCheckResponse).status }}</div>

                            <div><strong>Uptime:</strong></div>
                            <div class="text-end">{{ formatUptime((healthCheckResult.message as
                                HealthCheckResponse).uptime) }}</div>

                            <div><strong>Memory:</strong></div>
                            <div class="text-end">{{ ((healthCheckResult.message as
                                HealthCheckResponse).memoryUsage) }} MB</div>

                            <div><strong>CPU:</strong></div>
                            <div class="text-end">{{ formatPercent((healthCheckResult.message as
                                HealthCheckResponse).cpuUsage) }}</div>
                        </div>
                    </div>
                    <div v-else class="fs-6 fw-bold small text-white">
                        <strong>Error:</strong> {{ friendlyErrorMessage }}
                    </div>
                </template>
                <template v-else>
                    <div class="small">Loading health status...</div>
                </template>
            </div>
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
            </div>
        </div>

        <!-- Footer -->
        <footer class="bg-dark text-white text-center p-1">
            <p>© 2025 Christian Murschall</p>
        </footer>
    </div>
</template>

<script setup lang="ts">
import { onMounted, ref, onUnmounted, watch, toRaw, computed } from 'vue';
import { useProjectStore } from './stores/projectStore';

import ToolBar from './components/menu/ToolBar.vue';
import LeftSideBar from './components/LeftSideBar.vue';
import MainGrid from './components/MainGrid.vue';


import { GridManagerItem } from './managers/gridItemManager';
import { getLayoutManager } from './managers/layoutManager';
import { EmptySubscription, Subscription } from './core/observable';
import { BToastOrchestrator, useToastController } from 'bootstrap-vue-next';
import { getPluginManager } from './managers/pluginManager';
import { TestDriveProjectInfo, HealthApiClient as client, safeFetch } from './core/utilities/utilities';
import { HealthCheckResponse } from '../services/restclient';


const { show: showToast } = useToastController();

const mainGrid = ref<typeof MainGrid | null>(null);


// Initialize the store
const projectStore = useProjectStore();


const availableLayouts = ref<string[]>([]);
const layoutsData = ref<Record<string, GridManagerItem[]>>({});
let subscription: Subscription = EmptySubscription;

watch(() => projectStore.loadedProject, (newProject) => {
    if (!newProject) {
        getPluginManager().setCurrentProject(undefined);
        return;
    }
    const rawProject = toRaw(newProject);
    const clonedProject = JSON.parse(JSON.stringify(rawProject)) as TestDriveProjectInfo;
    getPluginManager().setCurrentProject(clonedProject);
}, { immediate: true });


let heatbeatInterval: NodeJS.Timeout | null = null;

const healthCheckResult = ref<{ status: string, message: string | HealthCheckResponse } | null>(null);

const headerClass = computed(() =>
    healthCheckResult.value?.status === 'error' ? 'bg-danger' : 'bg-primary'
);

const friendlyErrorMessage = computed(() => {
    const raw = healthCheckResult.value?.message ?? '';
    if (typeof raw !== 'string') return 'Unknown error';
    if (raw.includes('interceptors')) return 'Server is unavailable or unresponsive';
    return raw;
});

const formatUptime = (raw: string): string => {
    // Split into parts
    const [hStr, mStr, sStr] = raw.split(':');
    const hours = parseInt(hStr, 10);
    const minutes = parseInt(mStr, 10);

    const totalMinutes = hours * 60 + minutes;
    const days = Math.floor(totalMinutes / 1440); // 1440 minutes in a day
    const remainingMinutes = totalMinutes % 1440;
    const finalHours = Math.floor(remainingMinutes / 60);
    const finalMinutes = remainingMinutes % 60;

    const parts: string[] = [];
    if (days > 0) parts.push(`${days}d`);
    if (finalHours > 0) parts.push(`${finalHours}h`);
    if (finalMinutes > 0 || parts.length === 0) parts.push(`${finalMinutes}m`);

    return parts.join(' ');
}


const formatPercent = (value: number): string => {
    return `${(value).toFixed(1)}%`;
}

onMounted(async () => {

    await projectStore.initializeStore();
    subscription = getLayoutManager().layouts$.subscribe((layouts) => {
        layoutsData.value = layouts;
        availableLayouts.value = Object.keys(layouts);
    });
    getPluginManager().setShowToast(showToast);


    heatbeatInterval = setInterval(async () => {

        const [error, result] = await safeFetch(() => client.healthcheckApiHealthcheckGet());
        if (error) {
            console.error('Error fetching health check:', error);
            healthCheckResult.value = { status: 'error', message: error.message };
            return;
        }
        if (result) {
            healthCheckResult.value = { status: 'success', message: result };
        }

    }, 5000);
});



onUnmounted(() => {
    subscription.unsubscribe();

    if (heatbeatInterval) {
        clearInterval(heatbeatInterval);
        heatbeatInterval = null;
    }
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

.health-grid {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 0.1rem 0.5rem;
}

.health-status {
    min-width: 250px;
    font-size: 0.8rem;
    line-height: 1.2;
}
</style>
