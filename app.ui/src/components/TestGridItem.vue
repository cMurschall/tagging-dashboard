<template>
  <div>
    <h4>Example Grid Item</h4>
    <button @click="updateTitle">Change Title</button>
    <div>Show menu: {{ showMenu }}</div>
    <button @click="seekTo(10)">Seek to 10 seconds</button>
    <button @click="seekTo(20)">Seek to 20 seconds</button>
  </div>

</template>

<script lang="ts">
import { defineComponent, inject } from 'vue';
import { useVideoControl } from './../composables/useVideoControl';

const { seekTo } = useVideoControl()

export default defineComponent({
  name: 'ChildComponent',
  data() {
    return {
      counter: 0
    };
  },
  props: {
    showMenu: {
      type: Boolean,
      default: false
    },
  },
  setup() {
    const setCardTitle = inject('setCardTitle') as (title: string) => void;




    return {
      updateTitle: () => setCardTitle('Updated Title from Child '),
      seekTo
    };
  },
  mounted() {
    console.log('Test grid item mounted');
  },
  unmounted() {
    console.log('Test grid item unmounted');
  }
});
</script>
