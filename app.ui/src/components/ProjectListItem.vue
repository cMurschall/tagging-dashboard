<template>
    <BCard bg-variant="light" text-variant="dark" class="mb-2">
        <BCardText>
            <div>
                <p>Route: {{ props.project.metaData?.routeName }}</p>
                <p>Driver: {{ props.project.metaData?.driverName }}</p>
            </div>
        </BCardText>


        <template #footer>
            <div class="d-flex justify-content-between">
                <BButton>Load</BButton>
                <BButton variant="info">Edit</BButton>
                <BButton variant="danger" @click="handleDeleteProject">Delete</BButton>
            </div>
        </template>
    </BCard>


</template>



<script setup lang="ts">
import { defineProps } from 'vue'
import { useAppStore } from './../stores/appStore';

import { safeFetch, ApiClient as client, TestDriveDataOutput } from '../services/Utilities'

import { useToastController } from 'bootstrap-vue-next'

const { show: showToast } = useToastController()

const store = useAppStore();

interface ProjectListItemProps {
    project: TestDriveDataOutput
}

const props = defineProps<ProjectListItemProps>()


const handleDeleteProject = async () => {
    console.log('Deleting project:', props.project.id)

    
    const [error, data] = await safeFetch(() => client.deleteTestdriveApiV1ProjectDelete({
        testdriveId: props.project.id
    }))
    if(error){
        showToast?.({
          props: {
            title: 'Error deleting project',
            body: error.message,
            value: 2500,
            variant: 'danger',
            pos: 'top-end',

          }
        });
    }
    else{
        showToast?.({
          props: {
            title: 'Project deleted',
            body: 'Project deleted successfully',
            value: 2500,
            variant: 'success',
            pos: 'top-end',
          }
        });

        store.removeProject(props.project.id)
    }
    
}


</script>
