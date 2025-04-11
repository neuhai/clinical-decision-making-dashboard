<template>
  <div :class="['patient-section', { fullscreen: isFullscreen }]">
    <div v-if="!patient" class="no-data-message">
      <p>Please select a patient to view their details</p>
    </div>
    
    <div v-else class="patient-info-grid">
      <!-- Left Column: Patient Information -->
      <div class="patient-details">
        <p><strong>Cancer Type:</strong> {{ patient.cancerType || 'N/A' }}</p>
        <p><strong>Cancer Stage:</strong> {{ patient.stage || 'N/A' }}</p>
        <p><strong>Treatment Type:</strong> {{ patient.treatment || 'N/A' }}</p>
        <p><strong>Risk Level:</strong> <span :class="`risk-level ${getRiskClass(patient.riskLevel)}`">{{ patient.riskLevel }}</span></p>
      </div>

      <!-- Right Column: Hospitalizations -->
      <div>
        <h3 class="hospitalizations-header">Hospitalizations:</h3>
        <div class="hospitalizations">
          <ul v-if="patient.hospitalizations && patient.hospitalizations.length > 0" class="hospitalization-list">
            <li v-for="entry in patient.hospitalizations" :key="entry.date">
              <strong>{{ entry.date }}</strong> - {{ entry.reason }}
            </li>
          </ul>
          <div v-else class="no-hospitalizations">
            No hospitalizations recorded.
          </div>
        </div>
      </div>
    </div>
    
    <!-- Zoom Toggle Button -->
    <button class="zoom-btn" @click="toggleFullscreen">
      <i v-if="isFullscreen" class="fa-solid fa-compress"></i>
      <i v-else class="fa-solid fa-expand"></i>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

// Ensure patient is passed as a prop
interface Patient {
  id?: string;
  name?: string;
  cancerType?: string;
  stage?: string;
  treatment?: string;
  riskLevel?: string;
  hospitalizations?: { date: string; reason: string }[];
}

const props = defineProps<{
  patient: Patient | null;
}>();

const isFullscreen = ref(false);

function toggleFullscreen() {
  isFullscreen.value = !isFullscreen.value;
}

function getRiskClass(riskLevel?: string) {
  if (!riskLevel) return 'risk-none';
  
  switch (riskLevel.toLowerCase()) {
    case 'high':
      return 'risk-high';
    case 'moderate':
      return 'risk-moderate';
    case 'low':
      return 'risk-low';
    default:
      return 'risk-none';
  }
}
</script>

<style scoped>
.patient-section {
  position: relative;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9fafb;
  transition: all 0.3s ease-in-out;
}

.patient-section.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: white;
  z-index: 1000;
  overflow-y: auto;
  padding: 40px;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
}

.no-data-message {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 150px;
  font-style: italic;
  color: #6b7280;
  background-color: #f3f4f6;
  border-radius: 6px;
}

.patient-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.patient-details p {
  margin: 8px 0;
  line-height: 1.5;
}

.hospitalizations-header {
  margin-bottom: 8px;
  font-size: 1.2rem;
  font-weight: bold;
  color: #1f2937;
}

.hospitalizations {
  overflow-y: auto;
  max-height: 120px;
  background-color: #f3f4f6;
  border-radius: 6px;
  padding: 10px;
}

.hospitalization-list {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.hospitalization-list li {
  padding: 8px;
  border-bottom: 1px solid #e5e7eb;
}

.hospitalization-list li:last-child {
  border-bottom: none;
}

.no-hospitalizations {
  padding: 12px;
  font-style: italic;
  color: #6b7280;
  text-align: center;
}

.risk-level {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.risk-high {
  background-color: #fee2e2;
  color: #dc2626;
}

.risk-moderate {
  background-color: #fef3c7;
  color: #d97706;
}

.risk-low {
  background-color: #d1fae5;
  color: #10b981;
}

.risk-none {
  background-color: #e5e7eb;
  color: #6b7280;
}

.zoom-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #555;
  padding: 8px;
  border-radius: 50%;
  transition: background-color 0.3s;
}

.zoom-btn:hover {
  background-color: rgba(0, 0, 0, 0.1);
}
</style>
  
  