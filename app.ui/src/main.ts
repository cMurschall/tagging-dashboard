import { createApp } from 'vue';
import App from './App.vue';

// Import Bootstrap and BootstrapVue CSS files
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue-3/dist/bootstrap-vue-3.css';

// Import your custom SCSS file (this should come after Bootstrap CSS so it can override styles)
import './globalStyles.scss';

// Import Bootstrap JavaScript functionality
import 'bootstrap/dist/js/bootstrap.js';

import BootstrapVue3 from 'bootstrap-vue-3';

app = createApp(App);
app.use(BootstrapVue3);
app.mount('#app');

import 'bootstrap/dist/js/bootstrap.js';
