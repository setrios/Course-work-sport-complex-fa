<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Training Sessions</h2>
      <button
        @click="showCreateModal = true"
        class="px-4 py-2 bg-accent hover:bg-accent-dark text-white rounded-md transition-colors"
      >
        Create Session
      </button>
    </div>

    <!-- Create Session Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showCreateModal = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Create Session</h3>
        <form @submit.prevent="handleCreateSession" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Service
            </label>
            <select
              v-model="sessionForm.service_id"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            >
              <option value="">Select a service</option>
              <option v-for="service in services" :key="service.id" :value="service.id">
                {{ service.name }}
              </option>
            </select>
          </div>
          <!-- Show Client dropdown for trainers, Trainer dropdown for clients -->
          <div v-if="currentUserRole === 'trainer'">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Client
            </label>
            <select
              v-model="sessionForm.client_id"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            >
              <option value="">Select a client</option>
              <option v-for="client in clients" :key="client.id" :value="client.id">
                {{ client.full_name }}
              </option>
            </select>
          </div>
          <div v-else>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Trainer (optional)
            </label>
            <select
              v-model="sessionForm.trainer_id"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            >
              <option :value="null">No trainer (unassigned)</option>
              <option v-for="trainer in trainers" :key="trainer.id" :value="trainer.id">
                {{ trainer.full_name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Scheduled At
            </label>
            <input
              v-model="sessionForm.scheduled_at"
              type="datetime-local"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Duration (minutes)
            </label>
            <input
              v-model.number="sessionForm.duration_minutes"
              type="number"
              min="15"
              step="15"
              placeholder="60"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Notes
            </label>
            <textarea
              v-model="sessionForm.notes"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            ></textarea>
          </div>
          <div v-if="error" class="text-red-600 dark:text-red-400 text-sm">{{ error }}</div>
          <div class="flex gap-3">
            <button
              type="submit"
              :disabled="creating"
              class="flex-1 px-4 py-2 bg-accent hover:bg-accent-dark text-white rounded-md transition-colors disabled:opacity-50"
            >
              {{ creating ? 'Creating...' : 'Create' }}
            </button>
            <button
              type="button"
              @click="showCreateModal = false"
              class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>

    <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
      <!-- Admin Tabs -->
      <div v-if="currentUserRole === 'admin'" class="flex border-b border-gray-200 dark:border-gray-700">
        <button
          v-for="tab in ['scheduled', 'in_progress', 'completed', 'cancelled']"
          :key="tab"
          @click="activeTab = tab"
          class="flex-1 py-3 px-4 text-sm font-medium text-center focus:outline-none transition-colors capitalize"
          :class="activeTab === tab 
            ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400' 
            : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'"
        >
          {{ tab.replace('_', ' ') }}
        </button>
      </div>

      <div v-if="loading" class="text-center py-8 text-gray-600 dark:text-gray-400">Loading...</div>
      <div v-else-if="filteredSessions.length === 0" class="text-center py-8 text-gray-600 dark:text-gray-400">
        No sessions found
      </div>
      <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
        <div
          v-for="session in filteredSessions"
          :key="session.id"
          class="p-4 hover:bg-gray-50 dark:hover:bg-gray-700"
        >
          <div class="flex justify-between items-start">
            <div>
              <p class="font-medium text-gray-900 dark:text-white">{{ session.service_name || 'N/A' }}</p>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                Trainer: {{ session.trainer_name || 'Unassigned' }}
              </p>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                Client: {{ session.client_name }}
              </p>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                {{ formatDate(session.scheduled_at) }}
              </p>
              <p class="text-sm text-gray-500 dark:text-gray-500">
                Duration: {{ session.duration_minutes || 60 }} minutes
              </p>
              <p v-if="session.notes" class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Notes: {{ session.notes }}
              </p>
            </div>
            <div class="flex items-center gap-2">
              <span :class="getStatusBadgeClass(session.status)">
                {{ session.status || 'scheduled' }}
              </span>
              <button
                @click="handleDeleteSession(session.id)"
                :disabled="session.status === 'cancelled'"
                class="px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ session.status === 'cancelled' ? 'Cancelled' : 'Cancel' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { authService } from '../services/auth'
import api from '../services/api'

const sessions = ref([])
const activeTab = ref('scheduled')
const adminSessions = ref({
  scheduled: [],
  in_progress: [],
  completed: [],
  cancelled: []
})
const services = ref([])
const trainers = ref([])
const clients = ref([])
const loading = ref(true)
const creating = ref(false)
const showCreateModal = ref(false)
const error = ref('')
const currentUserRole = ref('')

const sessionForm = ref({
  client_id: null,
  service_id: '',
  trainer_id: null,
  scheduled_at: '',
  notes: '',
  duration_minutes: 60,
})

const filteredSessions = computed(() => {
  if (currentUserRole.value === 'admin') {
    return adminSessions.value[activeTab.value] || []
  }
  return sessions.value
})

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

const getStatusBadgeClass = (status) => {
  const baseClasses = 'px-2 py-1 text-xs font-semibold rounded-full'
  switch (status) {
    case 'scheduled':
      return `${baseClasses} bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200`
    case 'in_progress':
      return `${baseClasses} bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 animate-pulse`
    case 'completed':
      return `${baseClasses} bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300`
    case 'cancelled':
      return `${baseClasses} bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200`
    default:
      return `${baseClasses} bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300`
  }
}

onMounted(async () => {
  try {
    const user = await authService.getCurrentUser()
    currentUserRole.value = user.role
    
    // If user is a client, set client_id and load trainers
    // If user is a trainer, set trainer_id and load clients
    if (user.role === 'client') {
      sessionForm.value.client_id = user.id
      const [servicesRes, trainersRes, dashboardRes] = await Promise.all([
        api.get('/services/'),
        api.get('/trainers/list'),
        api.get(`/users/${user.id}/dashboard`),
      ])
      services.value = servicesRes.data
      trainers.value = trainersRes.data
      sessions.value = [
        ...(dashboardRes.data.scheduled_sessions || []),
        ...(dashboardRes.data.in_progress_sessions || []),
        ...(dashboardRes.data.completed_sessions || []),
        ...(dashboardRes.data.cancelled_sessions || []),
      ]
    } else if (user.role === 'trainer') {
      sessionForm.value.trainer_id = user.id
      const [servicesRes, clientsRes, dashboardRes] = await Promise.all([
        api.get(`/trainers/${user.id}/specialized-services`),
        api.get('/clients/list'),
        api.get(`/users/${user.id}/dashboard`),
      ])
      services.value = servicesRes.data
      clients.value = clientsRes.data
      sessions.value = [
        ...(dashboardRes.data.scheduled_sessions || []),
        ...(dashboardRes.data.in_progress_sessions || []),
        ...(dashboardRes.data.completed_sessions || []),
        ...(dashboardRes.data.cancelled_sessions || []),
      ]
    } else if (user.role === 'admin') {
      const [servicesRes, trainersRes, clientsRes, adminSesRes] = await Promise.all([
        api.get('/services/'),
        api.get('/trainers/list'),
        api.get('/clients/list'),
        api.get('/admin/sessions/')
      ])
      services.value = servicesRes.data
      trainers.value = trainersRes.data
      clients.value = clientsRes.data
      
      adminSessions.value = {
        scheduled: adminSesRes.data.scheduled_sessions || [],
        in_progress: adminSesRes.data.in_progress_sessions || [],
        completed: adminSesRes.data.completed_sessions || [],
        cancelled: adminSesRes.data.cancelled_sessions || []
      }
    }
  } catch (error) {
    console.error('Failed to load sessions:', error)
  } finally {
    loading.value = false
  }
})

const handleCreateSession = async () => {
  creating.value = true
  error.value = ''
  
  try {
    const payload = {
      client_id: sessionForm.value.client_id,
      service_id: parseInt(sessionForm.value.service_id),
      scheduled_at: sessionForm.value.scheduled_at ? new Date(sessionForm.value.scheduled_at).toISOString() : null,
      notes: sessionForm.value.notes || null,
      duration_minutes: sessionForm.value.duration_minutes || 60,
    }
    
    if (sessionForm.value.trainer_id) {
      payload.trainer_id = parseInt(sessionForm.value.trainer_id)
      await api.post('/sessions/', payload)
    } else {
      await api.post('/sessions/unassigned/', payload)
    }
    
    showCreateModal.value = false
    
    // Reset form but keep user-specific IDs
    const user = await authService.getCurrentUser()
    sessionForm.value = {
      client_id: user.role === 'client' ? user.id : null,
      trainer_id: user.role === 'trainer' ? user.id : null,
      service_id: '',
      scheduled_at: '',
      notes: '',
      duration_minutes: 60,
    }
    
    // Reload sessions
    if (user.role === 'admin') {
      const adminSesRes = await api.get('/admin/sessions/')
      adminSessions.value = {
        scheduled: adminSesRes.data.scheduled_sessions || [],
        in_progress: adminSesRes.data.in_progress_sessions || [],
        completed: adminSesRes.data.completed_sessions || [],
        cancelled: adminSesRes.data.cancelled_sessions || []
      }
    } else {
      const dashboardRes = await api.get(`/users/${user.id}/dashboard`)
      sessions.value = [
        ...(dashboardRes.data.scheduled_sessions || []),
        ...(dashboardRes.data.in_progress_sessions || []),
        ...(dashboardRes.data.completed_sessions || []),
        ...(dashboardRes.data.cancelled_sessions || []),
      ]
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create session'
  } finally {
    creating.value = false
  }
}

const handleDeleteSession = async (sessionId) => {
  if (!confirm('Are you sure you want to delete this session?')) return
  
  try {
    await api.delete(`/sessions/${sessionId}`)
    const user = await authService.getCurrentUser()
    if (user.role === 'admin') {
      const adminSesRes = await api.get('/admin/sessions/')
      adminSessions.value = {
        scheduled: adminSesRes.data.scheduled_sessions || [],
        in_progress: adminSesRes.data.in_progress_sessions || [],
        completed: adminSesRes.data.completed_sessions || [],
        cancelled: adminSesRes.data.cancelled_sessions || []
      }
    } else {
      const dashboardRes = await api.get(`/users/${user.id}/dashboard`)
      sessions.value = [
        ...(dashboardRes.data.scheduled_sessions || []),
        ...(dashboardRes.data.in_progress_sessions || []),
        ...(dashboardRes.data.completed_sessions || []),
        ...(dashboardRes.data.cancelled_sessions || []),
      ]
    }
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to delete session')
  }
}
</script>

