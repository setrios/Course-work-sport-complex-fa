<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Medical Documents</h2>
    </div>

    <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Submit Medical Document</h3>
      <form @submit.prevent="handleSubmitMedical" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Client Email
          </label>
          <input
            v-model="medicalForm.client_email"
            type="email"
            required
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            :readonly="!isAdmin"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Doctor Name
          </label>
          <input
            v-model="medicalForm.doctor_name"
            type="text"
            required
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Result
          </label>
          <select
            v-model="medicalForm.result"
            required
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
          >
            <option value="">Select result</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="pending">Pending</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Details (JSON)
          </label>
          <textarea
            v-model="medicalForm.detailsJson"
            rows="5"
            required
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent font-mono text-sm"
            placeholder='{"blood_pressure": "120/80", "heart_rate": 72, "notes": "Fit for exercise"}'
          ></textarea>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Enter valid JSON format</p>
        </div>
        <div v-if="error" class="text-red-600 dark:text-red-400 text-sm">{{ error }}</div>
        <div v-if="success" class="text-green-600 dark:text-green-400 text-sm">
          {{ success }}
          <span v-if="docId" class="block mt-1">Document ID: <code class="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">{{ docId }}</code></span>
        </div>
        <button
          type="submit"
          :disabled="submitting"
          class="w-full px-4 py-2 bg-accent hover:bg-accent-dark text-white rounded-md transition-colors disabled:opacity-50"
        >
          {{ submitting ? 'Submitting...' : 'Submit' }}
        </button>
      </form>
    </div>

    <div v-if="latestDoc" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Latest Medical Document</h3>
      <div class="space-y-2">
        <div>
          <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Doctor:</span>
          <span class="ml-2 text-gray-900 dark:text-white">{{ latestDoc.doctor }}</span>
        </div>
        <div>
          <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Status:</span>
          <span class="ml-2 text-gray-900 dark:text-white">{{ latestDoc.status }}</span>
        </div>
        <div>
          <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Date:</span>
          <span class="ml-2 text-gray-900 dark:text-white">{{ formatDate(latestDoc.timestamp) }}</span>
        </div>
        <div>
          <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Details:</span>
          <pre class="mt-2 p-3 bg-gray-50 dark:bg-gray-700 rounded text-sm text-gray-900 dark:text-white overflow-auto">{{ JSON.stringify(latestDoc.clinical_data, null, 2) }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { authService } from '../services/auth'
import api from '../services/api'

const currentUser = ref(null)
const latestDoc = ref(null)
const submitting = ref(false)
const error = ref('')
const success = ref('')
const docId = ref('')

const medicalForm = ref({
  client_email: '',
  doctor_name: '',
  result: '',
  detailsJson: '{}',
})

const isAdmin = computed(() => {
  const user = authService.getUser()
  return user?.role === 'admin'
})

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

onMounted(async () => {
  try {
    const user = await authService.getCurrentUser()
    currentUser.value = user
    medicalForm.value.client_email = user.email
    
    const dashboardRes = await api.get(`/users/${user.id}/dashboard`)
    if (dashboardRes.data.latest_medical_doc) {
      latestDoc.value = dashboardRes.data.latest_medical_doc
    }
  } catch (error) {
    console.error('Failed to load user data:', error)
  }
})

const handleSubmitMedical = async () => {
  submitting.value = true
  error.value = ''
  success.value = ''
  docId.value = ''
  
  try {
    let details
    try {
      details = JSON.parse(medicalForm.value.detailsJson)
    } catch (e) {
      error.value = 'Invalid JSON format in details field'
      submitting.value = false
      return
    }
    
    const payload = {
      client_email: medicalForm.value.client_email,
      doctor_name: medicalForm.value.doctor_name,
      result: medicalForm.value.result,
      details: details,
    }
    
    const response = await api.post('/medical-checkup/', payload)
    success.value = 'Medical document submitted successfully!'
    docId.value = response.data.couchdb_id
    
    // Reload latest document
    const user = await authService.getCurrentUser()
    const dashboardRes = await api.get(`/users/${user.id}/dashboard`)
    if (dashboardRes.data.latest_medical_doc) {
      latestDoc.value = dashboardRes.data.latest_medical_doc
    }
    
    // Reset form
    medicalForm.value = {
      client_email: user.email,
      doctor_name: '',
      result: '',
      detailsJson: '{}',
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to submit medical document'
  } finally {
    submitting.value = false
  }
}
</script>

