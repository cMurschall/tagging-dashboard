<template>
  <div>
    <h2>Available Plugins</h2>
    <ul class="list-group">
      <li
        v-for="pluginName in availablePlugins"
        :key="pluginName"
        class="list-group-item d-flex justify-content-between align-items-center"
      >
        {{ pluginName }}
        <button class="btn btn-primary btn-sm" @click="selectPlugin(pluginName)">
          Configure
        </button>
      </li>
    </ul>

    <div v-if="selectedPlugin" class="mt-4">
      <h3>Configure {{ selectedPlugin }}</h3>
      <div v-for="(option, key) in pluginConfigSchema" :key="key" class="mb-3">
        <label>{{ key }} ({{ option.type }})</label>
        <input
          v-if="option.type === 'string'"
          class="form-control"
          v-model="config[key]"
          :placeholder="option.default"
        />
        <input
          v-if="option.type === 'number'"
          class="form-control"
          v-model.number="config[key]"
          :placeholder="option.default"
        />
        <small class="text-muted">{{ option.description }}</small>
      </div>
      <button class="btn btn-success" @click="instantiatePlugin">
        Load Plugin
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { PluginManager } from './../services/PluginManager';

export default defineComponent({
  name: 'PluginUI',
  props: { pluginManager: Object as () => PluginManager },
  setup(props) {
    const availablePlugins = ref<string[]>([]);
    const selectedPlugin = ref<string | null>(null);
    const pluginConfigSchema = ref<Record<string, any> | null>(null);
    const config = ref<Record<string, any>>({});

    const loadMetadata = async () => {
      await props.pluginManager.loadPluginsMetadata();
      availablePlugins.value = props.pluginManager.listAvailablePlugins();
    };

    const selectPlugin = (pluginName: string) => {
      selectedPlugin.value = pluginName;
      pluginConfigSchema.value = props.pluginManager.getPluginConfigSchema(pluginName);
      config.value = Object.fromEntries(
        Object.entries(pluginConfigSchema.value || {}).map(([key, schema]) => [key, schema.default])
      );
    };

    const instantiatePlugin = async () => {
      if (selectedPlugin.value) {
        await props.pluginManager.loadAndInstantiatePlugin(selectedPlugin.value, config.value);
      }
    };

    loadMetadata();

    return { availablePlugins, selectedPlugin, pluginConfigSchema, config, selectPlugin, instantiatePlugin };
  },
});
</script>
