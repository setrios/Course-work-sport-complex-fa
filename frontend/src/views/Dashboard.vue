<template>
  <div class="space-y-6">
    <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Welcome, {{ user?.full_name || 'User' }}</h2>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <p class="text-sm text-gray-600 dark:text-gray-400">Scheduled</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ dashboard?.scheduled_sessions?.length || 0 }}</p>
        </div>
        <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
          <p class="text-sm text-green-700 dark:text-green-400">In Progress</p>
          <p class="text-2xl font-bold text-green-800 dark:text-green-300">{{ dashboard?.in_progress_sessions?.length || 0 }}</p>
        </div>
        <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <p class="text-sm text-gray-600 dark:text-gray-400">Completed</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ dashboard?.completed_sessions?.length || 0 }}</p>
        </div>
        <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <p class="text-sm text-gray-600 dark:text-gray-400">Active Subscriptions</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ dashboard?.subscriptions?.length || 0 }}</p>
        </div>
      </div>
    </div>

    <div class="space-y-6">
      <!-- Scheduled Sessions -->
      <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Scheduled Sessions</h3>
        <div v-if="loading" class="text-center py-4 text-gray-600 dark:text-gray-400">Loading...</div>
        <div v-else-if="dashboard?.scheduled_sessions?.length === 0" class="text-center py-4 text-gray-600 dark:text-gray-400">
          No scheduled sessions
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="session in dashboard?.scheduled_sessions"
            :key="session.id"
            class="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <p class="font-medium text-gray-900 dark:text-white">{{ session.service_name }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-400" v-if="session.trainer_name">
                  Trainer: {{ session.trainer_name || 'Unassigned' }}
                </p>
                <p class="text-sm text-gray-600 dark:text-gray-400" v-if="session.client_name">
                  Client: {{ session.client_name }}
                </p>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  {{ formatDate(session.scheduled_at) }}
                </p>
                <p class="text-sm text-gray-500 dark:text-gray-500">
                  Duration: {{ session.duration_minutes }} minutes
                </p>
              </div>
              <span class="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                Scheduled
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- In Progress Sessions -->
      <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6" v-if="dashboard?.in_progress_sessions?.length > 0">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">In Progress</h3>
        <div class="space-y-3">
          <div
            v-for="session in dashboard?.in_progress_sessions"
            :key="session.id"
            class="border border-green-300 dark:border-green-700 rounded-lg p-4 bg-green-50 dark:bg-green-900/10"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <p class="font-medium text-gray-900 dark:text-white">{{ session.service_name }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-400" v-if="session.trainer_name">
                  Trainer: {{ session.trainer_name || 'Unassigned' }}
                </p>
                <p class="text-sm text-gray-600 dark:text-gray-400" v-if="session.client_name">
                  Client: {{ session.client_name }}
                </p>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  {{ formatDate(session.scheduled_at) }}
                </p>
                <p class="text-sm text-gray-500 dark:text-gray-500">
                  Duration: {{ session.duration_minutes }} minutes
                </p>
              </div>
              <span class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 animate-pulse">
                In Progress
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Completed Sessions -->
      <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Completed Sessions</h3>
        <div v-if="loading" class="text-center py-4 text-gray-600 dark:text-gray-400">Loading...</div>
        <div v-else-if="dashboard?.completed_sessions?.length === 0" class="text-center py-4 text-gray-600 dark:text-gray-400">
          No completed sessions
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="session in dashboard?.completed_sessions?.slice(0, 5)"
            :key="session.id"
            class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 opacity-75"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <p class="font-medium text-gray-900 dark:text-white">{{ session.service_name }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-400" v-if="session.trainer_name">
                  Trainer: {{ session.trainer_name }}
                </p>
                <p class="text-sm text-gray-600 dark:text-gray-400" v-if="session.client_name">
                  Client: {{ session.client_name }}
                </p>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  {{ formatDate(session.scheduled_at) }}
                </p>
                <p class="text-sm text-gray-500 dark:text-gray-500">
                  Duration: {{ session.duration_minutes }} minutes
                </p>
              </div>
              <span class="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
                Completed
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Specializations (Trainers Only) / Subscriptions (Others) -->
      <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
        <!-- Show Specializations for Trainers -->
        <template v-if="user?.role === 'trainer'">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Specializations</h3>
          <div v-if="loading" class="text-center py-4 text-gray-600 dark:text-gray-400">Loading...</div>
          <div v-else>
            <!-- Add new specialization -->
            <div class="mb-4 flex gap-2">
              <select
                v-model="selectedServiceId"
                class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select a service</option>
                <option v-for="service in availableServices" :key="service.id" :value="service.id">
                  {{ service.name }}
                </option>
              </select>
              <button
                @click="addSpecialization"
                :disabled="!selectedServiceId"
                class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                Add
              </button>
            </div>

            <!-- Display specializations -->
            <div v-if="dashboard?.specializations?.length === 0" class="text-center py-4 text-gray-600 dark:text-gray-400">
              No specializations added yet
            </div>
            <div v-else class="space-y-2">
              <div
                v-for="spec in dashboard?.specializations"
                :key="spec.id"
                class="flex items-center justify-between border border-gray-200 dark:border-gray-700 rounded-lg p-3"
              >
                <span class="font-medium text-gray-900 dark:text-white">{{ spec.service_name }}</span>
                <button
                  @click="deleteSpecialization(spec.id)"
                  class="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 font-bold text-xl"
                  title="Delete specialization"
                >
                  ×
                </button>
              </div>
            </div>
          </div>
        </template>

        <!-- Show Active Subscriptions for Non-Trainers -->
        <template v-else>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Active Subscriptions</h3>
          <div v-if="loading" class="text-center py-4 text-gray-600 dark:text-gray-400">Loading...</div>
          <div v-else-if="dashboard?.subscriptions?.length === 0" class="text-center py-4 text-gray-600 dark:text-gray-400">
            No active subscriptions
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="sub in dashboard?.subscriptions"
              :key="sub.id"
              class="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
            >
              <p class="font-medium text-gray-900 dark:text-white">{{ sub.service_name }}</p>
              <p class="text-sm text-gray-600 dark:text-gray-400">Plan: {{ sub.plan_type }}</p>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                Since: {{ formatDate(sub.created_at) }}
              </p>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { authService } from '../services/auth'
import api from '../services/api'

const user = ref(null)
const dashboard = ref(null)
const loading = ref(true)
const selectedServiceId = ref('')
const services = ref([])

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

// Compute available services (ones not already specialized in)
const availableServices = computed(() => {
  if (!services.value || !dashboard.value?.specializations) return services.value || []
  
  const specializedServiceIds = dashboard.value.specializations.map(spec => spec.service_id)
  return services.value.filter(service => !specializedServiceIds.includes(service.id))
})

const loadDashboard = async () => {
  try {
    const response = await api.get(`/users/${user.value.id}/dashboard`)
    dashboard.value = response.data
  } catch (error) {
    console.error('Failed to load dashboard:', error)
  }
}

const addSpecialization = async () => {
  if (!selectedServiceId.value) return
  
  try {
    await api.post(`/trainers/${user.value.id}/specializations`, {
      service_id: parseInt(selectedServiceId.value)
    })
    selectedServiceId.value = ''
    await loadDashboard()
  } catch (error) {
    console.error('Failed to add specialization:', error)
    if (error.response?.status === 409) {
      alert('You already have this specialization')
    } else if (error.response?.status === 404) {
      alert('Service not found')
    } else {
      alert('Failed to add specialization. Please try again.')
    }
  }
}

const deleteSpecialization = async (specializationId) => {
  if (!confirm('Are you sure you want to delete this specialization?')) return
  
  try {
    await api.delete(`/trainers/${user.value.id}/specializations/${specializationId}`)
    await loadDashboard()
  } catch (error) {
    console.error('Failed to delete specialization:', error)
    alert('Failed to delete specialization. Please try again.')
  }
}

onMounted(async () => {
  try {
    const currentUser = await authService.getCurrentUser()
    user.value = currentUser
    
    // Load services if user is a trainer
    if (currentUser.role === 'trainer') {
      const servicesRes = await api.get('/services/')
      services.value = servicesRes.data
    }
    
    await loadDashboard()
  } catch (error) {
    console.error('Failed to load dashboard:', error)
  } finally {
    loading.value = false
  }
})
</script>

