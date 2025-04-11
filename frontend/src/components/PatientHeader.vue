<template>
  <div class="header">
    <div class="patient-info">
      <div class="avatar">
        <i class="fas fa-user"></i>
      </div>
      <div>
        <h1>{{ patient?.name || 'No Patient Selected' }}</h1>
        <p v-if="patient">{{ patient.age }} y.o. / {{ patient.gender }}</p>
        <p v-else class="select-patient-text">Please select a patient from the sidebar</p>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab"
        :class="['tab', { active: selectedTab === tab }]"
        @click="selectTab(tab)"
      >
        {{ tab }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

interface Patient {
  name: string;
  age: number;
  gender: string;
}

const props = defineProps<{
  patient: Patient | null;
}>();

const tabs = ['Homepage', 'Quick View', 'Medications', 'Results'];
const selectedTab = ref(tabs[0]);

const emit = defineEmits(['tabSelected']);

function selectTab(tab: string) {
  selectedTab.value = tab;
  emit('tabSelected', tab);
}
</script>

<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background-color: #f3f4f6;
  border-bottom: 1px solid #e5e7eb;
  width: 100%;
  box-sizing: border-box;
}

.patient-info {
  display: flex;
  align-items: center;
}

.avatar {
  width: 40px;
  height: 40px;
  background-color: #d1d5db;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  font-size: 1.5rem;
  color: white;
}

.patient-info h1 {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
  color: #1f2937;
}

.patient-info p {
  margin: 0;
  font-size: 1rem;
  color: #6b7280;
}

.select-patient-text {
  font-style: italic;
  color: #9ca3af;
}

.tabs {
  display: flex;
  gap: 8px;
}

.tab {
  padding: 6px 12px;
  font-size: 1rem;
  font-weight: bold;
  color: #1d4ed8;
  background-color: transparent;
  border: 1px solid #1d4ed8;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.tab.active {
  background-color: #1d4ed8;
  color: white;
  border-color: #1d4ed8;
}
</style>
  
  
  