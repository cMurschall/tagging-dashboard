// src/stores/appStore.ts
import { defineStore } from 'pinia';

import { safeFetch, ApiClient as client, TestDriveProjectInfo } from './../services/Utilities';
import { useToastController } from 'bootstrap-vue-next'

const { show: showToast } = useToastController()



export const getProjectStore = defineStore('app', {
  state: () => ({
    availableCsvValues: [] as string[],
    availableVideoValues: [] as string[],
    availableProjects: [] as TestDriveProjectInfo[],
    loadedProject: undefined as TestDriveProjectInfo | undefined,

    isLoading: false

  }),
  getters: {
    isProjectLoaded: (state) => !!state.loadedProject,
  },
  actions: {
    addProject(project: TestDriveProjectInfo) {
      this.availableProjects.push(project);
    },
    removeProject(projectId: number) {
      this.availableProjects = this.availableProjects.filter(
        (project) => project.id !== projectId
      );
    },
    async loadProject(projectId: number) {
      const [error, activeProject] = await safeFetch(() => client.activateTestdriveApiV1ProjectActivateTestdriveIdPost({
        testdriveId: projectId
      }));
      if (activeProject?.testdrive) {
        this.loadedProject = activeProject.testdrive;
        console.info('Project loaded', this.loadedProject);
      }
    },
    async unloadProject() {

      const [error, deactivatedProject] = await safeFetch(() => client.deactivateTestdriveApiV1ProjectDeactivatePost());
      if (error) {
        showToast?.({
          props: {
            title: 'Error unloading project',
            body: error.message,
            value: 2500,
            variant: 'danger',
            pos: 'top-end',

          }
        });
        console.error('Error unloading project', error);
      } else {
        this.loadedProject = undefined;
        console.info('Project unloaded');
      }

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



      const [activeProjectError, activeProject] = await safeFetch(() => client.getActiveTestdriveApiV1ProjectActiveGet());
      if (activeProjectError) {
        showToast?.({
          props: {
            title: 'Error loading active project',
            body: activeProjectError.message,
            value: 2500,
            variant: 'danger',
            pos: 'top-end',

          }
        });
        // log error
        console.error('Error fetching active project', activeProjectError);
      } else if (activeProject?.testdrive) {
        this.loadedProject = activeProject.testdrive;
        console.info('Active project fetched', this.loadedProject);
      }

      this.isLoading = false;
    }

  },
});
