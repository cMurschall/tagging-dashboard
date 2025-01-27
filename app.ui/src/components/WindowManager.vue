<template>
  <div>
    <h2>Plugin Window Manager</h2>
    <button class="btn btn-primary" @click="openWindow('Scatter Plot', 'scatter-plot')">Open Scatter Plot</button>
    <button class="btn btn-primary" @click="openWindow('Map Visualization', 'map-visualization')">Open Map</button>
  </div>
</template>

<script lang="ts">

</script>

<style scoped>
h2 {
  margin-bottom: 20px;
}
button {
  margin-right: 10px;
}
</style>
