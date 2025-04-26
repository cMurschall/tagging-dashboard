<template>
  <div>
    <h4>Example Grid Item.</h4>
    <div>Id: {{ id }}</div>
    <button @click="updateTitle">Change Title</button>
    <div>Show menu: {{ showMenu }}</div>
    <div>Counter: {{ pluginState.counter }}</div>
    <button @click="pluginState.counter++">Increment Counter</button>
    <button @click="seekTo(10)">Seek to 10 seconds</button>
    <button @click="seekTo(20)">Seek to 20 seconds</button>
  </div>

</template>

<script lang="ts">
import { defineComponent, inject } from 'vue';
// import { useVideoControl } from '../../composables/useVideoControl';
import { PluginServices } from '../../managers/pluginManager';
import { useObservable } from '../../core/utilities/utilities';



type PluginState = {
  counter: number;
}


export default defineComponent({
  name: 'ChildComponent',
  data() {
    return {
      pluginState: {
        counter: 0
      } as PluginState
    };
  },

  setup() {

    const pluginService = inject<PluginServices>('pluginService');
    if (!pluginService) {
      throw new Error('Plugin service not found!');
    }

    const id = pluginService.getId();
    const showMenu =useObservable(pluginService.showMenu$);


    return {
      updateTitle: () => pluginService.cardTitle$.next('Updated Title from Child ' + Math.random().toFixed(2)),
      seekTo: pluginService.getVideoControl().seekTo,
      pluginService,
      id,
      showMenu,
    };
  },
  mounted() {
    this.pluginState = this.pluginService.getPluginState() as PluginState || this.pluginState;
    // Set the card title when the component is mounted
    console.log('Test grid item mounted.');

  },
  unmounted() {
    console.log('Test grid item unmounted');
  },
  watch: {
    pluginState: {
      handler(newValue) {
        this.pluginService.savePluginState(newValue);
      },
      deep: true
    }
  },
});
</script>
