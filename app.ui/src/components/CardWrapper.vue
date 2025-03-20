<template>
  <div class="card h-100">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h5 class="mb-0">{{ title }}</h5>
      <button class="btn btn-sm btn-danger" @click="$emit('remove')">X</button>
    </div>
    <div class="card-body no-scrollbar">
      <slot />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, provide } from 'vue';

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
</style>