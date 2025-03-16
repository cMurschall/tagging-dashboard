import { createApp } from 'vue';
import App from './App.vue';

import {pinia, bootstrap} from "./plugins/AppPlugins";

// Import Bootstrap and BootstrapVue CSS files
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue-next/dist/bootstrap-vue-next.css';

// Import your custom SCSS file (this should come after Bootstrap CSS so it can override styles)
import './globalStyles.scss';

// Import Bootstrap JavaScript functionality
import './../node_modules/bootstrap/dist/js/bootstrap.js';



const app = createApp(App);
app.use(bootstrap); // Important
app.use(pinia);

app.mount('#app');


