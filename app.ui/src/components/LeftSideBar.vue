<template>
    <div>
        <BButton variant="success" @click="showNewProjectModal = !showNewProjectModal">Create new project</BButton>

        <BModal v-model="showNewProjectModal" title="Create New Project"   :footer="false">
            <div>
                <!-- File Mode Switch -->
                <BFormGroup label="Select file input mode:">
                    <BFormRadioGroup v-model="fileInputMode" buttons button-variant="outline-primary" size="sm">
                        <BFormRadio value="use_existing">Use existing files</BFormRadio>
                        <BFormRadio value="upload_new">Upload new files</BFormRadio>
                    </BFormRadioGroup>
                </BFormGroup>





                <!-- CSV File -->
                <BFormGroup label="CSV File">
                    <template v-if="fileInputMode === 'use_existing'">
                        <BFormSelect v-model="newProjectPayload.csvFileName" :options="projectStore.availableCsvValues">
                        </BFormSelect>
                    </template>
                    <template v-else>
                        <BFormFile v-model="newCsvFile" accept=".csv" required></BFormFile>
                        <BProgress :value="csvUploadProgress" max="100" class="mb-2"
                            v-if="isUploading && csvUploadProgress > 0">
                            <BProgressBar :value="csvUploadProgress">{{ csvUploadProgress }}%</BProgressBar>
                        </BProgress>
                    </template>
                </BFormGroup>

                <!-- Video File -->
                <BFormGroup label="Video File">
                    <template v-if="fileInputMode === 'use_existing'">
                        <b-form-select v-model="newProjectPayload.videoFileName"
                            :options="projectStore.availableVideoValues"></b-form-select>
                    </template>
                    <template v-else>
                        <BFormFile v-model="newVideoFile" accept="video/*" required></BFormFile>
                        <BProgress :value="videoUploadProgress" max="100" class="mb-3"
                            v-if="isUploading && videoUploadProgress > 0">
                            <BProgressBar :value="videoUploadProgress">{{ videoUploadProgress }}%</BProgressBar>
                        </BProgress>

                    </template>
                </BFormGroup>

                <!-- Meta Inputs -->

                <!-- Driver Name -->
                <BFormGroup label="Driver Name" label-for="driver-name">
                    <BFormInput id="driver-name" v-model="newProjectPayload.driverName" required
                        placeholder="Enter driver's name">
                    </BFormInput>
                </BFormGroup>

                <!-- Vehicle ID -->
                <BFormGroup label="Vehicle ID" label-for="vehicle-id">
                    <BFormInput id="vehicle-id" v-model="newProjectPayload.vehicleName" required
                        placeholder="Enter vehicle ID">
                    </BFormInput>
                </BFormGroup>

                <!-- Route Name -->
                <BFormGroup label="Route Name" label-for="route-name">
                    <BFormInput id="route-name" v-model="newProjectPayload.routeName" required
                        placeholder="Enter route name">
                    </BFormInput>
                </BFormGroup>

                <!-- Notes -->
                <BFormGroup label="Notes" label-for="notes">
                    <BFormTextarea id="notes" v-model="newProjectPayload.notes"
                        placeholder="Enter additional notes (optional)">
                    </BFormTextarea>
                </BFormGroup>



            </div>
            <template #footer>
                <BButton variant="secondary" @click="showNewProjectModal = false">Cancel</BButton>
                <BButton variant="primary" :disabled="isUploading" @click="handleCreateProject">
                    <span v-if="isUploading">
                        <b-spinner small type="grow" class="me-2" /> Uploading...
                    </span>
                    <span v-else>
                        Create
                    </span>
                </BButton>
            </template>
        </BModal>

        <div v-if="projectStore.isProjectLoaded">
            <BCard class="my-3">
                <BCardHeader class="d-flex justify-content-between align-items-center">
                    <h4 class="mb-0">Loaded Project</h4>
                    <BButton variant="danger" size="sm" @click="handleUnloadProject">
                        <i class="bi bi-x-circle me-1"></i> Unload
                    </BButton>

                </BCardHeader>
                <BCardBody v-if="projectStore.loadedProject?.isLive">
                    <BListGroup flush>
                        <BListGroupItem>
                            <strong>Live Streaming</strong><br>
                        </BListGroupItem>
                        <BListGroupItem v-if="projectStore.loadedProject?.testDriveDataInfo?.csvFileName">
                            <strong>Data file:</strong><br>
                            <BButton size="sm" variant="outline-secondary" class="ml-2"
                                @click="copyToClipboard(projectStore.loadedProject?.testDriveDataInfo?.csvFileFullPath)">
                                📋
                            </BButton>
                            {{ projectStore.loadedProject?.testDriveDataInfo?.csvFileName }}

                        </BListGroupItem>
                        <BListGroupItem v-if="projectStore.loadedProject?.testDriveVideoInfo?.videoFileName">
                            <strong>Video file:</strong><br>
                            <BButton size="sm" variant="outline-secondary" class="ml-2"
                                @click="copyToClipboard(projectStore.loadedProject?.testDriveVideoInfo?.videoFileFullPath)">
                                📋
                            </BButton>
                            {{ projectStore.loadedProject?.testDriveVideoInfo?.videoFileName }}
                        </BListGroupItem>
                        <BListGroupItem v-if="projectStore.loadedProject?.testDriveTagInfo?.tagFileName">
                            <strong>Tag file:</strong><br>
                            <BButton size="sm" variant="outline-secondary" class="ml-2"
                                @click="copyToClipboard(projectStore.loadedProject?.testDriveTagInfo?.tagFileFullPath)">
                                📋
                            </BButton>
                            {{ projectStore.loadedProject?.testDriveTagInfo?.tagFileName }}
                        </BListGroupItem>
                    </BListGroup>
                </BCardBody>


                <BCardBody v-else>
                    <BListGroup flush>
                        <BListGroupItem>
                            <strong>Project ID:</strong><br>
                            {{ projectStore.loadedProject?.id }}
                        </BListGroupItem>
                        <BListGroupItem>
                            <strong>Driver:</strong><br>
                            {{ projectStore.loadedProject?.testDriveMetaInfo?.driverName }}
                        </BListGroupItem>
                        <BListGroupItem>
                            <strong>Route:</strong><br>
                            {{ projectStore.loadedProject?.testDriveMetaInfo?.routeName }}
                        </BListGroupItem>
                        <BListGroupItem>
                            <strong>Vehicle:</strong><br>
                            {{ projectStore.loadedProject?.testDriveMetaInfo?.vehicleName }}
                        </BListGroupItem>
                        <BListGroupItem v-if="projectStore.loadedProject?.testDriveDataInfo?.averageSpeedMS">
                            <strong>Avg. Speed:</strong><br>
                            {{ ((projectStore.loadedProject?.testDriveDataInfo?.averageSpeedMS ?? 0) * 3.6).toFixed(2)
                            }}
                            km/h
                        </BListGroupItem>
                        <BListGroupItem v-if="projectStore.loadedProject?.testDriveDataInfo?.maxSpeedMS">
                            <strong>Top Speed:</strong><br>
                            {{ ((projectStore.loadedProject?.testDriveDataInfo?.maxSpeedMS ?? 0) * 3.6).toFixed(2) }}
                            km/h
                        </BListGroupItem>
                        <BListGroupItem v-if="projectStore.loadedProject?.testDriveDataInfo?.drivenDistanceM">
                            <strong>Distance:</strong><br>
                            {{ ((projectStore.loadedProject?.testDriveDataInfo?.drivenDistanceM ?? 0) / 1000
                            ).toFixed(2)
                            }} km
                        </BListGroupItem>
                        <BListGroupItem v-if="projectStore.loadedProject?.testDriveDataInfo?.csvFileName">
                            <strong>Data file:</strong><br>
                            <BButton size="sm" variant="outline-secondary" class="ml-2"
                                @click="copyToClipboard(projectStore.loadedProject?.testDriveDataInfo?.csvFileFullPath)">
                                📋
                            </BButton>
                            {{ projectStore.loadedProject?.testDriveDataInfo?.csvFileName }}

                        </BListGroupItem>
                        <BListGroupItem v-if="projectStore.loadedProject?.testDriveVideoInfo?.videoFileName">
                            <strong>Video file:</strong><br>
                            <BButton size="sm" variant="outline-secondary" class="ml-2"
                                @click="copyToClipboard(projectStore.loadedProject?.testDriveVideoInfo?.videoFileFullPath)">
                                📋
                            </BButton>
                            {{ projectStore.loadedProject?.testDriveVideoInfo?.videoFileName }}
                        </BListGroupItem>
                        <BListGroupItem v-if="projectStore.loadedProject?.testDriveTagInfo?.tagFileName">
                            <strong>Tag file:</strong><br>
                            <BButton size="sm" variant="outline-secondary" class="ml-2"
                                @click="copyToClipboard(projectStore.loadedProject?.testDriveTagInfo?.tagFileFullPath)">
                                📋
                            </BButton>
                            {{ projectStore.loadedProject?.testDriveTagInfo?.tagFileName }}
                        </BListGroupItem>
                        <BListGroupItem>
                            <strong>Data/Video Overlap:</strong><br>
                            <TimelineRange :testDriveDataInfo="projectStore.loadedProject?.testDriveDataInfo ?? null"
                                :testDriveVideoInfo="projectStore.loadedProject?.testDriveVideoInfo ?? null" />
                        </BListGroupItem>
                    </BListGroup>
                </BCardBody>
            </BCard>

        </div>

        <div v-else>
            <h4 v-if="projectStore.availableProjects.length">Available Projects</h4>

            <div v-for="(project, index) in projectStore.availableProjects" :key="index">
                <ProjectListItem :project="project" />
            </div>
        </div>

    </div>
</template>

<script setup lang="ts">

import ProjectListItem from './ProjectListItem.vue';
import TimelineRange from './TimelineRange.vue'
import { ref } from 'vue'
import { useProjectStore } from './../stores/projectStore';
import { CreateProjectPayload, getAxiosErrorMessage, isNullOrUndefined, uploadCsvFile, uploadVideoFile } from '../core/utilities/utilities';
import { safeFetch, ProjectApiClient as client } from '../core/utilities/utilities';
import {
    BButton, BFormGroup, BFormRadio, BFormRadioGroup, BFormSelect, BFormFile,
    BListGroupItem, BListGroup, BCardBody, BCard, BCardHeader, BModal, BProgress, BProgressBar,
    BFormInput, BFormTextarea
} from 'bootstrap-vue-next';
import { useToastController } from 'bootstrap-vue-next';




const { show: showToast } = useToastController();


const projectStore = useProjectStore()

const fileInputMode = ref("use_existing");// or "upload_new"
const newCsvFile = ref<null | File>(null)
const newVideoFile = ref<null | File>(null)

const csvUploadProgress = ref(0)
const videoUploadProgress = ref(0)
const isUploading = ref(false)

// Create a factory function to provide default values
const createDefaultProjectPayload = (): CreateProjectPayload => {
    return {
        csvFileName: '',
        videoFileName: '',
        driverName: '',
        routeName: '',
        vehicleName: '',
    };
}


const showNewProjectModal = ref(false)
const newProjectPayload = ref<CreateProjectPayload>(createDefaultProjectPayload())



const handleCreateProject = async () => {
    try {
        // Add your project creation logic here
        console.log('Creating new project:', newProjectPayload.value)

        if (fileInputMode.value === "upload_new") {
            if (isNullOrUndefined(newCsvFile.value) || isNullOrUndefined(newVideoFile.value)) {
                throw new Error("Please upload both CSV and video files.");
            }

            try {
                const dataCsv = await uploadCsvFile(newCsvFile.value!, x => csvUploadProgress.value = x);
                console.log('CSV upload response:', dataCsv)
                newProjectPayload.value.csvFileName = dataCsv.filename;
            } catch (error) {
                showToast?.({
                    props: {
                        title: 'Error uploading CSV',
                        body: getAxiosErrorMessage(error),
                        value: 2500,
                        variant: 'danger',
                        pos: 'top-end',
                    }
                });
                return;

            }

            try {
                const dataVideo = await uploadVideoFile(newVideoFile.value!, x => videoUploadProgress.value = x);
                console.log('Video upload response:', dataVideo)
                newProjectPayload.value.videoFileName = dataVideo.filename;
            } catch (error) {
                showToast?.({
                    props: {
                        title: 'Error uploading video',
                        body: getAxiosErrorMessage(error),
                        value: 2500,
                        variant: 'danger',
                        pos: 'top-end',
                    }
                });
                return;

            }
        }


        const [error, data] = await safeFetch(() => client.createTestdriveApiV1ProjectCreatePost({
            createProjectPayload: newProjectPayload.value
        }))
        if (error) {
            showToast?.({
                props: {
                    title: 'Error',
                    body: error.message,
                    value: 2500,
                    variant: 'danger',
                    pos: 'top-end',

                }
            });
        } else if (data) {
            showToast?.({
                props: {
                    title: 'Project created',
                    body: `the project was created successfully with id: ${data.testdrive.id}.`,
                    value: 2500,
                    variant: 'success',
                    pos: 'top-end',
                }
            });
            projectStore.addProject(data.testdrive)
        }

    } catch (error) {
        console.error(error)
    } finally {
        showNewProjectModal.value = false; // manually close modal

        // reset new Project
        newProjectPayload.value = createDefaultProjectPayload()

        isUploading.value = false;
        csvUploadProgress.value = 0;
        videoUploadProgress.value = 0;
    }

}


const handleUnloadProject = async () => {
    console.log('Unloading project id:', projectStore.loadedProject?.id)
    await projectStore.unloadProject()
}


const copyToClipboard = async (text: string | undefined) => {
    if (!text) return;
    await navigator.clipboard.writeText(text)


    showToast?.({
        props: {
            title: 'Copied to clipboard',
            body: `File path was copied to clipboard`,
            value: 2500,
            variant: 'success',
            pos: 'top-end',
        }
    });

}


</script>

<style>
.progress-bar {
    position: relative !important;
}
</style>