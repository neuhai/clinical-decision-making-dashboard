<template>
  <div class="risk-prediction">
    <div class="header">
      <h3>Risk Assessment</h3>
      <div class="risk-level" :class="riskLevelClass">
        {{ riskLevel }}
      </div>
    </div>

    <div class="risk-content">
      <!-- Circle Progress for Risk Score -->
      <div class="score-section">
        <CircleProgress 
          :value="riskScore" 
          :color="riskColor"
          label="Cardiotoxicity Risk" 
        />
        <div class="score-details">
          <p>Last updated: {{ lastUpdated }}</p>
          <p>Previous score: {{ previousScore }}%</p>
          <span class="score-change" :class="scoreChangeClass">
            <i :class="scoreChangeIcon"></i>
            {{ scoreChange }}%
          </span>
        </div>
      </div>

      <!-- Feature Importance Chart -->
      <div class="feature-importance">
        <h4>Contributing Factors</h4>
        <div v-for="feature in sortedFeatures" 
             :key="feature.name" 
             class="feature-bar">
          <div class="feature-info">
            <span class="feature-name">{{ feature.name }}</span>
            <span class="feature-value">{{ feature.value }}%</span>
          </div>
          <div class="bar-container">
            <div class="bar-fill" 
                 :style="{ width: `${feature.value}%`, backgroundColor: feature.color }">
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import CircleProgress from './CircleProgress.vue';

interface Feature {
  name: string;
  value: number;
  color: string;
}

// Dummy data
const riskScore = ref(75);
const previousScore = ref(68);
const lastUpdated = ref(new Date().toLocaleString());

const features = ref<Feature[]>([
  { name: 'Heart Rate Variability', value: 85, color: '#ef4444' },
  { name: 'QT Interval', value: 72, color: '#f97316' },
  { name: 'Left Ventricular EF', value: 65, color: '#eab308' },
  { name: 'Troponin Levels', value: 58, color: '#84cc16' },
  { name: 'BNP Levels', value: 45, color: '#14b8a6' }
]);

// Computed properties
const sortedFeatures = computed(() => {
  return [...features.value].sort((a, b) => b.value - a.value);
});

const scoreChange = computed(() => {
  return (riskScore.value - previousScore.value).toFixed(1);
});

const scoreChangeClass = computed(() => {
  return {
    'increase': scoreChange.value > 0,
    'decrease': scoreChange.value < 0
  };
});

const scoreChangeIcon = computed(() => {
  return scoreChange.value > 0 
    ? 'fas fa-arrow-up' 
    : 'fas fa-arrow-down';
});

const riskLevel = computed(() => {
  if (riskScore.value >= 75) return 'High Risk';
  if (riskScore.value >= 50) return 'Moderate Risk';
  return 'Low Risk';
});

const riskLevelClass = computed(() => {
  if (riskScore.value >= 75) return 'high';
  if (riskScore.value >= 50) return 'moderate';
  return 'low';
});

const riskColor = computed(() => {
  if (riskScore.value >= 75) return '#ef4444';
  if (riskScore.value >= 50) return '#f97316';
  return '#84cc16';
});
</script>

<style scoped>
.risk-prediction {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

h3 {
  margin: 0;
  color: var(--text-color);
  font-size: 1.2rem;
}

.risk-level {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 0.9rem;
  font-weight: 500;
}

.risk-level.high {
  background-color: #fef2f2;
  color: #ef4444;
}

.risk-level.moderate {
  background-color: #fff7ed;
  color: #f97316;
}

.risk-level.low {
  background-color: #f0fdf4;
  color: #84cc16;
}

.risk-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.score-section {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 15px;
  background: #f8fafc;
  border-radius: 8px;
}

.score-details {
  flex: 1;
}

.score-details p {
  margin: 5px 0;
  color: var(--secondary-color);
  font-size: 0.9rem;
}

.score-change {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
  font-size: 0.9rem;
}

.score-change.increase {
  color: #ef4444;
}

.score-change.decrease {
  color: #84cc16;
}

.feature-importance {
  padding: 15px;
  background: #f8fafc;
  border-radius: 8px;
}

h4 {
  margin: 0 0 15px 0;
  color: var(--secondary-color);
  font-size: 1rem;
}

.feature-bar {
  margin-bottom: 12px;
}

.feature-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  font-size: 0.9rem;
}

.feature-name {
  color: var(--text-color);
}

.feature-value {
  color: var(--secondary-color);
  font-weight: 500;
}

.bar-container {
  height: 8px;
  background-color: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  transition: width 0.6s ease;
}
</style>
  