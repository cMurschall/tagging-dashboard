<template>
  <div>
    <h2>Plugin Window Manager</h2>
    <button class="btn btn-primary" @click="openWindow('Scatter Plot', 'scatter-plot')">Open Scatter Plot</button>
    <button class="btn btn-primary" @click="openWindow('Map Visualization', 'map-visualization')">Open Map</button>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import WinBox from "winbox";

export default defineComponent({
  name: "WindowManager",
  methods: {
    openWindow(title: string, id: string) {
      // Check if the window is already open
      if (document.getElementById(id)) {
        console.log(`${title} window is already open.`);
        return;
      }

      // Create a new WinBox window
      new WinBox({
        title: title,
        id: id, // Unique ID for the window
        width: "600px",
        height: "400px",
        top: 50,
        left: 50,
        mount: document.createElement("div"), // Placeholder element for Vue components
        onclose: () => {
          console.log(`${title} window closed.`);
        },
      });

      // Dynamically mount a Vue component into the window
      this.mountPlugin(id);
    },
    mountPlugin(id: string) {
      import(`./plugins/${id}`).then((pluginModule) => {
        const placeholder = document.getElementById(id);
        if (placeholder) {
          const PluginComponent = pluginModule.default;
          const app = createApp(PluginComponent);
          app.mount(placeholder);
        }
      });
    },
  },
});
</script>

<style scoped>
h2 {
  margin-bottom: 20px;
}
button {
  margin-right: 10px;
}
</style>
