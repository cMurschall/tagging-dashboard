<template>
  <div>
    <div>
      <video ref="videoElement" class="video-js" :options="videoOptions" @error="handleError"></video>
      <div id="thumbnail-preview"></div>
    </div>
    <div v-if="error" class="alert alert-danger mt-3">
      {{ error }}
    </div>
    <!-- <div v-if="isDevMode()">
      <span>{{ currentSimulationTimeString }}</span>
      <pre>{{ props.videoInfo }}</pre>
    </div> -->
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, inject } from 'vue';
import { ApiPath, TestDriveVideoInfo, isDevMode, clamp } from '../../core/utilities/utilities';
// import { useVideoControl } from './../../composables/useVideoControl'
import videojs from "video.js";
import "videojs-sprite-thumbnails";

import { FrameByFrameButton } from '../../core/frameByFrameButton';
import { PluginServices } from '@/types/plugin';
import { VideoPlayer } from '@/types/video';


// Register the component with Video.js, so it can be used in players.
videojs.registerComponent('FrameByFrameButton', FrameByFrameButton);


// Inject the function from the parent
const pluginService = inject<PluginServices>('pluginService');
if (!pluginService) {
  throw new Error('Plugin service not found!');
}




type PlayerOptions = typeof videojs.options;


const videoElement = ref<HTMLVideoElement | null>(null); // Reference to the html video element
const videoPlayer = ref<VideoPlayer | undefined>(undefined); // Reference to the video player instance



const videoOptions = ref<PlayerOptions>({
  controls: true,
  autoplay: true,
  preload: 'auto',
  muted: true,
  fluid: true,
  sources: [],
  aspectRatio: '16:9',
  responsive: true,
  playbackRates: [0.5, 1, 1.5, 2],
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
    pluginService.cardTitle$.next(`Player: ${videoInfo.videoFileName}`);
  }
}

const handleError = () => {
  error.value = "Unable to load the video. Please try again.";
}


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
    pluginService.getVideoControl().setSeekTo((simulationTime: number) => {
      if (videoPlayer.value) {
        const simulationStart = pluginService.getProjectInfo()?.testDriveVideoInfo?.videoSimulationTimeStartS ?? 0;

        const videoTime = simulationTime - simulationStart
        console.log('Seeking video to:', videoTime, 'seconds');


        // Ensure the new time is within the video duration
        const duration = videoPlayer.value.duration();
        if (!duration) {
          console.warn('Video duration is not available yet.');
          return;
        }
        const clampedTime = clamp(videoTime, 0, duration);
        videoPlayer.value.currentTime(clampedTime);

        // if the video is paused, update the time immediately
        // This is to ensure that the time is updated even if the video is paused
        if (videoPlayer.value.paused()) {
          updateTime();
        }
      }
    });


    // const roundingPrecisionMs = 300; // Define the rounding precision in milliseconds
    const updateTime = () => {
      const currentTime = videoPlayer.value?.currentTime() ?? 0;
      const simulationStart = pluginService.getProjectInfo()?.testDriveVideoInfo?.videoSimulationTimeStartS ?? 0;
      synchronizeData(currentTime, simulationStart);
    };


    videoPlayer.value?.on('timeupdate', updateTime);
    videoPlayer.value?.on('seeked', updateTime);
    videoPlayer.value?.on('pause', updateTime);



    videoPlayer.value?.getChild('ControlBar')?.addChild('FrameByFrameButton', {
      fps: pluginService.getProjectInfo()?.testDriveVideoInfo?.videoFrameRate,
      value: +10
    });
    videoPlayer.value?.getChild('ControlBar')?.addChild('FrameByFrameButton', {
      fps: pluginService.getProjectInfo()?.testDriveVideoInfo?.videoFrameRate,
      value: (pluginService.getProjectInfo()?.testDriveVideoInfo?.videoFrameRate ?? 30)
    });
    videoPlayer.value?.getChild('ControlBar')?.addChild('FrameByFrameButton', {
      fps: pluginService.getProjectInfo()?.testDriveVideoInfo?.videoFrameRate,
      value: -1 * (pluginService.getProjectInfo()?.testDriveVideoInfo?.videoFrameRate ?? 30)
    });
    videoPlayer.value?.getChild('ControlBar')?.addChild('FrameByFrameButton', {
      fps: pluginService.getProjectInfo()?.testDriveVideoInfo?.videoFrameRate,
      value: -10
    });

    // remove VolumePanel from the control bar
    const volumePanel = videoPlayer.value?.getChild('ControlBar')?.getChild('VolumePanel');
    if (volumePanel) {
      videoPlayer.value?.getChild('ControlBar')?.removeChild(volumePanel);
    }

    // Ensure loadVideo is called only after the video player is ready
    const videoInfo = pluginService.getProjectInfo()?.testDriveVideoInfo;
    if (videoInfo) {
      loadVideo(videoInfo);
    }
  }) as VideoPlayer; // Cast the player to the custom VideoPlayer type


})
onBeforeUnmount(() => {
  if (videoPlayer.value) {
    videoPlayer.value.dispose();
    videoPlayer.value = undefined;
  }
  if (pluginService.simulationTime) {
    pluginService.simulationTime.next(0); // Reset the observable when the component is destroyed
  }
})



const synchronizeData = (currentSecond: number, simulationStart: number) => {


  const simulationTimeInSeconds = simulationStart + currentSecond

  if (isDevMode()) {
    const simulationTime_Minutes = Math.floor(simulationTimeInSeconds / 60);
    const simulationTime_Seconds = simulationTimeInSeconds % 60;
    const simulationTime_Milliseconds = simulationTimeInSeconds * 1000 % 1000;

    const videoFps = pluginService.getProjectInfo()?.testDriveVideoInfo?.videoFrameRate ?? 30;
    const frameCount = Math.floor(simulationTimeInSeconds * videoFps);

    const timeString = `${simulationTime_Minutes.toFixed(0).padStart(2, '0')}:${simulationTime_Seconds.toFixed(0).padStart(2, '0')}.${simulationTime_Milliseconds.toFixed(0).padStart(3, '0')}`;

    currentSimulationTimeString.value = `Simulation time: ${simulationTimeInSeconds.toFixed(3)}s - from video: ${timeString}. Frame: ${frameCount}`;

  }

  pluginService.simulationTime.next(simulationTimeInSeconds);

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
