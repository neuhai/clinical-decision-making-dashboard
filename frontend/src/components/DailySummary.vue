<template>
  <div :class="['daily-summary', { 'is-zoomed': isZoomed }]">
    <div class="header">
      <div class="header-title">
        <h3>Daily Summary</h3>
        <span class="info-icon">
          <i class="fa-solid fa-info-circle"></i>
          <span class="tooltip-text">This summary is generated by an LLM using the patient's wearable sensor data and conversation log.</span>
        </span>
      </div>
      <div class="date-picker">
        <input type="date" v-model="selectedDate" @change="updateContent" />
      </div>
    </div>
  
    <!-- Summary Section with Loading State -->
    <div class="content-wrapper">
      <div class="section summary-section">
        <div class="section-header">
          <h4>LLM-Generated Summary</h4>
          <div v-if="isLoading" class="loading-spinner"></div>
        </div>
        
        <div v-if="notificationVisible" class="notification" :class="notificationType">
          {{ notificationMessage }}
          <button class="close-notification" @click="notificationVisible = false">×</button>
        </div>
        
        <!-- Full-width text area using all available space -->
        <div class="summary-text-container">
          <textarea v-model="llmSummary" readonly class="summary-textarea" :class="{ 'error-text': hasError }"></textarea>
        </div>
        
        <div v-if="hasError" class="retry-section">
          <button @click="updateContent" class="retry-button">
            <i class="fa-solid fa-rotate"></i> Retry
          </button>
          <span class="retry-hint">API request failed. This may be due to the backend service being unavailable or no data existing for this date.</span>
        </div>
      </div>
    </div>
    <!--
    <div class="content">
      <div class="column">
        <div class="section-header">
          <h4>Self-Reported Symptoms</h4>
        </div>
        <div class="section">
          <div class="section-content">
            <div v-if="symptoms.length">
              <div v-for="(symptom, index) in symptoms" :key="index" class="symptom-item">
                <h5>{{ symptom.name }}</h5>
                <p>{{ symptom.description }}</p>
              </div>
            </div>
            <div v-else>
              <p>No symptoms reported for this date.</p>
            </div>
          </div>
        </div>
      </div>
  
      <div class="column">
        <div class="section-header">
          <h4>Wearable Sensor Data</h4>
        </div>
        <div class="section">
          <div class="section-content">
            <div class="sensor-item">
              <h5>Heart Rate</h5>
              <p>{{ sensorData.heartRate }} BPM (avg)</p>
            </div>
            <div class="sensor-item">
              <h5>SpO2</h5>
              <p>{{ sensorData.spO2 }}% (avg)</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    -->

  </div>

</template>
  
<script setup>
import { ref, onMounted, watch } from 'vue';

// State variables
const today = new Date().toISOString().split('T')[0];
const selectedDate = ref(today);
const llmSummary = ref('Your daily health summary will appear here...');
const isZoomed = ref(false);
const isLoading = ref(false);
const hasError = ref(false);
const retryCount = ref(0);
const maxRetries = 2;

// Simple notification system
const notificationVisible = ref(false);
const notificationMessage = ref('');
const notificationType = ref('info');

function showNotification(message, type = 'info') {
  notificationMessage.value = message;
  notificationType.value = type;
  notificationVisible.value = true;
  
  // Auto-hide after 5 seconds
  setTimeout(() => {
    notificationVisible.value = false;
  }, 5000);
}

// ✅ Automatically load data on component mount
onMounted(() => {
  updateContent();
});

// Main function to fetch and update content
async function updateContent() {
  isLoading.value = true;
  hasError.value = false;
  notificationVisible.value = false;
  llmSummary.value = 'Generating your health summary...';
  
  try {
    const patientId = '1'; // Replace with dynamic patient ID if needed
    const formattedDate = selectedDate.value;
    
    console.log(`Fetching summary for date: ${formattedDate}, attempt ${retryCount.value + 1}`);
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002';
    // Make request to backend API
    const response = await fetch(`${apiBaseUrl}/api/daily-summary/${patientId}?date=${formattedDate}`, {
      // Add timeout to prevent long waiting
      signal: AbortSignal.timeout(10000)
    });
    
    // Handle HTTP errors
    if (!response.ok) {
      const status = response.status;
      console.error(`API returned status ${status}`);
      
      let errorMsg;
      if (status === 404) {
        errorMsg = `No health data available for ${new Date(formattedDate).toLocaleDateString()}. Please try another date.`;
      } else if (status >= 500) {
        errorMsg = "The server encountered an error processing your request. Please try again later.";
      } else {
        errorMsg = `Error retrieving summary. Status: ${status}`;
      }
      
      throw new Error(errorMsg);
    }
    
    // Process successful response
    const data = await response.json();
    
    if (data.summary) {
      llmSummary.value = data.summary;
      retryCount.value = 0; // Reset retry count on success
      hasError.value = false;
      showNotification("Summary successfully generated!", "success");
    } else {
      throw new Error("Received empty summary from API");
    }
    
  } catch (error) {
    console.error("Error fetching daily summary:", error);
    hasError.value = true;
    
    // Set error message in the summary area
    llmSummary.value = error.message || "Could not generate summary. The backend service may be unavailable.";
    
    // Show notification
    if (retryCount.value === 0) {
      showNotification(error.message, "error");
    }
    
    // Increment retry count
    retryCount.value++;
    
    // Auto-retry once if it's the first error
    if (retryCount.value <= maxRetries) {
      console.log(`Automatically retrying (${retryCount.value}/${maxRetries})...`);
      setTimeout(updateContent, 2000); // Retry after 2 seconds
    }
  } finally {
    isLoading.value = false;
  }
}

// Reset retry count when date changes
watch(selectedDate, () => {
  retryCount.value = 0;
});
</script>
  
<style scoped>
.daily-summary {
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9fafb;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  position: relative;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background-color: #3b82f6;
  color: white;
}

.header h3 {
  font-size: 1rem;
  font-weight: bold;
  color: white;
  margin: 0;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
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

.info-icon {
  position: relative;
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  color: white;
}

.info-icon:hover .tooltip-text {
  visibility: visible;
  opacity: 1;
}

.date-picker input {
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  font-size: 0.875rem;
}

/* New wrapper to take up all remaining space */
.content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px;
  overflow: hidden;
}

.section {
  margin: 0;
  padding: 0;
}

.summary-section {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-header h4 {
  font-size: 0.95rem;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Simple notification styling */
.notification {
  margin-bottom: 10px;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 0.875rem;
  position: relative;
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.notification.error {
  background-color: #fee2e2;
  color: #b91c1c;
  border-left: 4px solid #ef4444;
}

.notification.success {
  background-color: #d1fae5;
  color: #047857;
  border-left: 4px solid #10b981;
}

.notification.info {
  background-color: #dbeafe;
  color: #1e40af;
  border-left: 4px solid #3b82f6;
}

.close-notification {
  position: absolute;
  right: 8px;
  top: 8px;
  background: none;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  line-height: 1;
  padding: 0;
  color: inherit;
  opacity: 0.7;
}

.close-notification:hover {
  opacity: 1;
}

.summary-text-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.summary-textarea {
  flex: 1;
  min-height: 150px;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  font-size: 0.95rem;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: white;
  color: #333;
  resize: none;
  box-sizing: border-box;
  line-height: 1.5;
}

.error-text {
  color: #b91c1c;
  background-color: #fee2e2;
  border-color: #fca5a5;
}

.retry-section {
  display: flex;
  align-items: center;
  margin-top: 10px;
  gap: 10px;
}

.retry-button {
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 10px;
  font-size: 0.85rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.retry-button:hover {
  background-color: #2563eb;
}

.retry-hint {
  font-size: 0.75rem;
  color: #6b7280;
}
</style>
