
import { PluginServices, TaggingDashboardPlugin } from '../../src/managers/pluginManager';

const samplePlugin: TaggingDashboardPlugin = {
    create: (container: HTMLElement, pluginServices: PluginServices) => {
        // Create a simple DOM element.
        const elem = document.createElement('div');
        elem.innerHTML = `<h3>Hello from a sample plugin!</h3>
                      <p>Project info:</p>
                      <pre>${JSON.stringify(pluginServices.getProjectInfo(), null, 2)}</pre>
                      `;
        container.appendChild(elem);
    },
    onMounted: () => {
        console.log('Sample plugin mounted');
    },
    onUnmounted: () => {
        console.log('Sample plugin unmounted');
    }
};

export default samplePlugin;
