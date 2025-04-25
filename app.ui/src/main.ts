import { createApp } from 'vue';
import App from './App.vue';

import { createPinia } from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import { createBootstrap, } from 'bootstrap-vue-next';

export const pinia = createPinia();
pinia.use(piniaPluginPersistedstate)

export const bootstrap = createBootstrap();


// Import Bootstrap and BootstrapVue CSS files
import './assets/fonts/Geist/geist-all.css';
import './assets/fonts/GeistMono/geist-mono-all.css';

// Import your custom SCSS file (this should come after Bootstrap CSS so it can override styles)
import './globalStyles.scss';

// Import Bootstrap JavaScript functionality
import './../node_modules/bootstrap/dist/js/bootstrap.js';
import { getPluginManager } from './managers/pluginManager.js';


(async () => {
    await getPluginManager().loadExternalPlugins();

    const app = createApp(App);
    app.use(bootstrap); // Important
    app.use(pinia);

    app.mount('#app');
})();





