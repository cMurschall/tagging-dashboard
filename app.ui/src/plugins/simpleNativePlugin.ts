
import { PluginServices, TaggingDashboardPlugin } from './../managers/pluginManager';

const simpleNativePlugin: TaggingDashboardPlugin = {
    create: (container: HTMLElement, pluginServices: PluginServices) => {
        // Create a simple DOM element.
        const elem = document.createElement('div');
        elem.innerHTML = `<h3>Hello from a simple plugin!</h3>
                      <p>Project info: ${JSON.stringify(pluginServices.getProjectInfo())}</p>`;
        container.appendChild(elem);
    },
    onMounted: () => {
        console.log('Simple plugin mounted');
    },
    onUnmounted: () => {
        console.log('Simple plugin unmounted');
    }
};

export default simpleNativePlugin;
