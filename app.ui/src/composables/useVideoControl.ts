// src/composables/useVideoControl.ts
import { ref } from 'vue'
import { VideoPlayer } from '../components/plugins/VideoPlayer.vue'


// Just a plain function reference, not reactive
const videoRef = ref<VideoPlayer | null>(null)


// This will eventually hold the "real" seekTo function
const seekToImpl = ref<(time: number) => void>(() => {
  console.warn('[useVideoControl] seekTo called before VideoPlayer is ready.')
})

// This function never changes, but it delegates to whatever is in `seekToImpl.value`
function seekTo(time: number) {
  seekToImpl.value(time)
}

export function useVideoControl() {
  return {
    videoRef,
    seekTo,
    setSeekTo(fn: (time: number) => void) {
      seekToImpl.value = fn
    },
  }
}