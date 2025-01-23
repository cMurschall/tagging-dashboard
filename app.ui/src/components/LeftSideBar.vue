<template>
    <div>
        <BButton variant="success" @click="showNewProjectModal = !showNewProjectModal">Create new project</BButton>

        <BModal v-model="showNewProjectModal" title="Create New Project" @ok="createNewProject">
            <div>
                <BFormGroup label="CSV file:" label-for="input-csv-file"
                    description="Please select the corresponding csv file">
                    <b-form-select id="input-csv-file" v-model="newProject.rawDataPath"
                        :options="store.availableCsvValues"></b-form-select>
                </BFormGroup>

                <BFormGroup label="Video file:" label-for="input-video-file"
                    description="Please select the corresponding video file">
                    <b-form-select id="input-video-file" v-model="newProject.videoPath"
                        :options="store.availableVideoValues"></b-form-select>
                </BFormGroup>


                <!-- Driver Name -->
                <BFormGroup label="Driver Name" label-for="driver-name">
                    <b-form-input id="driver-name" v-if="newProject.metaData" v-model="newProject.metaData.driverName"
                        required placeholder="Enter driver's name"></b-form-input>
                </BFormGroup>

                <!-- Vehicle ID -->
                <BFormGroup label="Vehicle ID" label-for="vehicle-id">
                    <b-form-input id="vehicle-id" v-if="newProject.metaData" v-model="newProject.metaData.vehicleId"
                        required placeholder="Enter vehicle ID"></b-form-input>
                </BFormGroup>



                <!-- Route Name -->
                <BFormGroup label="Route Name" label-for="route-name">
                    <b-form-input id="route-name" v-if="newProject.metaData" v-model="newProject.metaData.routeName"
                        required placeholder="Enter route name"></b-form-input>
                </BFormGroup>

                <!-- Notes -->
                <BFormGroup label="Notes" label-for="notes">
                    <b-form-textarea id="notes" v-if="newProject.metaData" v-model="newProject.metaData.notes"
                        placeholder="Enter additional notes (optional)"></b-form-textarea>
                </BFormGroup>
            </div>


        </BModal>



        <h4 v-if="store.availableProjects.length">Available Projects</h4>

        <div v-for="(project, index) in store.availableProjects" :key="index">
            <ProjectListItem :project="project" />
        </div>


    </div>
</template>

<script setup lang="ts">
import ProjectListItem from './ProjectListItem.vue';


import { ref } from 'vue'
import { useAppStore } from './../stores/appStore';
import { useToastController } from 'bootstrap-vue-next'

const { show: showToast } = useToastController()



// Create a factory function to provide default values
function createDefaultTestDriveData(): TestDriveDataOutput {
    return {
        id: -1,
        rawDataPath: '',
        videoPath: '',
        tags: [],
        metaData: {
            driverName: '',
            routeName: '',
            vehicleId: '',
            notes: ''
        }
    };
}


const showNewProjectModal = ref(false)

import { safeFetch, ApiClient as client, TestDriveDataOutput } from './../services/Utilities';
import { BFormGroup } from 'bootstrap-vue-next';

const newProject = ref<TestDriveDataOutput>(createDefaultTestDriveData())



const store = useAppStore()


const createNewProject = async () => {
    // Add your project creation logic here
    console.log('Creating new project:', newProject.value)


    const [error, data] = await safeFetch(() => client.createTestdriveApiV1ProjectPost({
        testDriveDataInput: newProject.value
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
        store.addProject(data.testdrive)
    }
    // reset new Project
    newProject.value = createDefaultTestDriveData()

}
</script>

<style></style>