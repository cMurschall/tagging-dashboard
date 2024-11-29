<template>
  <div class="container">
    <h1 class="my-4">Tagging Dashboard</h1>

  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import PluginUI from './PluginUI.vue';
import { PluginManager } from './../services/PluginManager';

export default defineComponent({
  name: 'Dashboard',
  components: { PluginUI },
  setup() {
    const pluginManager = new PluginManager('/public/plugins');
    pluginManager.loadPluginsMetadata();
    return { pluginManager };
  },
});
</script>

<style>
body {
  background-color: #f8f9fa;
}
</style>
