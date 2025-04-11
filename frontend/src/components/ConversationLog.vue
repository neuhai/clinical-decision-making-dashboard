<template>
  <div class="conversational-log">
    <div class="header">
      <div class="header-title">
        <h3>Conversational Log</h3>
        <span class="info-icon">
          <i class="fa-solid fa-info-circle"></i>
          <span class="tooltip-text">This section displays the patient's conversation with the chatbot.</span>
        </span>
      </div>
      <div class="date-picker">
        <input type="date" :value="selectedDate" @change="onDateChange" />
      </div>
    </div>

    <div class="content">
      <!-- Daily Features Section -->
      <div class="daily-features">
        <div class="section-header">
          <h4>Symptom Summary</h4>
        </div>
        <div class="features-grid">
          <div
            class="feature"
            v-for="(feature, index) in features"
            :key="index"
            :class="{ 'feature-selected': selectedFeature === feature.label }"
            @click="onDotClick(feature.label)"
          >
            <font-awesome-icon
              :icon="feature.iconClass"
              :class="['clickable-icon', feature.iconColorClass]"
            />
            <span class="feature-label">{{ feature.label }}</span>
            <span class="symptom-status" :class="feature.statusClass">
              {{ feature.status }}
            </span>
          </div>
        </div>
      </div>

      <!-- Chat Log Section -->
      <div class="chat-log">
        <div class="chat-log-header">
          <h4>
            {{ selectedFeature ? selectedFeature : 'Select a symptom to view conversation' }}
          </h4>
        </div>
        <div class="messages" v-if="selectedFeature">
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="['message', message.type]"
          >
            <img :src="getIcon(message.icon)" alt="icon" class="icon" />
            <span
              class="message-text"
              :class="{
                'experienced-true': message.type === 'patient' && message.experienced === true,
                'experienced-false': message.type === 'patient' && message.experienced === false
              }"
            >
              {{ message.text }}
            </span>
          </div>
        </div>
        <div class="empty-state" v-else>
          <p>Please select a symptom from the left panel to view the conversation.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faInfoCircle, faExclamation, faCircle } from '@fortawesome/free-solid-svg-icons';
import robotIcon from '@/assets/robot.png';
import userIcon from '@/assets/user.png';

// Register icons
library.add(faInfoCircle, faExclamation, faCircle);

// Props accepting patient data from Sidebar.vue
const props = defineProps<{
  conversationLog: {
    date: string;
    conversations: {
      [key: string]: { type: string; text: string; icon: string; experienced?: boolean }[];
    };
  } | null;
}>();

// Format date function (convert from MM/DD/YYYY to YYYY-MM-DD format for input)
function formatDateForInput(dateString: string): string {
  if (!dateString) return new Date().toISOString().slice(0, 10);
  
  // If already in YYYY-MM-DD format
  if (/^\d{4}-\d{2}-\d{2}$/.test(dateString)) {
    return dateString;
  }
  
  // Convert from MM/DD/YYYY to YYYY-MM-DD
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
  
  // Default to current date if parsing fails
  return new Date().toISOString().slice(0, 10);
}

// State variables
const selectedDate = ref(formatDateForInput(props.conversationLog?.date || ''));
const selectedFeature = ref<string | null>(null);

// Enhanced feature data with status
const features = computed(() => {
  const result = [
    { label: 'Shortness of Breath', iconClass: 'circle', iconColorClass: 'green-icon', status: 'Not Reported', statusClass: 'status-good' },
    { label: 'Palpitation', iconClass: 'circle', iconColorClass: 'green-icon', status: 'Not Reported', statusClass: 'status-good' },
    { label: 'Chest Discomfort', iconClass: 'circle', iconColorClass: 'green-icon', status: 'Not Reported', statusClass: 'status-good' },
    { label: 'Swelling', iconClass: 'circle', iconColorClass: 'green-icon', status: 'Not Reported', statusClass: 'status-good' },
    { label: 'Fatigue', iconClass: 'circle', iconColorClass: 'green-icon', status: 'Not Reported', statusClass: 'status-good' },
    { label: 'Syncope', iconClass: 'circle', iconColorClass: 'green-icon', status: 'Not Reported', statusClass: 'status-good' }
  ];
  
  // Update status based on conversation data
  if (props.conversationLog?.conversations) {
    Object.keys(props.conversationLog.conversations).forEach(symptom => {
      const index = result.findIndex(item => item.label === symptom);
      if (index >= 0) {
        const messages = props.conversationLog?.conversations[symptom] || [];
        // Look for patient messages with 'experienced' property
        const experiencedMessage = messages.find(
          msg => msg.type === 'patient' && msg.experienced === true
        );
        
        if (experiencedMessage) {
          result[index].status = 'Reported';
          result[index].statusClass = 'status-warning';
          result[index].iconClass = 'exclamation';
          result[index].iconColorClass = 'yellow-icon';
        }
      }
    });
  }
  
  return result;
});

// Computed property to display messages based on the selected feature
const messages = computed(() => {
  if (!props.conversationLog || !selectedFeature.value) return [];
  return props.conversationLog.conversations[selectedFeature.value] || [];
});

// Method to handle feature selection
const onDotClick = (feature: string) => {
  selectedFeature.value = feature === selectedFeature.value ? null : feature;
};

// Method to handle date change
const onDateChange = (event: Event) => {
  const input = event.target as HTMLInputElement;
  selectedDate.value = input.value;
  // In a real implementation, this would load data for the selected date
  // For now, just reset the feature selection
  selectedFeature.value = null;
};

// Utility function to dynamically return the correct icon image
const getIcon = (iconName: string) => {
  return iconName === 'robotIcon' ? robotIcon : userIcon;
};

// Watch for changes in the conversationLog
watch(() => props.conversationLog, (newLog) => {
  if (newLog) {
    // Update date from conversationLog
    selectedDate.value = formatDateForInput(newLog.date);
    // Reset feature selection when data changes
    selectedFeature.value = null;
  }
}, { deep: true });
</script>

<style scoped>
.conversational-log {
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9fafb;
  padding: 16px;
  max-width: 100%;
  overflow: hidden;
  position: relative;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
  background-color: #3b82f6;
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
  margin: 0;
  color: white;
}

/* Match date picker style from AIRiskPrediction */
.date-picker input {
  padding: 5px;
  font-size: 0.875rem;
  border-radius: 4px;
  border: 1px solid #ddd;
  background-color: white;
}

.info-icon {
  position: relative;
  display: inline-flex;
  align-items: center;
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

.content {
  display: flex;
  gap: 20px;
  margin-top: 16px;
}

.section-header {
  margin-bottom: 12px;
}

.section-header h4 {
  font-size: 0.95rem;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.daily-features {
  width: 45%;
}

.features-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.feature {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid transparent;
  transition: all 0.2s ease;
  cursor: pointer;
}

.feature:hover {
  border-color: #cbd5e1;
}

.feature-selected {
  background-color: #f0f9ff;
  border-color: #93c5fd;
}

.clickable-icon {
  font-size: 1.2rem;
  transition: transform 0.2s;
}

.feature:hover .clickable-icon {
  transform: scale(1.1);
}

.green-icon {
  color: #10b981;
}

.yellow-icon {
  color: #f59e0b;
}

.feature-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  flex: 1;
}

.symptom-status {
  font-size: 0.75rem;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.status-good {
  background-color: #d1fae5;
  color: #10b981;
}

.status-warning {
  background-color: #fef3c7;
  color: #f59e0b;
}

.chat-log {
  width: 55%;
  display: flex;
  flex-direction: column;
}

.chat-log-header {
  margin-bottom: 12px;
}

.chat-log-header h4 {
  font-size: 0.95rem;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
  padding: 12px;
  background-color: #f3f4f6;
  border-radius: 8px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  background-color: #f3f4f6;
  border-radius: 8px;
  color: #6b7280;
  font-size: 0.875rem;
  text-align: center;
  padding: 20px;
}

.message {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.message.bot {
  flex-direction: row;
}

.message.patient {
  flex-direction: row-reverse;
}

.icon {
  width: 24px;
  height: 24px;
  margin-top: 4px;
}

.message-text {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 0.875rem;
  max-width: 70%;
  border: 3px solid transparent;
  transition: border-color 0.3s;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.bot .message-text {
  background-color: #e5e7eb;
  color: #374151;
  border-bottom-left-radius: 4px;
}

.patient .message-text {
  background-color: #dbeafe;
  color: #1e40af;
  border-bottom-right-radius: 4px;
}

.patient .message-text.experienced-true {
  border-color: #f59e0b;
}

.patient .message-text.experienced-false {
  border-color: #10b981;
}
</style>

  
  
  
  
  