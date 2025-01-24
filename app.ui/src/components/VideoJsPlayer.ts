import videojs from 'video.js';
import { defineComponent, h, ref, onMounted, onBeforeUnmount, PropType } from 'vue';

export default defineComponent({
  name: 'VideoJsPlayer',
  props: {
    options: {
      type: Object as PropType<Record<string, any>>,
      default: () => ({})
    }
  },
  setup(props) {
    const videoPlayerRef = ref<HTMLVideoElement | null>(null);
    let player: videojs.Player | null = null;

    onMounted(() => {
      if (videoPlayerRef.value) {
        player = videojs(videoPlayerRef.value, props.options, function () {
          this.log('onPlayerReady');
        });
      }
    });

    onBeforeUnmount(() => {
      if (player) {
        player.dispose();
      }
    });

    return () => 
      h('div', [
        h('video', {
          ref: videoPlayerRef,
          class: 'video-js'
        })
      ]);
  }
});