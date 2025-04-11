<template>
  <div class="chart-container">
    <div class="chart-header">
      <div class="title-section">
        <h3>Wearable Sensor Data</h3>
        <div class="vital-signs">
          <span class="vital-sign heart-rate">
            <i class="fas fa-heartbeat"></i> {{ currentHeartRate }} bpm
          </span>
          <span class="vital-sign spo2">
            <i class="fas fa-lungs"></i> {{ currentSpO2 }}% SpO2
          </span>
          <span class="vital-sign respiration">
            <i class="fas fa-wind"></i> {{ currentRespiration }} br/min
          </span>
        </div>
      </div>
      <div class="time-controls">
        <button 
          v-for="period in timePeriods" 
          :key="period.value"
          :class="['time-button', { active: selectedPeriod === period.value }]"
          @click="handlePeriodChange(period.value)"
        >
          {{ period.label }}
        </button>
      </div>
    </div>
    
    <div class="chart">
      <LineChart
        :data="displayData"
        :margin="{ top: 20, right: 30, left: 40, bottom: 20 }"
        @mouseenter="handleChartHover"
        @mouseleave="handleChartLeave"
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis 
          dataKey="time" 
          stroke="#64748b"
          :tick="{ fill: '#64748b' }"
        />
        <YAxis 
          yAxisId="vitals"
          stroke="#64748b"
          :tick="{ fill: '#64748b' }"
          :domain="['dataMin - 5', 'dataMax + 5']"
        />
        <YAxis 
          yAxisId="spo2"
          orientation="right"
          domain={[90, 100]}
          stroke="#64748b"
          :tick="{ fill: '#64748b' }"
        />
        <Tooltip :content="CustomTooltip" />
        <Legend />
        <Line
          type="monotone"
          dataKey="heartRate"
          stroke="#3b82f6"
          strokeWidth={2}
          dot={false}
          yAxisId="vitals"
          name="Heart Rate (bpm)"
          activeDot={{ r: 6 }}
        />
        <Line
          type="monotone"
          dataKey="respiration"
          stroke="#ef4444"
          strokeWidth={2}
          dot={false}
          yAxisId="vitals"
          name="Respiration Rate"
          activeDot={{ r: 6 }}
        />
        <Line
          type="monotone"
          dataKey="spo2"
          stroke="#10b981"
          strokeWidth={2}
          dot={false}
          yAxisId="spo2"
          name="SpO2 (%)"
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watchEffect, defineComponent, h } from 'vue';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';

interface SensorReading {
  time: string;
  heartRate: number;
  respiration: number;
  spo2: number;
  timestamp: Date;
}

interface TimePeriod {
  label: string;
  value: string;
}

// Custom tooltip component using Vue's render function
const CustomTooltip = defineComponent({
  props: {
    active: Boolean,
    payload: Array,
    label: String
  },
  setup(props) {
    return () => {
      if (props.active && props.payload && props.payload.length) {
        return h('div', { class: 'custom-tooltip' }, [
          h('p', { class: 'label' }, `Time: ${props.label}`),
          ...props.payload.map((pld: any) =>
            h('p', { key: pld.dataKey, style: { color: pld.color } }, `${pld.name}: ${pld.value}`)
          )
        ]);
      }
      return null;
    };
  }
});

// Generate dummy data for different time periods
const generateDummyData = (hours: number): SensorReading[] => {
  const data: SensorReading[] = [];
  const now = new Date();
  
  for (let i = hours; i >= 0; i--) {
    const timestamp = new Date(now.getTime() - i * 3600000);
    data.push({
      time: timestamp.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      heartRate: 70 + Math.random() * 20,
      respiration: 14 + Math.random() * 6,
      spo2: 95 + Math.random() * 5,
      timestamp: timestamp
    });
  }
  return data;
};

const timePeriods: TimePeriod[] = [
  { label: '24H', value: '24h' },
  { label: '7D', value: '7d' },
  { label: '30D', value: '30d' },
  { label: '90D', value: '90d' }
];

const selectedPeriod = ref('24h');
const dummyDataMap = {
  '24h': generateDummyData(24),
  '7d': generateDummyData(168),
  '30d': generateDummyData(720),
  '90d': generateDummyData(2160)
};

const displayData = computed(() => {
  return dummyDataMap[selectedPeriod.value];
});

// Current values for the vital signs display
const currentHeartRate = ref(0);
const currentSpO2 = ref(0);
const currentRespiration = ref(0);

// Initialize the current values
watchEffect(() => {
  const latest = displayData.value[displayData.value.length - 1];
  currentHeartRate.value = Math.round(latest.heartRate);
  currentSpO2.value = Math.round(latest.spo2);
  currentRespiration.value = Math.round(latest.respiration);
});

const handlePeriodChange = (period: string) => {
  selectedPeriod.value = period;
};

const handleChartHover = (e: any) => {
  if (e && e.activePayload) {
    // Update current values based on hover position
    const data = e.activePayload[0].payload;
    currentHeartRate.value = Math.round(data.heartRate);
    currentSpO2.value = Math.round(data.spo2);
    currentRespiration.value = Math.round(data.respiration);
  }
};

const handleChartLeave = () => {
  // Reset to latest values when leaving chart
  const latest = displayData.value[displayData.value.length - 1];
  currentHeartRate.value = Math.round(latest.heartRate);
  currentSpO2.value = Math.round(latest.spo2);
  currentRespiration.value = Math.round(latest.respiration);
};
</script>

<style scoped>
.chart-container {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.title-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.vital-signs {
  display: flex;
  gap: 20px;
}

.vital-sign {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.9rem;
  padding: 4px 8px;
  border-radius: 4px;
  background: #f1f5f9;
}

.heart-rate { color: #3b82f6; }
.spo2 { color: #10b981; }
.respiration { color: #ef4444; }

h3 {
  margin: 0;
  color: var(--text-color);
  font-size: 1.2rem;
}

.time-controls {
  display: flex;
  gap: 8px;
}

.time-button {
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: transparent;
  color: var(--text-color);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.time-button:hover {
  background: #f1f5f9;
}

.time-button.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.chart {
  height: 300px;
  width: 100%;
}

:deep(.custom-tooltip) {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>
  