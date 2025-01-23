// src/stores/appStore.ts
import { defineStore } from 'pinia';

import { safeFetch, ApiClient as client, TestDriveDataOutput } from './../services/Utilities';
import { useToastController } from 'bootstrap-vue-next'

const { show: showToast } = useToastController()



export const useAppStore = defineStore('app', {
  state: () => ({
    availableCsvValues: [] as string[],
    availableVideoValues: [] as string[],
    availableProjects: [] as TestDriveDataOutput[],
    loadedProject: {},


    isLoading: false

  }),
  actions: {
    addProject(project: TestDriveDataOutput) {
      this.availableProjects.push(project);
    },
    removeProject(projectId: number) {
      this.availableProjects = this.availableProjects.filter(
        (project) => project.id !== projectId
      );
    },
    async initializeStore() {
      this.isLoading = true;

      const [csvFilesError, csvFilesData] = await safeFetch(() => client.getCsvFilesApiV1ProjectFilesCsvGet());
      if (csvFilesError) {
        showToast?.({
          props: {
            title: 'Error loading csv files',
            body: csvFilesError.message,
            value: 2500,
            variant: 'danger',
            pos: 'top-end',

          }
        });
        // log error 
        console.error('Error fetching csv files', csvFilesError);

      } else {
        this.availableCsvValues = csvFilesData?.files || [];
        console.info('CSV files fetched', this.availableCsvValues);
      }

      const [videoFilesError, videoFilesData] = await safeFetch(() => client.getVideoFilesApiV1ProjectFilesVideoGet());
      if (videoFilesError) {
        showToast?.({
          props: {
            title: 'Error loading video files',
            body: videoFilesError.message,
            value: 2500,
            variant: 'danger',
            pos: 'top-end',

          }
        });
        // log error
        console.error('Error fetching video files', videoFilesError);
      }
      else {
        this.availableVideoValues = videoFilesData?.files || [];
        console.info('Video files fetched', this.availableVideoValues);
      }


      const [allProjectsError, allProjectesData] = await safeFetch(() => client.getAllTestdrivesApiV1ProjectAllGet());
      if (allProjectsError) {
        showToast?.({
          props: {
            title: 'Error loading projects',
            body: allProjectsError.message,
            value: 2500,
            variant: 'danger',
            pos: 'top-end',

          }
        });
        // log error
        console.error('Error fetching all projects', allProjectsError);
      }
      else {
        this.availableProjects = allProjectesData?.testdrives || [];
        console.info('All projects fetched', this.availableProjects);
      }

      this.isLoading = false;
    }

  },
});
