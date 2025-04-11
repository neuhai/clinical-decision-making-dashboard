<template>
    <div class="circle-progress">
      <svg viewBox="0 0 36 36" class="circular-chart">
        <path
          class="circle-bg"
          d="M18 2.0845
             a 15.9155 15.9155 0 0 1 0 31.831
             a 15.9155 15.9155 0 0 1 0 -31.831"
        />
        <path
          class="circle"
          :stroke-dasharray="dashArray"
          d="M18 2.0845
             a 15.9155 15.9155 0 0 1 0 31.831
             a 15.9155 15.9155 0 0 1 0 -31.831"
        />
        <text x="18" y="20.35" class="percentage">{{ value }}%</text>
      </svg>
      <p class="label">{{ label }}</p>
    </div>
  </template>
  
  <script setup>
  import { computed, defineProps } from 'vue';
  
  const props = defineProps({
    value: {
      type: Number,
      required: true,
    },
    max: {
      type: Number,
      default: 100,
    },
    label: {
      type: String,
      default: '',
    },
  });
  
  const percentage = computed(() => (props.value / props.max) * 100);
  const dashArray = computed(() => `${percentage.value}, 100`);
  </script>
  
  <style scoped>
  .circle-progress {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  
  .circular-chart {
    width: 100px;
    height: 100px;
    transform: rotate(-90deg);
  }
  
  .circle-bg {
    fill: none;
    stroke: #e6e6e6;
    stroke-width: 3.8;
  }
  
  .circle {
    fill: none;
    stroke: var(--highlight-color, #ff7070);
    stroke-width: 3.8;
    stroke-linecap: round;
    transition: stroke-dasharray 0.6s ease;
  }
  
  .percentage {
    fill: var(--text-color, #334155);
    font-size: 10px;
    text-anchor: middle;
    font-variant-caps: middle;
  }
  
  .label {
    font-size: 12px;
    color: var(--text-color, #334155);
    margin-top: 8px;
    text-align: center;
  }
  </style>
  