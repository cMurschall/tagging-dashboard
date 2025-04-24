import { createApp, App, Component, nextTick } from 'vue';
import { PluginServices, TaggingDashboardPlugin } from '../managers/pluginManager';




/**
 * Creates an adapter for a Vue 3 component to fit the TaggingDashboardPlugin interface.
 *
 * @param VueComponent - The Vue 3 component definition (e.g., imported from an .vue file).
 * @param rootProps - Optional props to pass to the root Vue component instance.
 * @returns An object conforming to the TaggingDashboardPlugin interface.
 */
export function createVuePluginAdapter(    VueComponent: Component): TaggingDashboardPlugin {

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

            // Make the pluginService available to the Vue component and its children
            // via Vue's provide/inject mechanism
            vueAppInstance.provide('pluginService', pluginService);

            // --- Optional: Add other global configurations if needed ---
            // vueAppInstance.use(router);
            // vueAppInstance.config.globalProperties.$myGlobal = ...

            // Mount the Vue application to the provided container element
            vueAppInstance.mount(container);

            // Call the user-defined onMounted hook *after* the app is mounted.
            // Using nextTick ensures it runs after Vue's initial DOM updates.
            if (userOnMounted) {
               nextTick(userOnMounted);
               // Or, if immediate call after mount() is sufficient:
               // userOnMounted();
            }
        },

        // Use getters and setters to capture the hooks provided by the consumer
        // *after* the adapter function has returned the plugin object.
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
            // Wrap the provided hook with the necessary Vue cleanup logic.
            // This ensures vueAppInstance.unmount() is always called.
            userOnUnmounted = () => {
                // 1. Call the user's cleanup logic first (if provided)
                if (hook) {
                    try {
                        hook();
                    } catch (error) {
                        console.error("Error executing plugin onUnmounted hook:", error);
                    }
                }

                // 2. Perform the Vue app unmounting
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
