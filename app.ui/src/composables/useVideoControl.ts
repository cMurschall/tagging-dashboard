// src/composables/useVideoControl.ts
import { ref } from 'vue'
import { VideoPlayer } from '../components/plugins/VideoPlayer.vue'

const videoRef = ref<VideoPlayer | null>(null)
// Just a plain function reference, not reactive
let seekTo = (time: number) => { }


export function useVideoControl() {
  return {
    videoRef,
    get seekTo() {
      return seekTo
    },
    setSeekTo(fn: typeof seekTo) {
      seekTo = fn
    },
  }
}
