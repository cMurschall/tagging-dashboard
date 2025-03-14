<template>
  <div class="card" style="width: 100%; max-width: 800px; margin: 0 auto;">
    <div class="card-body">
      <h5 class="card-title">Video Player</h5>
      <div class="card-img-top">
        <video-js ref="videoPlayer" class="vjs-default-skin" :options="videoOptions" @error="handleError"></video-js>
        <div id="thumbnail-preview"></div>
      </div>
      <div v-if="error" class="alert alert-danger mt-3">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, ref, watch, onMounted, onBeforeUnmount } from 'vue';
import { ApiPath, TestDriveVideoInfo } from '../services/Utilities';
import videojs from "video.js";
import "videojs-sprite-thumbnails";


interface VideoPlayerProps {
  videoInfo : TestDriveVideoInfo
}


const props = defineProps<VideoPlayerProps>()

const videoPlayer = ref<videojs.Player | undefined>(undefined)
const videoOptions = ref<videojs.PlayerOptions>({
  controls: true,
  autoplay: true,
  preload: 'auto',
  fluid: true,
  sources: [],
  aspectRatio: '16:9',
  responsive: true,
  controlBar: {
    volumePanel: {
      inline: false,
    },
  },
})


let lastProcessedSecond = -1;


const error = ref<string | undefined>(undefined)


const loadVideo = (videoInfo: TestDriveVideoInfo) => {
  if(!videoInfo.videoFileName) {
    error.value = "Video file name is missing.";
    return;
  }


  const encodedFileName = encodeURIComponent(videoInfo.videoFileName);
  const videoUrl = `${ApiPath}/player/video/${encodedFileName}`;
  error.value = undefined;

  videoOptions.value.sources = [{
    src: videoUrl,
    type: "video/mp4",
  }];
  console.log('videoOptions:', videoOptions.value);

  // videoOptions.aspectRatio  = `${videoInfo.videoWidth}:${videoInfo.videoHeight}`;


  if (videoPlayer.value) {
    videoPlayer.value.src(videoOptions.value.sources);
    // videoPlayer.value.options(videoOptions.value);
  }

  if (videoPlayer.value) {

    const encodedFileName = encodeURIComponent(videoInfo.videoSpriteInfo?.spriteFileName ?? '');
    const thumbnailUrl = `${ApiPath}/player/thumbnail/${encodedFileName}`;
    
    // setup sprite thumbnails
    const spriteThumbnailsOptions = {
      interval:videoInfo.videoSpriteInfo?.spriteInterval,
      url: thumbnailUrl,
      columns: videoInfo.videoSpriteInfo?.spriteColumns,
      rows: videoInfo.videoSpriteInfo?.spriteRows,
      width:videoInfo.videoSpriteInfo?.thumbnailWidth,
      height: videoInfo.videoSpriteInfo?.thumbnailHeight,
    }
    
    videoPlayer.value.spriteThumbnails(spriteThumbnailsOptions);
    console.log('spriteThumbnailsOptions:', spriteThumbnailsOptions);
  }
}

const handleError = () => {
  error.value = "Unable to load the video. Please try again.";
}

// Updated watch to avoid calling `loadVideo` prematurely
watch(() => props.videoInfo.videoFileName, (newValue) => {
  console.log('watched value:', newValue);
  // Call loadVideo only if the video player is initialized
  if (newValue && videoPlayer.value) {
    loadVideo(props.videoInfo);
  }
},
  { immediate: false } // Remove immediate to avoid preemptive execution
);


onMounted(() => {
  videoPlayer.value = videojs(videoPlayer.value, videoOptions.value, function () {
    console.log('Video player is ready');
    console.log('Video.js plugins:', videojs.getPlugins());
    console.log('Video.js player:', videoPlayer.value);


    videoPlayer.value.on('timeupdate', () => {
      // Get the current time in seconds (rounded down to the nearest second)
      const currentSecond = Math.floor(videoPlayer.value.currentTime());

      // Check if the current second is different from the last processed second
      if (currentSecond !== lastProcessedSecond) {
        lastProcessedSecond = currentSecond;

        // Example: Synchronize data to the current timestamp
        synchronizeData(currentSecond);
      }
    });


    // Ensure loadVideo is called only after the video player is ready
    if (props.videoInfo) {
      loadVideo(props.videoInfo);
    }
  });


})
onBeforeUnmount(() => {
  if (videoPlayer.value) {
    videoPlayer.value.dispose();
    videoPlayer.value = undefined;
  }
})



const synchronizeData = (currentSecond: number) => {
  //console.log('synchronizeData:', currentSecond)
}
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



#thumbnail-preview {
  position: absolute;
  bottom: 50px;
  left: 0;
  width: 120px;
  height: 90px;
  background-size: cover;
  background-position: center;
  display: none;
  z-index: 10;
}
</style>
