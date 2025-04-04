// src/stores/appStore.ts
import { defineStore } from 'pinia';


export interface GridItem {
    id: string;
    type: string;
    title: string;

    position: {
        x: number;
        y: number;
    };
    size: {
        width: number;
        height: number;
    };

    state: any;
}


export const useGridStore = defineStore('grid', {
    state: () => ({
        gridItems: {} as Record<string, GridItem>,
        layouts: {} as Record<string, Record<string, GridItem>>,
    }),
    getters: {
        getAllGridItems: (state) => {
            return state.gridItems;
        },
        getGridItemById: (state) => {
            return (id: string): GridItem | null => state.gridItems[id] || null;
        },
        getAllLayouts: (state) => {
            return state.layouts;
        },
        getLayoutByName: (state) => {
            return (name: string) => state.layouts[name] || null;
        }
    },
    actions: {

        addGridItem(item: GridItem) {
            this.gridItems[item.id] = item;
        },
        removeGridItem(id: string) {
            delete this.gridItems[id];
        },
        updateGridItemSize(id: string, size: { width: number; height: number }) {
            const item = this.gridItems[id];
            if (item) {
                item.size = size;
            }
        },
        updateGridItemPosition(id: string, position: { x: number; y: number }) {
            const item = this.gridItems[id];
            if (item) {
                item.position = position;
            }
        },
        updateGridItemState(id: string, state: any) {
            const item = this.gridItems[id];
            if (item) {
                item.state = state;
            }
        },
        saveGridItemsAsLayout(name: string) {
            this.layouts[name] = { ...this.gridItems };
        }
    },
    persist: {
        key: 'saved-layouts',
        storage: localStorage,
        pick: ['layouts']
    }

});
