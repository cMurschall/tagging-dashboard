<template>
  <div class="card h-100">
    <div class="card-header d-flex justify-content-between align-items-center smaller-header">
      <div @click="showMenu = !showMenu" style="cursor: pointer;">
        <svg v-if="!showMenu" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
          class="feather feather-menu">
          <line x1="3" y1="12" x2="21" y2="12"></line>
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
          class="feather feather-x">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </div>

      <h6 class="mb-0">{{ title }}</h6>



      <div class="d-flex justify-content-end align-items-center ">
        <button class="btn btn-outline-dark btn-sm mx-1" @click="handleToggleMoveLock">
          <svg v-if="!isMoveLocked" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
            fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
            aria-label="Move Handle">

            <line x1="12" y1="3" x2="12" y2="21"></line>
            <line x1="3" y1="12" x2="21" y2="12"></line>

            <polyline points="9 6 12 3 15 6"></polyline>
            <polyline points="9 18 12 21 15 18"></polyline>
            <polyline points="6 9 3 12 6 15"></polyline>
            <polyline points="18 9 21 12 18 15"></polyline>
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
            aria-label="Move Locked Handle">


            <g opacity="0.5">
              <line x1="12" y1="3" x2="12" y2="21"></line>
              <line x1="3" y1="12" x2="21" y2="12"></line>

              <polyline points="9 6 12 3 15 6"></polyline>
              <polyline points="9 18 12 21 15 18"></polyline>
              <polyline points="6 9 3 12 6 15"></polyline>
              <polyline points="18 9 21 12 18 15"></polyline>
            </g>
          </svg>
        </button>



        <button class="btn btn-outline-danger btn-sm  mx-1" @click="$emit('remove')">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
            class="feather feather-x">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
    </div>
    <div class="card-body no-scrollbar">
      <slot :showMenu="showMenu" />
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
  emits: ['remove', 'move-lock-changed'],
  setup(props, { emit }) {
    const cardTitle = ref(props.title);

    const showMenu = ref(false);
    const isMoveLocked = ref(true);

    // Watch for prop updates (in case title changes dynamically)
    watch(() => props.title, (newTitle) => {
      cardTitle.value = newTitle;
    });

    // Provide the function to allow children to change the title
    provide('setCardTitle', (newTitle: string) => {
      cardTitle.value = newTitle;
    });

    // Function to handle move lock toggle
    const handleToggleMoveLock = () => {
      isMoveLocked.value = !isMoveLocked.value;
      // Emit an event to notify parent component about the move lock state change
      emit('move-lock-changed', isMoveLocked.value);
    };

    return { title: cardTitle, showMenu, isMoveLocked, handleToggleMoveLock};
  },
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