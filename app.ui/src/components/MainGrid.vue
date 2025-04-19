<template>
    <div ref="gridContainer" class="grid-stack mt-3 mb-1"></div>
</template>

<script lang="ts">
import {
    useTemplateRef,
    defineComponent,
    onMounted,
    onBeforeUnmount,
    createApp,
    h,
    provide,
    readonly,
    markRaw,
} from 'vue';
import { GridItemHTMLElement, GridStack, GridStackNode } from 'gridstack';
import CardWrapper from './CardWrapper.vue';
import { pinia, bootstrap } from "./../plugins/AppPlugins";
import {getGridManager, GridManagerItem, GridManager } from './../managers/gridItemManager';


export default defineComponent({
    name: 'GenericGridStack',
    setup() {
        const gridContainer = useTemplateRef('gridContainer');
        let grid: GridStack | null = null;

        // Keep track of Vue sub-apps so we can unmount them on removal
        const shadowDom = new Map<string, any>();
        let renderedItems: GridManagerItem[] = [];


        const getCurrentLayout = () => {
            if (!grid) return;
            const layoutData = grid.save();
            return layoutData;
        };


        onMounted(() => {
            if (!gridContainer.value) {
                console.error('Grid container not found');
                return;
            }

            // Initialize GridStack on the container
            grid = GridStack.init(
                {
                    float: true,
                    cellHeight: 70,
                    minRow: 1,
                    margin: 2,
                },
                gridContainer.value as HTMLElement
            );
    

            grid.on('resizestop', (event: Event, el: GridItemHTMLElement) => {
                console.log('Resizestop:', { event, node: el.gridstackNode });

                if (el.gridstackNode && el.gridstackNode.id) {
                    getGridManager().updateItemById(el.gridstackNode.id.toString(), {
                        w: el.gridstackNode.w ?? 0,
                        h: el.gridstackNode.h ?? 0,
                    });
                }
            });



            grid.on('dragstop', (event: Event, el: GridItemHTMLElement) => {
                console.log('Drag end:', { event, node: el.gridstackNode });

                if (el.gridstackNode && el.gridstackNode.id) {
                    getGridManager().updateItemById(el.gridstackNode.id.toString(), {
                        x: el.gridstackNode.x ?? 0,
                        y: el.gridstackNode.y ?? 0,
                    });
                }
            });


            // GridStack's render callback:
            GridStack.renderCB = (contentEl: HTMLElement, w: GridStackNode) => {
                w.noMove = true; // Prevent moving the item with drag and drop

                const widget = w as GridManagerItem;

                console.log('Grid render CB', widget);


                // The store's component map (component name -> definition)
                const compName = widget.component as string;
                const compDef = getGridManager().getComponentMap()[compName]();
                if (!compDef) {
                    contentEl.textContent = `Unknown component: ${compName}`;
                    return;
                }


                // Create a sub-app that wraps the child component in CardWrapper
                const subApp = createApp({
                    setup() {

                        // Iterate over dependencies and provide each one:
                        const gridStoreItem = getGridManager().getGridItems().find(item => item.id === widget.id);
                        if (gridStoreItem) {
                            for (const key in gridStoreItem.dependencies) {
                                provide(key, readonly(markRaw(gridStoreItem.dependencies[key])));
                            }
                        }

                        // If user clicks remove in the card header, remove from store
                        const handleRemove = () => {
                            if (widget.id) {
                                getGridManager().removeItemById(widget.id.toString());
                            }
                        };

                        // If user clicks remove in the card header, 
                        const handleToggleMoveLock = (value: boolean) => {
                            console.log('Move lock changed:', {
                                value,
                                id: widget.id,
                            });
                            if (grid && w.el) {
                                grid?.update(w.el, { noMove: value });
                            }
                        };

                        // Wrap that child in our CardWrapper
                        return () =>
                            h(CardWrapper, {
                                title: widget.title,
                                onRemove: handleRemove,
                                "onMove-lock-changed": handleToggleMoveLock,
                            }, {
                                default: (slotProps: any) => {
                                    return h(compDef, {
                                        ...(widget.props || {}),
                                        showMenu: slotProps.showMenu,
                                        id: widget.id,
                                    });
                                }
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



            // Load the store items initially
            grid.load(getGridManager().getGridItems());

        });

        GridManager.newItemObservable.subscribe((newItem) => {
            console.log('New item added', newItem);
            const hasNode = renderedItems.some(item => item.id === newItem.id);
            if (!hasNode) {
                console.log(`Adding new item: ${newItem.title}-${newItem.id}. Has node: ${hasNode}`);
                const node = grid?.addWidget(newItem);
                if (node) {
                    renderedItems.push(newItem);
                }
            }
        });

        GridManager.removeItemObservable.subscribe((id) => {
            console.log('Removing item', id);
            const node = grid?.engine.nodes.find(n => n.id?.toString() === id.toString());
            if (node && node.el) {
                const actualId = node.id?.toString();
                grid?.removeWidget(node.el, false);
                renderedItems = renderedItems.filter(item => item.id !== id);

                // Unmount Vue sub-app
                if (actualId) {
                    const stored = shadowDom.get(actualId);
                    if (stored) {
                        stored.app.unmount();
                        shadowDom.delete(actualId);
                    } else {
                        console.log('Could not find shadow dom for', actualId);
                    }
                }
            }
        });

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

        return {
            getCurrentLayout
        };
    }
});
</script>

<style scoped>
.grid-stack {
    background: #fafafa;
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
