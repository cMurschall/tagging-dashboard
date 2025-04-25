// build-plugins.mjs
import { build } from 'vite';
import {
  readdirSync,
  statSync,
  copyFileSync,
  writeFileSync,
  mkdirSync,
  existsSync
} from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Parse CLI args
const args = process.argv.slice(2);
const isDev = args.includes('--dev');
const isProd = args.includes('--prod') || !isDev;

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const pluginRoot = path.resolve(__dirname, '../plugins');
const outputRoot = path.resolve(__dirname, '../../app/static/plugins'); // always build here

console.log(`🔧 Building plugins in ${isDev ? 'development' : 'production'} mode`);
console.log(`📁 Build output goes to: ${outputRoot}`);

const pluginDirs = readdirSync(pluginRoot).filter(name => {
  const pluginPath = path.join(pluginRoot, name);
  return statSync(pluginPath).isDirectory();
});

for (const pluginName of pluginDirs) {
  const pluginPath = path.join(pluginRoot, pluginName);
  const configPath = path.join(pluginPath, 'vite.plugin.config.ts');
  const manifestSrc = path.join(pluginPath, 'manifest.json');

  const builtJsFile = path.join(outputRoot, pluginName, `${pluginName}.js`);
  const manifestBuilt = path.join(outputRoot, pluginName, 'manifest.json');

  if (!existsSync(manifestSrc)) {
    console.warn(`⚠️ No manifest found for plugin '${pluginName}', skipping`);
    continue;
  }

  console.log(`⚙️ Building plugin: ${pluginName}`);
  await build({ configFile: configPath });

  console.log(`📦 Plugin built into: ${path.join(outputRoot, pluginName)}`);

  if (isDev) {
    console.log(`↩️ Copying built files back to plugin source folder for dev`);

    const pluginFolderDev = path.join(pluginRoot, pluginName);
    const jsDest = path.join(pluginFolderDev, `${pluginName}.js`);
    const manifestDest = path.join(pluginFolderDev, 'manifest.json');

    try {
      copyFileSync(builtJsFile, jsDest);
      // copyFileSync(manifestBuilt, manifestDest);
      console.log(`✅ Copied to: ${pluginFolderDev}`);
    } catch (err) {
      console.error(`❌ Failed to copy back to plugin folder: ${pluginName}`, err);
    }
  }
}

// Generate plugin-index.json in both prod and dev
const pluginIndex = JSON.stringify(pluginDirs, null, 2);
const indexProd = path.join(outputRoot, 'plugin-index.json');
const indexDev = path.join(pluginRoot, 'plugin-index.json');

writeFileSync(indexProd, pluginIndex);
writeFileSync(indexDev, pluginIndex);

console.log(`📝 Generated plugin-index.json in both:\n → ${indexProd}\n → ${indexDev}`);
console.log('✅ All plugins built successfully!');
