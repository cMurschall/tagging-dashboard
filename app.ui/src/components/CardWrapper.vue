<template>
  <div class="card h-100">
    <div class="card-header d-flex justify-content-between align-items-center smaller-header">
      <h6 class="mb-0">{{ title }}</h6>
      <button class="btn btn-sm btn-danger" @click="$emit('remove')">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                    class="feather feather-x">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
      </button>
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