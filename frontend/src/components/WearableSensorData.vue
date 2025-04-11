<template>
  <div class="sensor-card">
    <div class="card-header">
      <h3>
        Wearable Sensor Data 
        <span class="info-icon">
          <i class="fa-solid fa-info-circle"></i>
          <span class="tooltip-text">This section provides data from wearable sensors for heart rate, SpO2, and more.</span>
        </span>
      </h3>
      <div class="time-selection">
        <label>
          <input type="radio" value="24hrs" v-model="selectedTimeframe" /> Last 24 Hrs
        </label>
        <label>
          <input type="radio" value="10days" v-model="selectedTimeframe" /> Last 10 Days
        </label>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="isLoading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading sensor data...</p>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error" class="error-container">
      <p>{{ error }}</p>
      <button @click="loadWearableData" class="retry-button">Retry</button>
    </div>

    <!-- Data display -->
    <div v-else>
      <!-- Custom Legend with Clickable Toggles -->
      <div class="legend">
        <div 
          v-for="(dataset, index) in datasets" 
          :key="index" 
          class="legend-item" 
          @click="toggleDataset(index)">
          <span 
            :style="{ backgroundColor: dataset.borderColor, border: dataset.hidden ? '2px solid #d1d5db' : 'none' }"
            class="legend-color"
          ></span>
          <span :class="{ 'legend-label': true, inactive: dataset.hidden }">{{ dataset.label }}</span>
        </div>
      </div>

      <!-- Line Chart Component -->
      <div class="chart-container">
        <Line :data="chartData" :options="chartOptions" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted, watch } from 'vue';
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale
} from 'chart.js';

ChartJS.register(Title, Tooltip, LineElement, PointElement, LinearScale, CategoryScale);

// Props for receiving patient data
const props = defineProps<{
  patient: {
    id: string;
  } | null;
}>();

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002';  // Match the API URL used elsewhere
const selectedTimeframe = ref("24hrs");
const isLoading = ref(true);
const error = ref<string | null>(null);

// Define our wearable data structure
interface WearableSensorData {
  heartRate: { 
    "24hrs": number[]; 
    "10days": { date: string; value: number }[] 
  };
  respiration: { 
    "24hrs": number[]; 
    "10days": { date: string; value: number }[] 
  };
  spo2: { 
    "24hrs": number[]; 
    "10days": { date: string; value: number }[] 
  };
  skinTemperature: { 
    "24hrs": number[]; 
    "10days": { date: string; value: number }[] 
  };
}

const sensorData = ref<WearableSensorData>({
  heartRate: { 
    "24hrs": [], 
    "10days": [] 
  },
  respiration: { 
    "24hrs": [], 
    "10days": [] 
  },
  spo2: { 
    "24hrs": [], 
    "10days": [] 
  },
  skinTemperature: { 
    "24hrs": [], 
    "10days": [] 
  }
});

// ✅ Reactive datasets to ensure proper binding
const datasets = reactive([
  {
    label: "Heart Rate",
    borderColor: "#3b82f6",
    hidden: false,
    yAxisID: 'yHeartRate'
  },
  {
    label: "Respiration",
    borderColor: "#ec4899",
    hidden: false,
    yAxisID: 'yRespiration'
  },
  {
    label: "SpO2",
    borderColor: "#10b981",
    hidden: false,
    yAxisID: 'ySpO2'
  },
  {
    label: "Skin Temperature",
    borderColor: "#8b5cf6",
    hidden: false,
    yAxisID: 'ySkinTemp'
  }
]);

// ✅ Async function to load wearable data from API
async function loadWearableData() {
  if (!props.patient?.id) {
    error.value = "No patient selected";
    isLoading.value = false;
    return;
  }

  isLoading.value = true;
  error.value = null;

  try {
    console.log(`Fetching wearable data for patient ${props.patient.id}`);
    const response = await fetch(`${apiBaseUrl}/api/patients/${props.patient.id}/wearable-data`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    sensorData.value = data;
    console.log('Loaded wearable sensor data from API');
  } catch (err) {
    console.error('Error loading wearable sensor data:', err);
    error.value = 'Failed to load sensor data. Please try again.';
    
    // If we have fallback data from the patient prop, use it
    if (props.patient && 'wearableSensorData' in props.patient) {
      sensorData.value = (props.patient as any).wearableSensorData;
      error.value = 'Using cached data (API unavailable)';
    }
  } finally {
    isLoading.value = false;
  }
}

// ✅ Dynamic Chart Data Binding with null checking
const chartData = computed(() => ({
  labels: selectedTimeframe.value === "24hrs"
    ? Array.from({ length: 24 }, (_, i) => `${i}:00`)
    : sensorData.value.heartRate["10days"].map(entry => entry.date).reverse() || [],
  datasets: datasets.map((dataset, index) => {
    const dataKey = Object.keys(sensorData.value)[index] as keyof WearableSensorData;
    const sensorDataValue = sensorData.value[dataKey];
    
    return {
      ...dataset,
      data: selectedTimeframe.value === "24hrs"
        ? sensorDataValue["24hrs"] || []
        : (sensorDataValue["10days"] || []).map(d => d.value),
      hidden: dataset.hidden
    };
  })
}));

// ✅ Dynamic Y-Axis Visibility Control
const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: { title: { display: true, text: "Time" } },
    yHeartRate: {
      type: 'linear',
      position: 'left',
      title: { display: true, text: "Heart Rate (bpm)" },
      display: !datasets[0].hidden,
    },
    ySpO2: {
      type: 'linear',
      position: 'left',
      title: { display: true, text: "SpO2 (%)" },
      display: !datasets[2].hidden,
    },
    yRespiration: {
      type: 'linear',
      position: 'right',
      title: { display: true, text: "Respiration (breaths/min)" },
      display: !datasets[1].hidden,
    },
    ySkinTemp: {
      type: 'linear',
      position: 'right',
      title: { display: true, text: "Skin Temperature (°C)" },
      display: !datasets[3].hidden,
    }
  },
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      enabled: true
    },
    datalabels: {
      display: false
    }
  }
}));

// ✅ Click Event to Toggle Datasets and Hide/Show Y-Axis
function toggleDataset(index: number) {
  datasets[index].hidden = !datasets[index].hidden;
}

// Watch for patient changes to reload data
watch(() => props.patient?.id, (newId, oldId) => {
  if (newId && newId !== oldId) {
    loadWearableData();
  }
});

// Load data on component mount
onMounted(() => {
  if (props.patient?.id) {
    loadWearableData();
  }
});
</script>

<style scoped>
.sensor-card {
  border: none;
  border-radius: 0;
  background-color: transparent;
  padding: 0;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #3b82f6;
  padding: 12px;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
  color: white;
}

.card-header h3 {
  font-weight: bold;
  font-size: 1rem;
  color: white;
}

.time-selection label {
  margin-right: 10px;
  font-size: 0.875rem;
  color: white;
}

.info-icon {
  position: relative;
  display: inline-flex;
  align-items: center;
  margin-left: 8px;
  cursor: pointer;
}

.tooltip-text {
  visibility: hidden;
  width: 220px;
  background-color: #555;
  color: #fff;
  text-align: center;
  border-radius: 6px;
  padding: 5px 8px;
  position: absolute;
  font-size: 0.75rem;
  z-index: 10;
  top: -5px;
  left: 105%;
  transform: translateX(-50%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.info-icon:hover .tooltip-text {
  visibility: visible;
  opacity: 1;
}

.legend {
  display: flex;
  gap: 15px;
  padding-top: 10px;
  font-size: 0.875rem;
  color: #1f2937;
}

.legend-item {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.legend-color {
  width: 14px;
  height: 14px;
  display: inline-block;
  margin-right: 6px;
  border-radius: 2px;
  transition: border 0.3s;
}

.legend-label {
  color: #1f2937;
  transition: opacity 0.3s;
}

.legend-label.inactive {
  opacity: 0.5;
}

.chart-container {
  height: 300px;
  width: 100%;
  margin-top: 10px;
}

/* Loading and error states */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 0;
  color: #64748b;
  font-size: 0.85rem;
  height: 300px;
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
  height: 300px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
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
</style>
