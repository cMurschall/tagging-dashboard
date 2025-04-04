import { createPinia } from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import { createBootstrap } from 'bootstrap-vue-next';

export const pinia = createPinia();
pinia.use(piniaPluginPersistedstate)

export const bootstrap = createBootstrap();
