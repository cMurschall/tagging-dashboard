// src/stores/gridStore.ts
import { defineStore } from 'pinia';
import { markRaw } from 'vue';

export interface GridItem<T = Record<string, any>> {
  id: string;
  x?: number;
  y?: number;
  w?: number;
  h?: number;
  component?: string;
  title?: string;
  // Let props be a generic Record, so each widget can have different fields
  // props?: Record<string, any>;
  props?: T;  // This enforces type safety per component
}

export const useGridStore = defineStore('gridStore', {
  state: () => ({
    gridItems: [] as GridItem[],
    componentMap: {} as Record<string, any>
  }),
  actions: {
    // Because we don't want to provide any initial items, we won't have a "setGridItems" on mount.
    // We'll just add items on-demand.

    setComponentMap(map: Record<string, any>) {
      this.componentMap = map;
    },

    // addNewItem<T extends Record<string, any>>(item: GridItem<T>) {
    //   // A simple push to the array
    //   this.gridItems.push(item);
    // },

    addNewItem<T extends Record<string, any>>(item: Omit<GridItem<T>, 'props'> & { props: T }) {
      // Mark the props object as raw to prevent Vue from stripping prototype
      // item.props = markRaw(item.props);
      this.gridItems.push(item);
    },

    removeItemById(id: string) {
      const countBefore = this.gridItems.length
      this.gridItems = this.gridItems.filter(item => item.id !== id);
      const countAfter = this.gridItems.length

      // assert we removed exactly one item
      if (countBefore - countAfter !== 1) {
        console.error(`Error: removed ${countBefore - countAfter} items instead of 1`);
      }
    },

    removeAllItems() {
      this.gridItems = [];
    }
  }
});
