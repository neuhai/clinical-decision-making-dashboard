<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <h2>Patient List</h2>
    </div>

    <div v-if="isLoading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading patients...</p>
    </div>
    
    <div v-else-if="error" class="error-container">
      <p>{{ error }}</p>
      <button @click="loadPatients" class="retry-button">Retry</button>
    </div>

    <div v-else class="patients-list">
      <div 
        v-for="patient in filteredPatients" 
        :key="patient.id"
        :class="['patient-card', { active: selectedPatientId === patient.id }]"
        @click="selectPatient(patient)"
      >
        <div class="risk-indicator" :style="{ backgroundColor: getRiskColor(patient.riskLevel) }"></div>
        <div class="patient-info">
          <div class="patient-name">{{ patient.name }}</div>
          <div class="patient-details">
            {{ patient.age }} y.o. {{ patient.gender ? patient.gender.toLowerCase() : '' }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

interface Message {
  type: string;
  text: string;
  icon: string;
  experienced?: boolean;
}

interface Patient {
  id?: string;
  _id?: string;
  name: string;
  age: number;
  gender: string;
  cancerType?: string;
  stage?: string;
  treatment?: string;
  riskLevel: string;
  hospitalizations?: { date: string; reason: string }[];
  wearableSensorData?: {
    heartRate: { "24hrs": number[]; "10days": { date: string; value: number }[] };
    respiration: { "24hrs": number[]; "10days": { date: string; value: number }[] };
    spo2: { "24hrs": number[]; "10days": { date: string; value: number }[] };
    skinTemperature: { "24hrs": number[]; "10days": { date: string; value: number }[] };
  };
  aiRiskPrediction?: {
    lastUpdated: string;
    riskScore: number;
    featureImportance: { label: string; value: number }[];
  };
  conversationLog?: {
    date: string;
    conversations: {
      [key: string]: Message[];
    };
  };
}

const patients = ref<Patient[]>([]);
const selectedPatientId = ref<string | null>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002';
// Replace with your API URL
const selectedPatientData = ref<Patient | null>(null);
const emit = defineEmits(['selectPatient']);

// Load patients from the API
async function loadPatients() {
  isLoading.value = true;
  error.value = null;
  
  try {
    console.log('Fetching patients from API...');
    const response = await fetch(`${apiBaseUrl}/api/patients`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    patients.value = await response.json();
    console.log(`Loaded ${patients.value.length} patients`);
    
    // If we already had a selected patient, try to maintain that selection
    if (selectedPatientId.value && patients.value.find(p => p.id === selectedPatientId.value)) {
      fetchPatientDetails(selectedPatientId.value);
    }
  } catch (err) {
    console.error('Error loading patient data:', err);
    error.value = 'Failed to load patients. Please try again.';
    
    // Fall back to loading from local JSON if the API fails
    try {
      const response = await fetch('/src/assets/patients.json');
      patients.value = await response.json();
      console.log('Loaded patients from local JSON as fallback');
      error.value = 'Using offline data (API unavailable)';
    } catch (fallbackErr) {
      console.error('Even fallback loading failed:', fallbackErr);
    }
  } finally {
    isLoading.value = false;
  }
}

// Fetch full details for a specific patient
async function fetchPatientDetails(patientId: string) {
  if (!patientId) {
    console.error('Cannot fetch details: Patient ID is undefined');
    return;
  }

  try {
    console.log(`Fetching details for patient ${patientId}`);
    const response = await fetch(`${apiBaseUrl}/api/patients/${patientId}`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const patientData = await response.json();
    
    // Ensure the patient data has an id property
    if (!patientData.id && patientData._id) {
      patientData.id = patientData._id;
    }
    
    selectedPatientData.value = patientData;
    
    // Emit the selected patient with full details
    emit('selectPatient', patientData);
    
  } catch (err) {
    console.error(`Error fetching patient details for ID ${patientId}:`, err);
    
    // Fall back to the minimal data we already have
    const minimalPatient = patients.value.find(p => p.id === patientId || p._id === patientId);
    if (minimalPatient) {
      emit('selectPatient', minimalPatient);
    }
  }
}

onMounted(() => {
  loadPatients();
});

const filteredPatients = computed(() => {
  return patients.value.map(patient => {
    // Ensure each patient has an id property (use _id as fallback)
    if (!patient.id && patient._id) {
      patient.id = patient._id;
    }
    return patient;
  });
});

/**
 * Selects a patient and fetches full details
 */
const selectPatient = (patient: Patient) => {
  if (!patient || !patient.id) {
    console.warn('Attempted to select a patient with missing ID');
    return;
  }
  
  selectedPatientId.value = patient.id;
  
  // Fetch full patient details when selected
  fetchPatientDetails(patient.id);
};

/**
 * Determines the color associated with the patient's risk level.
 */
const getRiskColor = (riskLevel: string) => {
  return riskLevel === 'High' ? '#ef4444' : riskLevel === 'Moderate' ? '#f59e0b' : '#10b981';
};
</script>

<style scoped>
.sidebar {
  width: 200px;
  height: 100%;
  background: white;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.sidebar-header h2 {
  font-weight: 600;
  font-size: 1.2rem;
  color: #334155;
  margin: 0;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 0;
  color: #64748b;
  font-size: 0.85rem;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container {
  padding: 20px;
  text-align: center;
  color: #ef4444;
  font-size: 0.85rem;
}

.retry-button {
  margin-top: 10px;
  padding: 5px 10px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}

.patients-list {
  flex: 1;
  padding: 10px;
}

.patient-card {
  display: flex;
  align-items: center;
  padding: 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-bottom: 10px;
}

.patient-card.active {
  background-color: #e0f2fe;
}

.risk-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 12px;
}

.patient-info {
  display: flex;
  flex-direction: column;
}

.patient-name {
  font-weight: bold;
  font-size: 1rem;
  color: #334155;
}

.patient-details {
  font-size: 0.85rem;
  color: #64748b;
}
</style>

