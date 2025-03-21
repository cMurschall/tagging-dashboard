<template>
  <div>
    <div>
      <video ref="videoElement" class="video-js" :options="videoOptions" @error="handleError"></video>
      <div id="thumbnail-preview"></div>
    </div>
    <div v-if="error" class="alert alert-danger mt-3">
      {{ error }}
    </div>
    <div>
{{ currentSimulationTimeString }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, ref, watch, onMounted, onBeforeUnmount, inject } from 'vue';
import { ApiPath, TestDriveVideoInfo } from '../services/Utilities';
import { Observable } from './../observable';
import videojs from "video.js";
import "videojs-sprite-thumbnails";
import Player from 'video.js/dist/types/player';

// Inject the function from the parent
const setCardTitle = inject('setCardTitle') as (title: string) => void;

interface VideoPlayerProps {
  videoInfo: TestDriveVideoInfo,
  simulationTimeObservable: Observable<number>
}

interface VideoPlayer extends Player {
  spriteThumbnails: (options: any) => void;
}

type PlayerOptions = typeof videojs.options;
const props = defineProps<VideoPlayerProps>()

const videoElement = ref<HTMLVideoElement | null>(null); // Reference to the html video element
const videoPlayer = ref<VideoPlayer | undefined>(undefined); // Reference to the video player instance



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
const currentSimulationTimeString = ref<string>('');


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


  if (videoPlayer.value) {
    videoPlayer.value.src(videoOptions.value.sources);
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

  if (videoPlayer.value) {
    setCardTitle(`Player: ${videoInfo.videoFileName}`);
  }
}

const handleError = () => {
  error.value = "Unable to load the video. Please try again.";
}

// Updated watch to avoid calling `loadVideo` prematurely
watch(() => props.videoInfo.videoFileName, (newValue) => {
  // Call loadVideo only if the video player is initialized
  if (newValue && videoPlayer.value) {
    loadVideo(props.videoInfo);
  }
},
  { immediate: false } // Remove immediate to avoid preemptive execution
);


onMounted(() => {
  if (!videoElement.value) {
    console.error('Video element not found');
    return;
  }

  videoPlayer.value = videojs(videoElement.value, videoOptions.value, function () {
    console.log('Video player is ready');
    console.log('Video.js plugins:', videojs.getPlugins());
    console.log('Video.js player:', videoPlayer.value);

    const roundingPrecisionMs = 300; // Define the rounding precision in milliseconds

    videoPlayer.value?.on('timeupdate', () => {
      const currentTime = videoPlayer.value?.currentTime() ?? 0;
      const roundedTime = Math.floor(currentTime * (1000 / roundingPrecisionMs)) / (1000 / roundingPrecisionMs); // round to specified precision

      // Get the current time in seconds (rounded down to the nearest second)

      // Check if the current second is different from the last processed second
      if (roundedTime !== lastProcessedSecond) {
        lastProcessedSecond = roundedTime;

        // Example: Synchronize data to the current timestamp
        synchronizeData(roundedTime, props.videoInfo.videoSimulationTimeStartS ?? 0);
      }
    });


    // Ensure loadVideo is called only after the video player is ready
    if (props.videoInfo) {
      loadVideo(props.videoInfo);
    }
  }) as VideoPlayer; // Cast the player to the custom VideoPlayer type


})
onBeforeUnmount(() => {
  if (videoPlayer.value) {
    videoPlayer.value.dispose();
    videoPlayer.value = undefined;
  }
})



const synchronizeData = (currentSecond: number, simulationStart: number) => {


  const simulationTime = simulationStart + currentSecond

  currentSimulationTimeString.value = `Simulation time from video: ${new Date(simulationTime * 1000).toISOString().substring(11, 23)} - ${simulationTime.toFixed(3)}s`;

  if (!props.simulationTimeObservable.next) {
    Object.setPrototypeOf(props.simulationTimeObservable, Observable.prototype);
  }
  props.simulationTimeObservable.next(simulationTime);

}

</script>

<style lang="scss" scoped></style>
