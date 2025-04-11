<template>
  <div class="homepage">
    <div class="main-content">
      <div class="dashboard-grid">
        <div class="left-column">
          <PatientSection class="panel" :patient="patient" />
          <WearableSensorData class="panel" :patient="patient" />
          <DailySummary class="panel" />
        </div>

        <div class="right-column">
          <AiRiskPrediction class="panel" :patient="patient" />
          <!-- Correctly pass the conversationLog prop -->
          <ConversationLog 
            class="panel" 
            :conversationLog="patient?.conversationLog" 
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import PatientSection from '@/components/PatientSection.vue';
import AiRiskPrediction from '@/components/AiRiskPrediction.vue';
import WearableSensorData from '@/components/WearableSensorData.vue';
import DailySummary from '@/components/DailySummary.vue';
import ConversationLog from '@/components/ConversationLog.vue';

defineProps<{
  patient: {
    id: string;
    name: string;
    age: number;
    gender: string;
    cancerType: string;
    stage: string;
    treatment: string;
    riskLevel: string;
    aiRiskPrediction: {
      lastUpdated: string;
      riskScore: number;
      featureImportance: { label: string; value: number }[];
      historicalData?: { date: string; value: number }[];
    };
    wearableSensorData: {
      heartRate: { "24hrs": number[]; "10days": { date: string; value: number }[] };
      respiration: { "24hrs": number[]; "10days": { date: string; value: number }[] };
      spo2: { "24hrs": number[]; "10days": { date: string; value: number }[] };
      skinTemperature: { "24hrs": number[]; "10days": { date: string; value: number }[] };
    };
    conversationLog: {
      date: string;
      conversations: {
        [key: string]: { type: string; text: string; icon: string; experienced?: boolean }[];
      };
    };
  } | null;
}>();
</script>


<style scoped>
.homepage {
  display: flex;
  height: 100vh;
  background-color: #f3f4f6;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow-y: auto;
  width: 100%;
  box-sizing: border-box;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 2fr 2fr; 
  grid-template-rows: auto; 
  gap: 30px;
  padding: 20px;
  width: 100%;
  box-sizing: border-box;
}

.left-column, .right-column {
  display: grid;
  grid-template-rows: auto auto 1fr; /* This ensures the third item takes remaining space */
  gap: 20px;
}

.panel {
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  overflow: hidden; 
}
</style>



