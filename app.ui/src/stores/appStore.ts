// src/stores/appStore.ts
import { defineStore } from 'pinia';

import { safeFetch, ApiClient as client, TestDriveDataOutput } from './../services/Utilities';

export const useAppStore = defineStore('app', {
  state: () => ({
    availableCsvValues: [] as string[],
    availableVideoValues: [] as string[],
    availableProjects: [] as TestDriveDataOutput[],
    loadedProject: {},


    isLoading: false,
    errors: [] as Error[],

  }),
  actions: {
    async initializeStore() {
      this.isLoading = true;

      const [csvFilesError, csvFilesData] = await safeFetch(() => client.getCsvFilesApiV1ProjectFilesCsvGet());
      if (csvFilesError) {
        this.errors.push(csvFilesError);
        // log error 
        console.error('Error fetching csv files', csvFilesError);

      } else {
        this.availableCsvValues = csvFilesData?.files || [];
        console.info('CSV files fetched', this.availableCsvValues);
      }

      const [videoFilesError, videoFilesData] = await safeFetch(() => client.getVideoFilesApiV1ProjectFilesVideoGet());
      if (videoFilesError) {
        this.errors.push(videoFilesError);
        // log error
        console.error('Error fetching video files', videoFilesError);
      }
      else {
        this.availableVideoValues = videoFilesData?.files || [];
        console.info('Video files fetched', this.availableVideoValues);
      }


      const [allProjectsError, allProjectesData] = await safeFetch(() => client.getAllTestdrivesApiV1ProjectAllGet());
      if (allProjectsError) {
        this.errors.push(allProjectsError);
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
