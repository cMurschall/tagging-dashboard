<template>
    <BCard bg-variant="light" text-variant="dark" class="mb-2" 
     :header-bg-variant="isProjectLoaded ? 'warning' : 'light'"
     :header="props.project.metaData?.routeName ">
    
        
        
        <BCardText>
            <div>
                <p>Date: {{ dateTime }}</p>
                <p>Driver: {{ props.project.metaData?.driverName }}</p>
            </div>
        </BCardText>


        <template #footer>
            <div class="d-flex justify-content-between">
                <BButton  @click="handleLoadProject">Load</BButton>
                <BButton variant="info">Edit</BButton>
                <BButton variant="danger" @click="handleDeleteProject">Delete</BButton>
            </div>
        </template>
    </BCard>


</template>



<script setup lang="ts">
import { computed, defineProps } from 'vue'
import { getProjectStore } from './../stores/projectStore';

import { safeFetch, ApiClient as client, TestDriveDataOutput } from '../services/Utilities'

import { useToastController } from 'bootstrap-vue-next'

const { show: showToast } = useToastController()

const store = getProjectStore();

interface ProjectListItemProps {
    project: TestDriveDataOutput
}

const props = defineProps<ProjectListItemProps>()


const isProjectLoaded = computed(() => {
  return store.loadedProject?.id === props.project.id
})

const dateTime = computed(() => {
  // Parse the date string into a Date object
  const date = props.project.metaData?.testDate
  if(!date){
    return ' - '
  }


  // Check if the date is valid
  if (isNaN(date.getTime())) {
    throw new Error("Invalid date string");
  }

  // Extract date components
  const day = String(date.getDate()).padStart(2, "0"); // Add leading zero
  const month = String(date.getMonth() + 1).padStart(2, "0"); // Months are 0-indexed
  const year = date.getFullYear();

  // Extract time components
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");

  // Format the date as dd/mm/yyyy HH:MM
  return `${day}.${month}.${year} ${hours}:${minutes}`;
})

const handleLoadProject = () => {
    console.log('Loading project:', props.project.id)
    store.loadProject(props.project.id)
}

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
