import { defineConfig } from 'vite';
import Components from 'unplugin-vue-components/vite'
import { BootstrapVueNextResolver } from 'bootstrap-vue-next'
import vue from '@vitejs/plugin-vue';

// https://vite.dev/config/
export default defineConfig({
    plugins: [
        vue(),
        Components({ resolvers: [BootstrapVueNextResolver()] })
    ],
    build: {
        sourcemap: true,
        outDir: './../app/static',
    },
    css: {
        preprocessorOptions: {
          scss: {
            quietDeps: true, // Suppresses deprecation warnings from node_modules
          },
        },
      },
});
