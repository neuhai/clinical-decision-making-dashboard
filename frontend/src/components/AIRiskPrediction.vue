<template>
  <div class="ai-risk-prediction">
    <div class="header">
      <div class="header-title">
        <h3>AI Risk Prediction</h3>
        <span class="info-icon">
          <i class="fa-solid fa-info-circle"></i>
          <span class="tooltip-text">This section provides AI-based risk predictions for cardiotoxicity.</span>
        </span>
      </div>
      <!-- Date selection -->
      <div class="date-picker">
        <input type="date" :value="selectedDate" @change="onDateChange" />
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="isLoading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading risk prediction data...</p>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error" class="error-container">
      <p>{{ error }}</p>
      <button @click="loadRiskData" class="retry-button">Retry</button>
    </div>

    <div v-else class="content">
      <!-- Risk Score Section -->
      <div class="charts-container">
        <div class="risk-score-section">
          <h4 class="section-title">
            Cardiotoxicity Risk Score 
            <span class="info-icon">
              <i class="fa-solid fa-info-circle"></i>
              <span class="tooltip-text">Details about cardiotoxicity risk scoring based on multiple health data sources.</span>
            </span>
          </h4>
          <div class="gauge-chart-wrapper">
            <div class="gauge-chart-container">
              <Doughnut 
                :data="gaugeData" 
                :options="gaugeOptions" 
                :key="`gauge-${displayedRiskScore}-${selectedDate}`" 
              />
              <p class="score-text" :style="{ color: getRiskScoreColor(displayedRiskScore) }">
                {{ displayedRiskScore }}%
              </p>
              <div class="assessment-type" v-if="isLastUpdatedDate">
                (Current Assessment)
              </div>
            </div>
            <div class="risk-description">
              <p>(The score predicts the <strong>6-month</strong> risk of cardiovascular complications based on <strong>EHR data</strong>, wearable sensors, and self-reported symptoms.)</p>
            </div>
          </div>
        </div>

        <!-- Feature Importance Section -->
        <div class="feature-importance-section">
          <h4 class="section-title">
            Feature Importance 
            <span class="info-icon">
              <i class="fa-solid fa-info-circle"></i>
              <span class="tooltip-text">Factors contributing to the risk prediction, weighted by importance.</span>
            </span>
          </h4>
          <Bar :data="featureImportanceData" :options="featureImportanceOptions" />
        </div>
      </div>
      
      <!-- Risk Score Line Chart Section with Legend -->
      <div class="line-chart-section">
        <h4 class="section-title">Risk Trend</h4>
        <Line :data="lineChartData" :options="lineChartOptions" />
        <!-- Add color legend -->
        <div class="risk-color-legend">
          <div v-for="(item, index) in riskColorLegend" :key="index" class="legend-item">
            <div class="color-dot" :style="{ backgroundColor: item.color }"></div>
            <span>{{ item.label }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue';
import { Doughnut, Bar, Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement
} from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, LineElement, PointElement);

interface HistoricalDataPoint {
  date: string;
  value: number;
}

interface RiskPredictionData {
  lastUpdated: string;
  riskScore: number;
  featureImportance: { label: string; value: number }[];
  historicalData?: HistoricalDataPoint[];
}

// Props: now only need the patient ID
const props = defineProps<{
  patient: {
    id: string;
  } | null;
}>();

// State variables
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'; // Match the API URL used elsewhere
const selectedDate = ref('');
const featureImportance = ref<{ label: string; value: number }[]>([]);
const allHistoricalData = ref<HistoricalDataPoint[]>([]);
const riskPrediction = ref<RiskPredictionData | null>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);

// Format date strings for comparison (MM/DD/YYYY to YYYY-MM-DD)
function formatDateForComparison(dateString: string): string {
  if (!dateString) return '';
  
  // Already in YYYY-MM-DD format
  if (/^\d{4}-\d{2}-\d{2}$/.test(dateString)) {
    return dateString;
  }
  
  // Convert MM/DD/YYYY to YYYY-MM-DD
  if (/^\d{2}\/\d{2}\/\d{4}$/.test(dateString)) {
    const parts = dateString.split('/');
    return `${parts[2]}-${parts[0].padStart(2, '0')}-${parts[1].padStart(2, '0')}`;
  }
  
  // Try to parse as date object
  try {
    const date = new Date(dateString);
    if (!isNaN(date.getTime())) {
      return date.toISOString().slice(0, 10);
    }
  } catch (e) {
    console.error('Error parsing date:', e);
  }
  
  return '';
}

// Async function to load risk prediction data
async function loadRiskData() {
  if (!props.patient?.id) {
    error.value = "No patient selected";
    isLoading.value = false;
    return;
  }

  isLoading.value = true;
  error.value = null;

  try {
    console.log(`Fetching risk prediction data for patient ${props.patient.id}`);
    const response = await fetch(`${apiBaseUrl}/api/patients/${props.patient.id}/risk-prediction`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    riskPrediction.value = data;
    
    // Initialize component data with the fetched values
    initializeData();
    
    console.log('Loaded risk prediction data from API');
  } catch (err) {
    console.error('Error loading risk prediction data:', err);
    error.value = 'Failed to load risk prediction data. Please try again.';
  } finally {
    isLoading.value = false;
  }
}

// Check if the currently selected date is the last updated date
const isLastUpdatedDate = computed(() => {
  if (!riskPrediction.value) return false;
  
  const lastUpdatedFormatted = formatDateForComparison(riskPrediction.value.lastUpdated);
  return selectedDate.value === lastUpdatedFormatted;
});

// The displayed risk score
const displayedRiskScore = computed(() => {
  if (!riskPrediction.value) return 0;
  
  // If it's the lastUpdated date, use the current risk score
  if (isLastUpdatedDate.value) {
    return riskPrediction.value.riskScore;
  }
  
  // Otherwise, find the historical data point for this date
  const dataPoint = allHistoricalData.value.find(point => point.date === selectedDate.value);
  if (dataPoint) {
    return dataPoint.value;
  }
  
  // Fallback to current score if no matching date
  return riskPrediction.value.riskScore;
});

// Function to get color based on risk score (more granular version)
function getRiskScoreColor(score: number): string {
  if (score <= 30) return '#10b981'; // Very low risk - bright green
  if (score <= 40) return '#34d399'; // Low risk - green
  if (score <= 50) return '#6ee7b7'; // Low-medium risk - light green
  if (score <= 60) return '#fcd34d'; // Medium risk - yellow
  if (score <= 70) return '#fb923c'; // Medium-high risk - orange
  if (score <= 80) return '#f87171'; // High risk - light red
  return '#ef4444'; // Very high risk - bright red
}

// Gauge Chart Configuration
const gaugeData = computed(() => ({
  labels: ['Risk Score', 'Remaining'],
  datasets: [
    {
      data: [displayedRiskScore.value, 100 - displayedRiskScore.value],
      backgroundColor: [getRiskScoreColor(displayedRiskScore.value), '#e5e7eb'],
      borderWidth: 0,
      circumference: 180,
      rotation: -90,
    }
  ]
}));

const gaugeOptions = {
  cutout: '70%',
  plugins: {
      legend: { display: false },
      tooltip: { enabled: false },
      datalabels: { display: false }
  },
  responsive: true,
  maintainAspectRatio: false,
  animation: {
    animateRotate: true,
    animateScale: true,
    duration: 500
  }
};

// Feature Importance Chart Configuration
const featureImportanceData = computed(() => ({
  labels: featureImportance.value.map(item => item.label),
  datasets: [{
      data: featureImportance.value.map(item => item.value),
      backgroundColor: '#3b82f6',
      borderRadius: 5
  }]
}));

const featureImportanceOptions = {
  responsive: true,
  indexAxis: 'y',
  plugins: {
      legend: { display: false },
      datalabels: {
          anchor: 'end',
          align: 'end',
          color: '#374151',
          font: { weight: 'bold' },
          formatter: (value: number) => `${value}%`
      }
  },
  scales: {
      x: { beginAtZero: true, max: 100, display: false },
      y: { ticks: { color: '#374151' } }
  }
};

// Line Chart for Risk Score Over Time
const lineChartData = computed(() => {
  if (!riskPrediction.value) {
    return {
      labels: [],
      datasets: [{
        label: 'Risk Score',
        data: [],
        fill: false,
        borderColor: '#6b7280',
        backgroundColor: 'rgba(248, 113, 113, 0.1)',
        borderWidth: 2,
        pointRadius: 6
      }]
    };
  }

  // Create a copy of the historical data
  const historicalCopy = [...allHistoricalData.value];

  // Find if there's a data point for the lastUpdated date
  const lastUpdatedFormatted = formatDateForComparison(riskPrediction.value.lastUpdated);
  const lastUpdatedIndex = historicalCopy.findIndex(point => point.date === lastUpdatedFormatted);

  // If there is a data point for lastUpdated, override its value with current risk score
  if (lastUpdatedIndex >= 0) {
    historicalCopy[lastUpdatedIndex].value = riskPrediction.value.riskScore;
  } else if (lastUpdatedFormatted) {
    // Otherwise, add the current risk score as a new data point
    historicalCopy.push({
      date: lastUpdatedFormatted,
      value: riskPrediction.value.riskScore
    });
  }

  // Sort by date
  const sortedData = historicalCopy.sort((a, b) => 
    new Date(a.date).getTime() - new Date(b.date).getTime()
  );

  // Format data for chart
  return {
    labels: sortedData.map(point => {
      const date = new Date(point.date);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }),
    datasets: [{
      label: 'Risk Score',
      data: sortedData.map(point => point.value),
      fill: false,
      borderColor: '#6b7280', // Neutral color for the line
      backgroundColor: 'rgba(248, 113, 113, 0.1)',
      borderWidth: 2,
      pointRadius: 6,
      pointBackgroundColor: (context) => {
        const index = context.dataIndex;
        const value = sortedData[index]?.value || 0;
        return getRiskScoreColor(value);
      },
      pointBorderColor: (context) => {
        const index = context.dataIndex;
        const value = sortedData[index]?.value || 0;
        return getRiskScoreColor(value);
      },
      pointHoverRadius: 8,
      segment: {
        borderColor: (context) => {
          // Color line segments based on the average risk level between two points
          const index = context.p1DataIndex;
          if (index >= sortedData.length - 1) return '#6b7280'; // Default for last segment
          
          const value1 = sortedData[index]?.value || 0;
          const value2 = sortedData[index + 1]?.value || 0;
          const avgValue = (value1 + value2) / 2;
          
          return getRiskScoreColor(avgValue);
        }
      }
    }]
  };
});

const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 2,
  scales: {
    x: { 
      title: { 
        display: true, 
        text: 'Date',
        font: { size: 12 },
        color: '#374151'
      } 
    },
    y: { 
      title: { 
        display: true, 
        text: 'Risk Score (%)' 
      }, 
      min: 0, 
      max: 100, 
      ticks: {
        stepSize: 20,
        color: '#374151'
      }
    }
  },
  plugins: { 
    legend: { display: false },
    tooltip: {
      enabled: true,
      callbacks: {
        label: (context) => {
          const index = context.dataIndex;
          const value = context.parsed.y;
          
          let riskLevel = "Unknown";
          if (value <= 30) riskLevel = "Very Low";
          else if (value <= 50) riskLevel = "Low";
          else if (value <= 70) riskLevel = "Medium";
          else riskLevel = "High";
          
          const point = allHistoricalData.value[index];
          const isCurrentAssessment = point && 
            point.date === formatDateForComparison(riskPrediction.value?.lastUpdated || '');
          
          return isCurrentAssessment 
            ? `Current Assessment: ${value}% (${riskLevel} Risk)` 
            : `Historical: ${value}% (${riskLevel} Risk)`;
        }
      }
    },
    datalabels: { display: false }
  }
};

// Add a legend to explain risk colors
const riskColorLegend = [
  { color: '#10b981', label: 'Low Risk (<50%)' },
  { color: '#fcd34d', label: 'Medium Risk (50-70%)' },
  { color: '#ef4444', label: 'High Risk (>70%)' }
];

// Initialize component on mount
onMounted(() => {
  if (props.patient?.id) {
    loadRiskData();
  }
});

// Function to initialize component data
function initializeData() {
  if (!riskPrediction.value) return;

  console.log('Initializing with current risk score:', riskPrediction.value.riskScore);
  
  // Set feature importance
  featureImportance.value = riskPrediction.value.featureImportance;
  
  // Format the lastUpdated date for consistency
  const lastUpdatedFormatted = formatDateForComparison(riskPrediction.value.lastUpdated);
  
  // Default to showing the current assessment
  selectedDate.value = lastUpdatedFormatted;
  
  // Process historical data
  if (riskPrediction.value.historicalData) {
    allHistoricalData.value = riskPrediction.value.historicalData.map(point => ({
      date: point.date,
      value: point.value
    }));
  } else {
    allHistoricalData.value = [];
  }
  
  // Make sure the line chart includes the current assessment
  updateChartData();
}

// Function to handle date change
function onDateChange(event: Event) {
  const input = event.target as HTMLInputElement;
  selectedDate.value = input.value;
  console.log('Date changed to:', selectedDate.value);
}

// Function to update chart data
function updateChartData() {
  if (!riskPrediction.value) return;
  
  const lastUpdatedFormatted = formatDateForComparison(riskPrediction.value.lastUpdated);
  
  // Make sure we have the lastUpdated date in our dataset
  const hasLastUpdated = allHistoricalData.value.some(point => point.date === lastUpdatedFormatted);
  
  if (!hasLastUpdated && lastUpdatedFormatted) {
    allHistoricalData.value.push({
      date: lastUpdatedFormatted,
      value: riskPrediction.value.riskScore
    });
  }
}

// Watch for changes to patient data
watch(() => props.patient?.id, (newId, oldId) => {
  if (newId && newId !== oldId) {
    loadRiskData();
  }
});
</script>

<style scoped>
.ai-risk-prediction {
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #f9fafb;
    padding: 0;
    overflow: visible;
    position: relative;
}

.content {
    padding: 16px;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    background-color: #3b82f6;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    color: white;
}

.header-title {
    display: flex;
    align-items: center;
    gap: 8px;
}

.header h3 {
    font-size: 1rem;
    font-weight: bold;
    color: white;
    margin: 0;
}

.date-picker input {
    padding: 5px;
    font-size: 0.875rem;
    border-radius: 4px;
    border: 1px solid #ddd;
}

.info-icon {
    cursor: pointer;
    position: relative;
    color: inherit;
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
    bottom: -5px;
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

.charts-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 20px;
}

.section-title {
    font-size: 1rem;
    color: #1f2937;
    margin-top: 0;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.gauge-chart-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.gauge-chart-container {
    position: relative;
    width: 200px;
    height: 100px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.score-text {
    position: absolute;
    bottom: 0px;
    font-size: 1.5rem;
    font-weight: bold;
}

.assessment-type {
    font-size: 0.75rem;
    color: #6b7280;
    margin-top: -5px;
}

.risk-description {
    text-align: center;
    font-size: 0.75rem;
    color: #6b7280;
    max-width: 250px;
}

.risk-color-legend {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 10px;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 0.75rem;
    color: #6b7280;
}

.color-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
}

.line-chart-section {
    margin-top: 20px;
    position: relative;
    height: 300px;
    max-height: 300px;
    width: 100%;
    overflow: hidden;
}

.line-chart-section > * {
    max-height: 100%;
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
  height: 400px;
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
  height: 400px;
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



