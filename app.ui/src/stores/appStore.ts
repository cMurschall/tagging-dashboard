// src/stores/appStore.ts
import { defineStore } from 'pinia';

export const useAppStore = defineStore('app', {
  state: () => ({
    timestamp: 0, // video timestamp
    windows: [], // array of window configurations
    plugins: [], // loaded plugins
    tags: [], // user tags
  }),
  actions: {
    updateTimestamp(newTimestamp: number) {
      this.timestamp = newTimestamp;
    },
    addWindow(windowConfig: object) {
      this.windows.push(windowConfig);
    },
    removeWindow(windowId: string) {
      this.windows = this.windows.filter((window) => window.id !== windowId);
    },
    addTag(tag: object) {
      this.tags.push(tag);
    },
  },
});
