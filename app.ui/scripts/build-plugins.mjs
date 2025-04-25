// build-plugins.mjs
import { build } from 'vite';
import { readdirSync, statSync, copyFileSync, writeFileSync, mkdirSync, existsSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Required for __dirname in ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const pluginRoot = path.resolve(__dirname, '../plugins');
const outputRoot = path.resolve(__dirname, '../../app/static/plugins');

const pluginDirs = readdirSync(pluginRoot).filter(name => {
  const pluginPath = path.join(pluginRoot, name);
  return statSync(pluginPath).isDirectory();
});

for (const pluginName of pluginDirs) {
  const pluginPath = path.join(pluginRoot, pluginName);
  const configPath = path.join(pluginPath, 'vite.plugin.config.ts');
  const manifestSrc = path.join(pluginPath, 'manifest.json');
  const manifestDest = path.join(outputRoot, pluginName, 'manifest.json');

  console.log(`Looking for manifest at: ${manifestSrc}`);


  const pluginOutputDir = path.dirname(manifestDest);
  mkdirSync(pluginOutputDir, { recursive: true }); // Ensure the folder exists


  console.log(`Building plugin: ${pluginName}`);
  await build({ configFile: configPath });

  console.log(`Copying manifest to: ${manifestDest}`);
  copyFileSync(manifestSrc, manifestDest);
  console.log(`Done: ${pluginName}`);
}

const indexFile = path.join(outputRoot, 'plugin-index.json');
writeFileSync(indexFile, JSON.stringify(pluginDirs, null, 2));
console.log(`Generated plugin-index.json`);

