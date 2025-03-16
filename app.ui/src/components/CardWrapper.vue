<template>
    <div class="card h-100">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">{{ title }}</h5>
        <button class="btn btn-sm btn-danger" @click="$emit('remove')">X</button>
      </div>
      <div class="card-body">
        <!-- Default slot: where we place the child component -->
        <slot />
      </div>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent } from 'vue';
  
  export default defineComponent({
    name: 'CardWrapper',
    props: {
      title: {
        type: String,
        default: ''
      }
    },
    emits: ['remove']
  });
  </script>
  
  <style scoped>
  /* You can add or override some Bootstrap styles here if desired */
  </style>
  