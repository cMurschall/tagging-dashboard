<template>
    <div>
        <BButton variant="success" @click="showNewProjectModal = !showNewProjectModal">Create new project</BButton>

        <BModal v-model="showNewProjectModal" title="Create New Project" @ok="createNewProject">
            <div>
                <BFormGroup label="CSV file:" label-for="input-csv-file"
                    description="Please select the corresponding csv file">
                    <b-form-select id="input-csv-file" v-model="newProjectPayload.csvFileName"
                        :options="projectStore.availableCsvValues"></b-form-select>
                </BFormGroup>

                <BFormGroup label="Video file:" label-for="input-video-file"
                    description="Please select the corresponding video file">
                    <b-form-select id="input-video-file" v-model="newProjectPayload.videoFileName"
                        :options="projectStore.availableVideoValues"></b-form-select>
                </BFormGroup>


                <!-- Driver Name -->
                <BFormGroup label="Driver Name" label-for="driver-name">
                    <b-form-input id="driver-name" v-model="newProjectPayload.driverName" required
                        placeholder="Enter driver's name"></b-form-input>
                </BFormGroup>

                <!-- Vehicle ID -->
                <BFormGroup label="Vehicle ID" label-for="vehicle-id">
                    <b-form-input id="vehicle-id" v-model="newProjectPayload.vehicleName" required
                        placeholder="Enter vehicle ID"></b-form-input>
                </BFormGroup>



                <!-- Route Name -->
                <BFormGroup label="Route Name" label-for="route-name">
                    <b-form-input id="route-name" v-model="newProjectPayload.routeName" required
                        placeholder="Enter route name"></b-form-input>
                </BFormGroup>

                <!-- Notes -->
                <BFormGroup label="Notes" label-for="notes">
                    <b-form-textarea id="notes" v-model="newProjectPayload.notes"
                        placeholder="Enter additional notes (optional)"></b-form-textarea>
                </BFormGroup>
            </div>


        </BModal>

        <div v-if="projectStore.isProjectLoaded">
            <BCard class="my-3">
                <BCardHeader class="d-flex justify-content-between align-items-center">
                    <h4 class="mb-0">Loaded Project</h4>
                    <BButton variant="danger" size="sm" @click="handleUnloadProject">
                        <i class="bi bi-x-circle me-1"></i> Unload
                    </BButton>
                </BCardHeader>
                <BCardBody>
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
                        <BListGroupItem>
                            <strong>Avg. Speed:</strong><br>
                            {{ ((projectStore.loadedProject?.testDriveDataInfo?.averageSpeedMS ?? 0)* 3.6).toFixed(2) }}
                            km/h
                        </BListGroupItem>
                        <BListGroupItem>
                            <strong>Top Speed:</strong><br>
                            {{ ((projectStore.loadedProject?.testDriveDataInfo?.maxSpeedMS ?? 0) * 3.6).toFixed(2) }} km/h
                        </BListGroupItem>
                        <BListGroupItem>
                            <strong>Distance:</strong><br>
                            {{ ((projectStore.loadedProject?.testDriveDataInfo?.drivenDistanceM ?? 0) / 1000 ).toFixed(2)
                            }} km
                        </BListGroupItem>
                    </BListGroup>

                </BCardBody>
                <!-- <BCardFooter class="text-end">
             
                </BCardFooter> -->
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

import { ref } from 'vue'
import { useProjectStore } from './../stores/projectStore';
import { useGridStore } from './../stores/gridStore';

import { useToastController } from 'bootstrap-vue-next'
import { CreateProjectPayload } from '../services/Utilities';

import { safeFetch, ProjectApiClient as client } from './../services/Utilities';
import { BFormGroup } from 'bootstrap-vue-next';



const { show: showToast } = useToastController()
const projectStore = useProjectStore()
const gridStore = useGridStore()


// Create a factory function to provide default values
function createDefaultProjectPayload(): CreateProjectPayload {
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

const createNewProject = async () => {
    // Add your project creation logic here
    console.log('Creating new project:', newProjectPayload.value)


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
    // reset new Project
    newProjectPayload.value = createDefaultProjectPayload()

}


const handleUnloadProject = async () => {
    console.log('Unloading project id:', projectStore.loadedProject?.id)
    await projectStore.unloadProject()
}
</script>

<style></style>