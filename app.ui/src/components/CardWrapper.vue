<template>
  <div class="card h-100">
    <div class="card-header d-flex justify-content-between align-items-center smaller-header drag-target">

      <button @click="handleToggleMenu" class="btn btn-outline btn-sm  mx-1">
        <transition name="icon-transition" mode="out-in">
          <svg v-if="showMenu" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
          <!--!Font Awesome Free 6.7.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc.-->
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 512 512">
            <path
              d="M0 416c0 17.7 14.3 32 32 32l54.7 0c12.3 28.3 40.5 48 73.3 48s61-19.7 73.3-48L480 448c17.7 0 32-14.3 32-32s-14.3-32-32-32l-246.7 0c-12.3-28.3-40.5-48-73.3-48s-61 19.7-73.3 48L32 384c-17.7 0-32 14.3-32 32zm128 0a32 32 0 1 1 64 0 32 32 0 1 1 -64 0zM320 256a32 32 0 1 1 64 0 32 32 0 1 1 -64 0zm32-80c-32.8 0-61 19.7-73.3 48L32 224c-17.7 0-32 14.3-32 32s14.3 32 32 32l246.7 0c12.3 28.3 40.5 48 73.3 48s61-19.7 73.3-48l54.7 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-54.7 0c-12.3-28.3-40.5-48-73.3-48zM192 128a32 32 0 1 1 0-64 32 32 0 1 1 0 64zm73.3-64C253 35.7 224.8 16 192 16s-61 19.7-73.3 48L32 64C14.3 64 0 78.3 0 96s14.3 32 32 32l86.7 0c12.3 28.3 40.5 48 73.3 48s61-19.7 73.3-48L480 128c17.7 0 32-14.3 32-32s-14.3-32-32-32L265.3 64z" />
          </svg>

        </transition>
      </button>

      <h6 class="mb-0">{{ title }}</h6>

      <div class="d-flex justify-content-end align-items-center ">

        <button class="btn btn-outline-danger btn-sm  mx-1" @click="$emit('remove')">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
    </div>
    <div class="card-body no-scrollbar">
      <slot />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, inject } from 'vue';
import { PluginServices } from '../managers/pluginManager';
import { useObservable } from '../services/utilities';

export default defineComponent({
  name: 'CardWrapper',
  props: {
    title: {
      type: String,
      default: ''
    }
  },
  emits: ['remove'],
  setup(props) {


    const pluginService = inject<PluginServices>('pluginService');
    if (!pluginService) {
      throw new Error('Plugin service not found!');
    }

    const cardTitle = useObservable(pluginService.cardTitle$);
    cardTitle.value = props.title; // Set the initial title from props

    const showMenu = ref(false);

    const handleToggleMenu = () => {
      showMenu.value = !showMenu.value;
      pluginService.showMenu$.next(showMenu.value);
    };

    return { title: cardTitle, showMenu, handleToggleMenu };
  },
});
</script>


<style scoped lang="scss">
.no-scrollbar {
  overflow: auto;
  scrollbar-width: none; // Firefox
  -ms-overflow-style: none; // IE 10+

  &::-webkit-scrollbar {
    display: none; // Chrome, Safari, Opera
  }
}

.smaller-header {
  padding: 0.5rem 1rem;
  margin: 0;
}

// Transition for icons
.icon-transition {

  &-enter-active,
  &-leave-active {
    transition: all 0.2s ease;
  }

  &-enter-from,
  &-leave-to {
    opacity: 0;
    transform: scale(0.8);
  }

  &-enter-to,
  &-leave-from {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
