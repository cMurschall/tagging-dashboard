<template>
    <!-- The container for our GridStack layout -->
    <div ref="gridContainer" class="grid-stack mt-3"></div>
</template>

<script lang="ts">
import {
    useTemplateRef,
    defineComponent,
    onMounted,
    onBeforeUnmount,
    watch,
    createApp,
    h
} from 'vue';
import { GridStack, GridStackNode } from 'gridstack';
import { GridItem, useGridStore } from '../stores/gridStore';
import CardWrapper from './CardWrapper.vue';
import { pinia, bootstrap } from "./../plugins/AppPlugins";



export default defineComponent({
    name: 'GenericGridStack',
    setup() {
        // Access the store
        const gridStore = useGridStore();

        const gridContainer = useTemplateRef('gridContainer')
        let grid: GridStack | null = null;

        // Keep track of Vue sub-apps so we can unmount them on removal
        const shadowDom = new Map<string, any>();

        onMounted(() => {
            if (!gridContainer.value) {
                console.error('Grid container not found');
                return;
            }

            // 1) Initialize GridStack on the container
            grid = GridStack.init(
                {
                    float: true,
                    cellHeight: 70,
                    minRow: 1
                },
                gridContainer.value as HTMLElement
            );

            // 2) GridStack's render callback:
            GridStack.renderCB = (contentEl: HTMLElement, w: GridStackNode) => {
                const widget = w as GridItem;


                console.log('Grid render CB', widget);
                // The store's component map (component name -> definition)
                const compName = widget.component as string;
                const compDef = gridStore.componentMap[compName];
                if (!compDef) {
                    contentEl.textContent = `Unknown component: ${compName}`;
                    return;
                }

                // Create a sub-app that wraps the child component in CardWrapper

                const subApp = createApp({
                    setup() {
                        // If user clicks remove in the card header, remove from store
                        const handleRemove = () => {
                            if (widget.id) gridStore.removeItemById(widget.id.toString());
                        };

                        // Build the child that goes in the slot:
                        const childNode = h(compDef, {
                            // Spread any custom props from our widget props
                            ...(widget.props || {})
                        });

                        // Wrap that child in our CardWrapper
                        return () =>
                            h(CardWrapper, {
                                title: widget.title,
                                onRemove: handleRemove
                            }, {
                                default: () => childNode
                            });
                    }
                });

                // we share the same plugins with the parent app
                subApp.use(bootstrap);
                subApp.use(pinia);

                // Mount the child sub-app into the .grid-stack-item-content
                const vm = subApp.mount(contentEl);
                shadowDom.set(widget.id, { app: subApp, vm });
            };

            // 3) When GridStack removes widgets (drag out or removeWidget?), unmount the child apps
            grid.on('removed', (_event, removedItems: GridStackNode[]) => {
                removedItems.forEach(item => {
                    const id = item.id as string;
                    const stored = shadowDom.get(id);
                    if (stored) {

                        stored.app.unmount();
                        shadowDom.delete(id);
                    }
                });
            });

            // 4) Load the store items initially
            grid.load(gridStore.gridItems);
        });

        // 5) Whenever the store's gridItems change, reload GridStack
        watch(
            () => gridStore.gridItems,
            newItems => {
                if (!grid) return;
                // removeAll(false) => do not destroy the entire DOM/callback
                grid.removeAll(false);
                grid.load(newItems);
            },
            { deep: true }
        );

        // 6) Cleanup on unmount
        onBeforeUnmount(() => {
            // Unmount sub-apps
            shadowDom.forEach(vm => vm.$destroy?.());
            shadowDom.clear();

            // Destroy the grid
            if (grid) {
                grid.destroy(false);
                grid = null;
            }
        });

        return {};
    }
});
</script>

<style scoped>
.grid-stack {
    /* background: #fafafa; */
    background: lime;
    /* height is full height of the parent */
    height: 100%;
    
}

.grid-stack-item-content {
    background: #e0e7ff;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
}
</style>