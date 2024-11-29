<template>
  <div>
    <video ref="video" controls @timeupdate="onTimeUpdate">
      <source src="simulation.mp4" type="video/mp4" />
    </video>
  </div>
</template>

<script lang="ts">
export default {
  methods: {
    onTimeUpdate() {
      const currentTime = this.$refs.video.currentTime;
      this.$emit('time-update', currentTime);
    },
  },
};
</script>
