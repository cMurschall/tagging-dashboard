<template>
  <div class="card h-100">
    <div class="card-header d-flex justify-content-between align-items-center smaller-header">
      <h6 class="mb-0">{{ title }}</h6>
      <button class="btn btn-sm btn-danger" @click="$emit('remove')">X</button>
    </div>
    <div class="card-body no-scrollbar">
      <slot />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, provide, watch } from 'vue';

export default defineComponent({
  name: 'CardWrapper',
  props: {
    title: {
      type: String,
      default: ''
    }
  },
  setup(props) {
    const cardTitle = ref(props.title);

    // Watch for prop updates (in case title changes dynamically)
    watch(() => props.title, (newTitle) => {
      cardTitle.value = newTitle;
    });

    // Provide the function to allow children to change the title
    provide('setCardTitle', (newTitle: string) => {
      cardTitle.value = newTitle;
    });

    return { title: cardTitle };
  }
});
</script>


<style scoped>
.no-scrollbar {
  overflow: auto;
  scrollbar-width: none;
  /* For Firefox */
  -ms-overflow-style: none;
  /* For IE 10+ */
}

.no-scrollbar::-webkit-scrollbar {
  display: none;
  /* For Chrome, Safari, and Opera */
}

.smaller-header {
  padding: 0.5rem 1rem;
  margin: 0;
}
</style>