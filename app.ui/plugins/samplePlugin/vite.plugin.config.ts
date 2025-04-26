import { defineConfig } from 'vite';
import path from 'path';


const pluginName = path.basename(__dirname);
const outDir = path.resolve(__dirname, '../../../app/static/plugins', pluginName);
console.log(`Building sample plugin '${pluginName}' into: ${outDir}`);

export default defineConfig({
  build: {
    lib: {
      entry: path.resolve(__dirname, 'samplePlugin.ts'),
      name: 'SamplePlugin',
      fileName: pluginName,
      formats: ['es'],
    },
    outDir: outDir,
    emptyOutDir: true,
    rollupOptions: {
      external: ['vue'],
      output: {
        globals: {
          vue: 'Vue',
        },
      },
    },
  }
});