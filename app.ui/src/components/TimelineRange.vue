<template>
    <div class="timeline-container">
        <div class="timeline-track">
            <div class="timeline-bar data" :style="{ left: dataOffset + '%', width: dataWidth + '%' }">
                <span class="label">Data: {{ formatRange(dataStart, dataEnd) }}</span>
            </div>
        </div>

        <div class="timeline-track mt-1">
            <div class="timeline-bar video" :style="{ left: videoOffset + '%', width: videoWidth + '%' }">
                <span class="label">Video: {{ formatRange(videoStart, videoEnd) }}</span>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue'
import { TestDriveDataInfo, TestDriveVideoInfo } from '../../services/restclient';



const props = defineProps<{
    testDriveDataInfo: TestDriveDataInfo | null
    testDriveVideoInfo: TestDriveVideoInfo | null
}>()

// Default-safe values
const dataStart = computed(() => props.testDriveDataInfo?.dataSimulationTimeStartS ?? 0)
const dataEnd = computed(() => props.testDriveDataInfo?.dataSimulationTimeEndS ?? 0)

const videoStart = computed(() => props.testDriveVideoInfo?.videoSimulationTimeStartS ?? 0)
const videoEnd = computed(() => props.testDriveVideoInfo?.videoSimulationTimeEndS ?? 0)

const fullStart = computed(() => Math.min(dataStart.value, videoStart.value))
const fullEnd = computed(() => Math.max(dataEnd.value, videoEnd.value))
const totalRange = computed(() => fullEnd.value - fullStart.value)

const dataOffset = computed(() => ((dataStart.value - fullStart.value) / totalRange.value) * 100)
const dataWidth = computed(() => ((dataEnd.value - dataStart.value) / totalRange.value) * 100)

const videoOffset = computed(() => ((videoStart.value - fullStart.value) / totalRange.value) * 100)
const videoWidth = computed(() => ((videoEnd.value - videoStart.value) / totalRange.value) * 100)

const formatRange = (start: number, end: number): string => {
    const relativeStart = (start - fullStart.value).toFixed(1)
    const relativeEnd = (end - fullStart.value).toFixed(1)
    return `${relativeStart}s - ${relativeEnd}s`
}
</script>

<style scoped>
.timeline-container {
    width: 100%;
    max-width: 800px;
}

.timeline-track {
    position: relative;
    height: 1.3em;
    background-color: #e9ecef;
    border-radius: 1px;
    overflow: hidden;
}

.timeline-bar {
    position: absolute;
    top: 0;
    bottom: 0;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 6px;
    font-size: 0.85rem;
    color: #fff;
    border-radius: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.timeline-bar.data {
    background-color: #0d6efd;
    /* Bootstrap info */
}

.timeline-bar.video {
    background-color: #198754;
    /* Bootstrap success */
}

.label {
    pointer-events: none;

}
</style>