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
import { defineComponent, inject, PropType } from 'vue';
import { useVideoControl } from '../../composables/useVideoControl';
import { SetCardTitleFn } from '../../plugins/AppPlugins';
import { PluginServices } from '../../managers/pluginManager';


const { seekTo } = useVideoControl()

type PluginState = {
  counter: number;
}

const isPluginState = (obj: any): obj is PluginState => {
  return typeof obj === 'object' && 'counter' in obj;
};

export default defineComponent({
  name: 'ChildComponent',
  data() {
    return {
      pluginState: {
        counter: 0
      } as PluginState
    };
  },
  props: {
    showMenu: {
      type: Boolean,
      default: false
    },
    id: {
      type: String,
      default: ''
    },
    pluginState: {
      type: Object as PropType<PluginState>,
      default: () => ({ counter: 0 }),
    }
  },
  setup() {
    const setCardTitle = inject<SetCardTitleFn>('setCardTitle') ?? (() => { });
    const pluginService = inject<PluginServices>('pluginService');
    if (!pluginService) {
      throw new Error('Plugin service not found!');
    }


    return {
      updateTitle: () => setCardTitle('Updated Title from Child ' + Math.random().toFixed(2)),
      seekTo,
      pluginService
    };
  },
  mounted() {
    console.log('Test grid item mounted.');
    // copy the plugin state from the props to the local state
    if (this.$props.pluginState && isPluginState(this.$props.pluginState)) {
      console.log('Updating plugin state from props:', { ...this.$props.pluginState });
      this.pluginState = { ...this.$props.pluginState };
    }
  },
  unmounted() {
    console.log('Test grid item unmounted');
  },
  watch: {
    pluginState: {
      handler(newValue) {
        this.pluginService.savePluginState(this.id, newValue);
      },
      deep: true
    }
  },
});
</script>
