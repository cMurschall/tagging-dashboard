<template>
  <div class="card" style="width: 100%; max-width: 800px; margin: 0 auto;">
    <div class="card-body">
      <h5 class="card-title">Video Player</h5>
      <video ref="video" controls class="card-img-top" :src="videoUrl" @error="handleError">
        Your browser does not support the video tag.
      </video>
      <div v-if="error" class="alert alert-danger mt-3">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, ref, watch } from 'vue';
import { ApiPath } from '../services/Utilities';



interface VideoPlayerProps {
  videoSource: string | undefined;
}

const props = defineProps<VideoPlayerProps>()

const videoUrl = ref<string | undefined>(undefined)
const error = ref<string | undefined>(undefined)

const loadVideo = (filename: string) => {
  console.log('Loading video filename:', filename)
  const baseUrl = ApiPath; // Replace with your FastAPI server address
  const encodedFileName = encodeURIComponent(filename);
  videoUrl.value = `${baseUrl}/player/video/${encodedFileName}`;
  error.value = undefined;

  console.log('Loading video:', videoUrl.value);
}

const handleError = () => {
  error.value = "Unable to load the video. Please try again.";
}

watch(() => props.videoSource, (newValue) => {
  // log watched value
  console.log('watched value:', newValue)
  if (newValue) {
    loadVideo(newValue);
  }
}, { immediate: true })


</script>

<style scoped>
.card {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.card-title {
  text-align: center;
  margin-bottom: 15px;
}

.card-img-top {
  border-radius: 8px;
}

.alert {
  text-align: center;
}
</style>
