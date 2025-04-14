import { createPinia } from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import { createBootstrap, useToastController } from 'bootstrap-vue-next';

export const pinia = createPinia();
pinia.use(piniaPluginPersistedstate)

export const bootstrap = createBootstrap();

export type SetCardTitleFn = (title: string) => void;
export type ShowToastFn = ReturnType<typeof useToastController>['show'];