<template>
  <div>
    <div>
      <video ref="videoElement" class="video-js" :options="videoOptions" @error="handleError"></video>
      <div id="thumbnail-preview"></div>
    </div>
    <div v-if="error" class="alert alert-danger mt-3">
      {{ error }}
    </div>
    <div v-if="isDevMode()">
      <span>{{ currentSimulationTimeString }}</span>
      <pre>{{ props.videoInfo }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount, inject } from 'vue';
import { ApiPath, TestDriveVideoInfo, isDevMode } from '../../services/utilities';
import { Observable } from './../../observable';
import { useVideoControl } from './../../composables/useVideoControl'
import videojs from "video.js";
import "videojs-sprite-thumbnails";
import Player from 'video.js/dist/types/player';
import { FrameByFrameButton } from '../../services/frameByFrameButton';



// Register the component with Video.js, so it can be used in players.
videojs.registerComponent('FrameByFrameButton', FrameByFrameButton);



// Inject the function from the parent
const setCardTitle = inject('setCardTitle') as (title: string) => void;

interface VideoPlayerProps {
  videoInfo: TestDriveVideoInfo,
  // simulationTimeObservable: Observable<number>
}

export interface VideoPlayer extends Player {
  spriteThumbnails: (options: any) => void;
}

type PlayerOptions = typeof videojs.options;
const props = defineProps<VideoPlayerProps>()

const videoElement = ref<HTMLVideoElement | null>(null); // Reference to the html video element
const videoPlayer = ref<VideoPlayer | undefined>(undefined); // Reference to the video player instance

const { videoRef, setSeekTo } = useVideoControl()

const videoOptions = ref<PlayerOptions>({
  controls: true,
  autoplay: true,
  preload: 'auto',
  muted: true,
  fluid: true,
  sources: [],
  aspectRatio: '16:9',
  responsive: true,
  controlBar: {
    volumePanel: {
      inline: false,

    },
    remainingTimeDisplay: {
      displayNegative: false,
    }
  },
})


const error = ref<string | undefined>(undefined)
const currentSimulationTimeString = ref<string>('');



const simulationTimeObservable = inject<Observable<number>>('simulationTimeObservable');
if (!simulationTimeObservable) {
  throw new Error('simulationTimeObservable not provided');
}



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



    // Define the actual seekTo logic
    setSeekTo((simulationTime: number) => {
      if (videoPlayer.value) {
        const newTime = simulationTime - (props?.videoInfo?.videoSimulationTimeStartS ?? 0)
        console.log('Seeking video to:', newTime, 'seconds');
        videoPlayer.value.currentTime(newTime);
      }
    });


    // const roundingPrecisionMs = 300; // Define the rounding precision in milliseconds
    const updateTime = () => {
      const currentTime = videoPlayer.value?.currentTime() ?? 0;
      synchronizeData(currentTime, props.videoInfo.videoSimulationTimeStartS ?? 0);
    };


    videoPlayer.value?.on('timeupdate', updateTime);
    videoPlayer.value?.on('seeked', updateTime);
    videoPlayer.value?.on('pause', updateTime);



    videoPlayer.value?.getChild('ControlBar')?.addChild('FrameByFrameButton', {
      fps: props?.videoInfo?.videoFrameRate,
      value: +10
    });
    videoPlayer.value?.getChild('ControlBar')?.addChild('FrameByFrameButton', {
      fps: props?.videoInfo?.videoFrameRate,
      value: (props?.videoInfo?.videoFrameRate ?? 30)
    });
    videoPlayer.value?.getChild('ControlBar')?.addChild('FrameByFrameButton', {
      fps: props?.videoInfo?.videoFrameRate,
      value: -1 * (props?.videoInfo?.videoFrameRate ?? 30)
    });
    videoPlayer.value?.getChild('ControlBar')?.addChild('FrameByFrameButton', {
      fps: props?.videoInfo?.videoFrameRate,
      value: -10
    });

    // remove VolumePanel from the control bar
    const volumePanel = videoPlayer.value?.getChild('ControlBar')?.getChild('VolumePanel');
    if (volumePanel) {
      videoPlayer.value?.getChild('ControlBar')?.removeChild(volumePanel);
    }




    // Ensure loadVideo is called only after the video player is ready
    if (props.videoInfo) {
      loadVideo(props.videoInfo);
    }
  }) as VideoPlayer; // Cast the player to the custom VideoPlayer type


  videoRef.value = videoPlayer.value; // Set the videoRef to the player instance


})
onBeforeUnmount(() => {
  if (videoPlayer.value) {
    videoPlayer.value.dispose();
    videoPlayer.value = undefined;
  }
  if(simulationTimeObservable){
    simulationTimeObservable.next(0); // Reset the observable when the component is destroyed
  }
})



const synchronizeData = (currentSecond: number, simulationStart: number) => {


  const simulationTimeInSeconds = simulationStart + currentSecond

  if (isDevMode()) {
    const simulationTime_Minutes = Math.floor(simulationTimeInSeconds / 60);
    const simulationTime_Seconds = simulationTimeInSeconds % 60;
    const simulationTime_Milliseconds = simulationTimeInSeconds * 1000 % 1000;

    const frameCount = Math.floor(simulationTimeInSeconds * (props.videoInfo.videoFrameRate ?? 30));

    const timeString = `${simulationTime_Minutes.toFixed(0).padStart(2, '0')}:${simulationTime_Seconds.toFixed(0).padStart(2, '0')}.${simulationTime_Milliseconds.toFixed(0).padStart(3, '0')}`;

    currentSimulationTimeString.value = `Simulation time: ${simulationTimeInSeconds.toFixed(3)}s - from video: ${timeString}. Frame: ${frameCount}`;

  }

  simulationTimeObservable.next(simulationTimeInSeconds);

}



</script>

<style lang="scss" scoped>
.vjs-fbf {
  border: 1px solid white;
  padding: 2px 3px;
  border-radius: 2px;
}

/* CSS Grid - Clip toolbar - mobile */
@media only screen and (max-width: 576px) {

  .video-js .vjs-control {
    width: 2.5em;
  }

}
</style>
