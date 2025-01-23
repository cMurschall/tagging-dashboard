import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { createBootstrap } from 'bootstrap-vue-next';

import App from './App.vue';

// Import Bootstrap and BootstrapVue CSS files
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue-next/dist/bootstrap-vue-next.css';

// Import your custom SCSS file (this should come after Bootstrap CSS so it can override styles)
import './globalStyles.scss';

// Import Bootstrap JavaScript functionality
import 'bootstrap/dist/js/bootstrap.js';

const pinia = createPinia();
const bootstrap = createBootstrap();

const app = createApp(App);
app.use(bootstrap); // Important
app.use(pinia);

app.mount('#app');

import 'bootstrap/dist/js/bootstrap.js';
