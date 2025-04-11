<template>
  <DashboardView />
</template>

<script setup>
import DashboardView from './views/DashboardView.vue';
</script>

<style>
:root {
  --primary-color: #3b82f6;
  --secondary-color: #64748b;
  --text-color: #334155;
  --border-color: #e2e8f0;
  --bg-color: #ffffff;
  --highlight-color: #ff7070;
}

#app {
  font-family: Arial, sans-serif;
  color: var(--text-color);
  background-color: #f7f9fc;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
