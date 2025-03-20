<template>
  <div>
    <div>
      <video ref="videoPlayer" class="video-js" :options="videoOptions" @error="handleError"></video>
      <div id="thumbnail-preview"></div>
    </div>
    <div v-if="error" class="alert alert-danger mt-3">
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, ref, watch, onMounted, onBeforeUnmount } from 'vue';
import { ApiPath, TestDriveVideoInfo } from '../services/Utilities';
import videojs from "video.js";
import "videojs-sprite-thumbnails";
import { Observable } from './../observable';



interface VideoPlayerProps {
  videoInfo: TestDriveVideoInfo,
  simulationTimeObservable: Observable<number>
}

type PlayerOptions = typeof videojs.options;
const props = defineProps<VideoPlayerProps>()

const videoPlayer = ref<videojs.Player | undefined>(undefined)
const videoOptions = ref<PlayerOptions>({
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
  if (!videoInfo.videoFileName) {
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
      interval: videoInfo.videoSpriteInfo?.spriteInterval,
      url: thumbnailUrl,
      columns: videoInfo.videoSpriteInfo?.spriteColumns,
      rows: videoInfo.videoSpriteInfo?.spriteRows,
      width: videoInfo.videoSpriteInfo?.thumbnailWidth,
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
        synchronizeData(currentSecond, props.videoInfo.videoSimulationTimeStartS ?? 0);
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



const synchronizeData = (currentSecond: number, simulationStart: number) => {

  const simulationTime = simulationStart + currentSecond
  //const simulationMinutes = Math.floor(simulationTime / 60);
  //const simulationSeconds = simulationTime - simulationMinutes * 60;


  // console.log('synchronizeData:', {
  //   currentSecond,
  //   simulationStart,
  //   simulationTime,
  //   formattedTime: `${simulationMinutes}:${simulationSeconds}`
  // })
  props.simulationTimeObservable.next(simulationTime);

}
</script>

<style lang="scss" scoped></style>
