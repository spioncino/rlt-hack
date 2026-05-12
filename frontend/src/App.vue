<script setup lang="ts">
import Header from './components/Header.vue';
</script>

<template>
  <div class="app">
    <Header />

    <div class="content">
      <RouterView />
    </div>
  </div>
</template>

<style scoped>
.app {
  width: 100%;

  display: flex;
  align-items: center;
  flex-direction: column;

  gap: 48px;
}

.content {
  max-width: 1200px;
  width: 100%;
}
</style>
