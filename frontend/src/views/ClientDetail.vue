<template>
  <div class="space-y-6">
    <div v-if="loading" class="text-center py-8 text-gray-600 dark:text-gray-400">Loading...</div>
    <div v-else-if="client" class="space-y-6">
      <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">Client Details</h2>
        <div class="space-y-3">
          <div>
            <label class="text-sm font-medium text-gray-600 dark:text-gray-400">ID</label>
            <p class="text-gray-900 dark:text-white">{{ client.id }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-600 dark:text-gray-400">Full Name</label>
            <p class="text-gray-900 dark:text-white">{{ client.full_name }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-600 dark:text-gray-400">Email</label>
            <p class="text-gray-900 dark:text-white">{{ client.email }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Update Client</h3>
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
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'

const route = useRoute()
const router = useRouter()
const client = ref(null)
const loading = ref(true)
const updating = ref(false)
const deleting = ref(false)
const error = ref('')
const success = ref('')

const updateForm = ref({
  full_name: '',
  email: '',
})

onMounted(async () => {
  try {
    const response = await api.get(`/clients/${route.params.id}`)
    client.value = response.data
    updateForm.value = {
      full_name: response.data.full_name || '',
      email: response.data.email || '',
    }
  } catch (error) {
    console.error('Failed to load client:', error)
  } finally {
    loading.value = false
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
    
    await api.put(`/clients/${route.params.id}`, payload)
    success.value = 'Client updated successfully'
    const response = await api.get(`/clients/${route.params.id}`)
    client.value = response.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Update failed'
  } finally {
    updating.value = false
  }
}

const handleDelete = async () => {
  if (!confirm('Are you sure you want to delete this client?')) return
  
  deleting.value = true
  try {
    await api.delete(`/clients/${route.params.id}`)
    router.push('/clients')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Delete failed'
    deleting.value = false
  }
}
</script>

