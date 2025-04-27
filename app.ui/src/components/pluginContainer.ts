import { PluginServices, TaggingDashboardPlugin } from '@/types/plugin';
import { createApp, App, Component, nextTick } from 'vue';



export function createVuePluginAdapter(VueComponent: Component): TaggingDashboardPlugin {

    // Store the Vue app instance reference
    let vueAppInstance: App | null = null;

    // Store user-defined lifecycle hooks
    let userOnMounted: (() => void) | undefined;
    let userOnUnmounted: (() => void) | undefined;

    const pluginAdapter: TaggingDashboardPlugin = {
        create: (container: HTMLElement, pluginService: PluginServices) => {
            // Prevent creating multiple instances if create is called again without unmount
            if (vueAppInstance) {
                console.warn('Vue plugin adapter: Instance already exists. Unmounting previous one.');
                pluginAdapter.onUnmounted?.(); // Trigger cleanup
            }

            // Create the Vue app instance
            vueAppInstance = createApp(VueComponent);

            vueAppInstance.provide('pluginService', pluginService);
            vueAppInstance.mount(container);


            if (userOnMounted) {
                nextTick(userOnMounted);
            }
        },


        get onMounted(): (() => void) | undefined {
            return userOnMounted;
        },
        set onMounted(hook: (() => void) | undefined) {
            userOnMounted = hook;
        },

        get onUnmounted(): (() => void) | undefined {
            // Return the wrapped function that includes Vue cleanup
            return userOnUnmounted;
        },
        set onUnmounted(hook: (() => void) | undefined) {

            userOnUnmounted = () => {

                if (hook) {
                    try {
                        hook();
                    } catch (error) {
                        console.error("Error executing plugin onUnmounted hook:", error);
                    }
                }

                // Perform the Vue app unmounting
                if (vueAppInstance) {
                    vueAppInstance.unmount();
                    vueAppInstance = null; // Clear the reference
                    console.log('Vue plugin adapter: Instance unmounted.');
                } else {
                    console.warn('Vue plugin adapter: No instance to unmount.');
                }
            };
        }
    };

    // Initialize the onUnmounted logic by triggering the setter with 'undefined'.
    // This ensures the basic unmount functionality is always attached,
    // even if the consumer doesn't provide their own onUnmounted hook.
    pluginAdapter.onUnmounted = undefined;

    return pluginAdapter;
}
