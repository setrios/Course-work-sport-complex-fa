<template>
  <div class="space-y-6">
    <div v-if="loading" class="text-center py-8 text-gray-600 dark:text-gray-400">Loading...</div>
    <div v-else-if="trainer" class="space-y-6">
      <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">Trainer Details</h2>
        <div class="space-y-3">
          <div>
            <label class="text-sm font-medium text-gray-600 dark:text-gray-400">ID</label>
            <p class="text-gray-900 dark:text-white">{{ trainer.id }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-600 dark:text-gray-400">Full Name</label>
            <p class="text-gray-900 dark:text-white">{{ trainer.full_name }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-600 dark:text-gray-400">Email</label>
            <p class="text-gray-900 dark:text-white">{{ trainer.email }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-600 dark:text-gray-400">Specialization</label>
            <p class="text-gray-900 dark:text-white">{{ trainer.specialization || 'N/A' }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Update Trainer</h3>
        </div>
        <form @submit.prevent="handleUpdate" class="space-y-4">
          <div>
            <label for="full_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Full Name
            </label>
            <input
              id="full_name"
              v-model="updateForm.full_name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            />
          </div>
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Email
            </label>
            <input
              id="email"
              v-model="updateForm.email"
              type="email"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            />
          </div>
          <div>
            <label for="specialization" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Specialization
            </label>
            <input
              id="specialization"
              v-model="updateForm.specialization"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            />
          </div>
          <div v-if="error" class="text-red-600 dark:text-red-400 text-sm">{{ error }}</div>
          <div v-if="success" class="text-green-600 dark:text-green-400 text-sm">{{ success }}</div>
          <div class="flex gap-3">
            <button
              type="submit"
              :disabled="updating"
              class="px-4 py-2 bg-accent hover:bg-accent-dark text-white rounded-md transition-colors disabled:opacity-50"
            >
              {{ updating ? 'Updating...' : 'Update' }}
            </button>
            <button
              type="button"
              @click="handleDelete"
              :disabled="deleting"
              class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md transition-colors disabled:opacity-50"
            >
              {{ deleting ? 'Deleting...' : 'Delete' }}
            </button>
          </div>
        </form>
      </div>

      <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Sessions</h3>
        <div v-if="sessionsLoading" class="text-center py-4 text-gray-600 dark:text-gray-400">Loading...</div>
        <div v-else-if="sessions.length === 0" class="text-center py-4 text-gray-600 dark:text-gray-400">
          No sessions found
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="session in sessions"
            :key="session.id"
            class="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
          >
            <p class="font-medium text-gray-900 dark:text-white">{{ session.service_name || 'N/A' }}</p>
            <p class="text-sm text-gray-600 dark:text-gray-400">Client: {{ session.client_name }}</p>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ formatDate(session.scheduled_at) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'

const route = useRoute()
const router = useRouter()
const trainer = ref(null)
const sessions = ref([])
const loading = ref(true)
const sessionsLoading = ref(true)
const updating = ref(false)
const deleting = ref(false)
const error = ref('')
const success = ref('')

const updateForm = ref({
  full_name: '',
  email: '',
  specialization: '',
})

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

onMounted(async () => {
  try {
    const [trainerRes, sessionsRes] = await Promise.all([
      api.get(`/trainers/${route.params.id}`),
      api.get(`/trainers/${route.params.id}/sessions`),
    ])
    trainer.value = trainerRes.data
    sessions.value = sessionsRes.data
    updateForm.value = {
      full_name: trainerRes.data.full_name || '',
      email: trainerRes.data.email || '',
      specialization: trainerRes.data.specialization || '',
    }
  } catch (error) {
    console.error('Failed to load trainer:', error)
  } finally {
    loading.value = false
    sessionsLoading.value = false
  }
})

const handleUpdate = async () => {
  updating.value = true
  error.value = ''
  success.value = ''
  
  try {
    const payload = {}
    if (updateForm.value.full_name) payload.full_name = updateForm.value.full_name
    if (updateForm.value.email) payload.email = updateForm.value.email
    if (updateForm.value.specialization !== undefined) payload.specialization = updateForm.value.specialization || null
    
    await api.put(`/trainers/${route.params.id}`, payload)
    success.value = 'Trainer updated successfully'
    const response = await api.get(`/trainers/${route.params.id}`)
    trainer.value = response.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Update failed'
  } finally {
    updating.value = false
  }
}

const handleDelete = async () => {
  if (!confirm('Are you sure you want to delete this trainer?')) return
  
  deleting.value = true
  try {
    await api.delete(`/trainers/${route.params.id}`)
    router.push('/trainers')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Delete failed'
    deleting.value = false
  }
}
</script>

