import { BaseVisualization } from './../plugins/BaseVisualization';

export class PluginManager {
  private pluginInstances: Map<string, BaseVisualization> = new Map();
  private availablePlugins: Map<string, any> = new Map();

  constructor(private pluginDirectory: string) {}

  async loadPluginsMetadata(): Promise<void> {
    try {
      const response = await fetch(`${this.pluginDirectory}/plugins.json`);
      const pluginFiles: string[] = await response.json();

      for (const file of pluginFiles) {
        try {
          const module = await import(`${this.pluginDirectory}/${file}`);
          const { pluginInfo } = module;

          if (pluginInfo) {
            this.availablePlugins.set(pluginInfo.name, module);
            console.log(`Loaded plugin metadata: ${pluginInfo.name}`);
          }
        } catch (error) {
          console.error(`Failed to load plugin metadata ${file}:`, error);
        }
      }
    } catch (error) {
      console.error('Failed to load plugin metadata:', error);
    }
  }

  async loadAndInstantiatePlugin(pluginName: string, config: Record<string, any> = {}): Promise<void> {
    if (this.pluginInstances.has(pluginName)) return;

    const pluginModule = this.availablePlugins.get(pluginName);
    if (!pluginModule) return;

    try {
      const PluginClass = pluginModule.default;
      const pluginInstance = new PluginClass(config);
      this.pluginInstances.set(pluginName, pluginInstance);
      console.log(`Loaded and instantiated plugin: ${pluginName}`);
    } catch (error) {
      console.error(`Error instantiating plugin ${pluginName}:`, error);
    }
  }

  listAvailablePlugins(): string[] {
    return Array.from(this.availablePlugins.keys());
  }
}