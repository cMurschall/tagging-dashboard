import { defineConfig } from 'vite';
import path from 'path';


const pluginName = 'simplePlugin';
const outDir = path.resolve(__dirname, '../../../app/static/plugins', pluginName);
console.log(` Building plugin '${pluginName}' into: ${outDir}`);

export default defineConfig({
  build: {
    lib: {
      entry: path.resolve(__dirname, 'simplePlugin.ts'),
      name: 'SimplePlugin',
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