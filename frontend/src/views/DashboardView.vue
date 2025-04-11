<template>
  <div class="dashboard">
    <!-- Sidebar for patient selection -->
    <Sidebar @selectPatient="loadPatientData" />

    <div class="main-content">
      <!-- Display the selected patient's header and content -->
      <PatientHeader :patient="selectedPatient" />
      <HomepageContent 
        :patient="selectedPatient"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import Sidebar from '@/components/Sidebar.vue';
import PatientHeader from '@/components/PatientHeader.vue';
import HomepageContent from '@/components/HomepageContent.vue';
import { ref } from 'vue';

// Define the patient type with AI risk prediction and conversation log
interface Patient {
  id: string;
  name: string;
  age: number;
  gender: string;
  cancerType: string;
  stage: string;
  treatment: string;
  riskLevel: string;
  aiRiskPrediction: {
    riskScore: number;
    featureImportance: { label: string; value: number }[];
  };
  hospitalizations: { date: string; reason: string }[];
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
}

// State for holding the selected patient data
const selectedPatient = ref<Patient | null>(null);

// Function to handle patient selection and pass data from the sidebar
function loadPatientData(patient: Patient) {
  selectedPatient.value = patient;
}
</script>


<style scoped>
.dashboard {
  display: flex;
  height: 100vh;
}

.main-content {
  flex: 1;
  padding: 20px;
  background: white;
  display: flex;
  flex-direction: column;
}
</style>


  