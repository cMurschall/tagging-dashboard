<template>
    <div>
        <h4>Example Grid Item</h4>
        <button @click="updateTitle">Change Title</button>
    </div>
    
  </template>

<script lang="ts">
import { defineComponent, inject } from 'vue';

export default defineComponent({
  name: 'ChildComponent',
  data() {
    return {
      counter : 0
    };
  },
  props: {
  },
  setup() {
    const setCardTitle = inject('setCardTitle') as (title: string) => void;


    return {
      updateTitle: () => setCardTitle('Updated Title from Child ')
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

