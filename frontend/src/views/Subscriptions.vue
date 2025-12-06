<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Subscriptions</h2>
      <button
        @click="showCreateModal = true"
        class="px-4 py-2 bg-accent hover:bg-accent-dark text-white rounded-md transition-colors"
      >
        Create Subscription
      </button>
    </div>

    <!-- Create Subscription Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showCreateModal = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Create Subscription</h3>
        <form @submit.prevent="handleCreateSubscription" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Service
            </label>
            <select
              v-model="subscriptionForm.service_name"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            >
              <option value="">Select a service</option>
              <option v-for="service in services" :key="service.id" :value="service.name">
                {{ service.name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Plan Type
            </label>
            <input
              v-model="subscriptionForm.plan_type"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
              placeholder="e.g., Monthly, Annual"
            />
          </div>
          <div v-if="selectedService?.requires_medical">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Medical Document ID
            </label>
            <input
              v-model="subscriptionForm.medical_doc_id"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
              placeholder="CouchDB document ID"
            />
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
      <div v-if="loading" class="text-center py-8 text-gray-600 dark:text-gray-400">Loading...</div>
      <div v-else-if="subscriptions.length === 0" class="text-center py-8 text-gray-600 dark:text-gray-400">
        No subscriptions found
      </div>
      <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
        <div
          v-for="sub in subscriptions"
          :key="sub.id"
          class="p-4 hover:bg-gray-50 dark:hover:bg-gray-700"
        >
          <div class="flex justify-between items-start">
            <div>
              <p class="font-medium text-gray-900 dark:text-white">{{ sub.service_name }}</p>
              <p class="text-sm text-gray-600 dark:text-gray-400">Plan: {{ sub.plan_type }}</p>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                Created: {{ formatDate(sub.created_at) }}
              </p>
              <p v-if="sub.medical_doc_id" class="text-sm text-gray-600 dark:text-gray-400">
                Medical Doc ID: {{ sub.medical_doc_id }}
              </p>
            </div>
            <div class="flex gap-2">
              <button
                @click="editSubscription(sub)"
                class="px-3 py-1 text-sm bg-accent hover:bg-accent-dark text-white rounded-md transition-colors"
              >
                Edit
              </button>
              <button
                @click="handleDeleteSubscription(sub.id)"
                class="px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded-md transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Subscription Modal -->
    <div
      v-if="showEditModal && editingSubscription"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showEditModal = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Edit Subscription</h3>
        <form @submit.prevent="handleUpdateSubscription" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Plan Type
            </label>
            <input
              v-model="editForm.plan_type"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Medical Document ID
            </label>
            <input
              v-model="editForm.medical_doc_id"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            />
          </div>
          <div v-if="error" class="text-red-600 dark:text-red-400 text-sm">{{ error }}</div>
          <div class="flex gap-3">
            <button
              type="submit"
              :disabled="updating"
              class="flex-1 px-4 py-2 bg-accent hover:bg-accent-dark text-white rounded-md transition-colors disabled:opacity-50"
            >
              {{ updating ? 'Updating...' : 'Update' }}
            </button>
            <button
              type="button"
              @click="showEditModal = false"
              class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { authService } from '../services/auth'
import api from '../services/api'

const subscriptions = ref([])
const services = ref([])
const loading = ref(true)
const creating = ref(false)
const updating = ref(false)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const editingSubscription = ref(null)
const error = ref('')

const subscriptionForm = ref({
  client_id: null,
  service_name: '',
  plan_type: '',
  medical_doc_id: '',
})

const editForm = ref({
  plan_type: '',
  medical_doc_id: '',
})

const selectedService = computed(() => {
  return services.value.find(s => s.name === subscriptionForm.value.service_name)
})

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

onMounted(async () => {
  try {
    const user = await authService.getCurrentUser()
    subscriptionForm.value.client_id = user.id
    
    const [servicesRes, dashboardRes] = await Promise.all([
      api.get('/services/'),
      api.get(`/users/${user.id}/dashboard`),
    ])
    
    services.value = servicesRes.data
    subscriptions.value = dashboardRes.data.subscriptions || []
  } catch (error) {
    console.error('Failed to load subscriptions:', error)
  } finally {
    loading.value = false
  }
})

const handleCreateSubscription = async () => {
  creating.value = true
  error.value = ''
  
  try {
    const payload = {
      client_id: subscriptionForm.value.client_id,
      service_name: subscriptionForm.value.service_name,
      plan_type: subscriptionForm.value.plan_type,
      medical_doc_id: subscriptionForm.value.medical_doc_id || null,
    }
    
    await api.post('/subscriptions/', payload)
    showCreateModal.value = false
    subscriptionForm.value = {
      client_id: subscriptionForm.value.client_id,
      service_name: '',
      plan_type: '',
      medical_doc_id: '',
    }
    
    // Reload subscriptions
    const user = await authService.getCurrentUser()
    const dashboardRes = await api.get(`/users/${user.id}/dashboard`)
    subscriptions.value = dashboardRes.data.subscriptions || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create subscription'
  } finally {
    creating.value = false
  }
}

const editSubscription = (sub) => {
  editingSubscription.value = sub
  editForm.value = {
    plan_type: sub.plan_type,
    medical_doc_id: sub.medical_doc_id || '',
  }
  showEditModal.value = true
}

const handleUpdateSubscription = async () => {
  updating.value = true
  error.value = ''
  
  try {
    const payload = {}
    if (editForm.value.plan_type) payload.plan_type = editForm.value.plan_type
    if (editForm.value.medical_doc_id !== undefined) payload.medical_doc_id = editForm.value.medical_doc_id || null
    
    await api.put(`/subscriptions/${editingSubscription.value.id}`, payload)
    showEditModal.value = false
    editingSubscription.value = null
    
    // Reload subscriptions
    const user = await authService.getCurrentUser()
    const dashboardRes = await api.get(`/users/${user.id}/dashboard`)
    subscriptions.value = dashboardRes.data.subscriptions || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to update subscription'
  } finally {
    updating.value = false
  }
}

const handleDeleteSubscription = async (subscriptionId) => {
  if (!confirm('Are you sure you want to delete this subscription?')) return
  
  try {
    await api.delete(`/subscriptions/${subscriptionId}`)
    const user = await authService.getCurrentUser()
    const dashboardRes = await api.get(`/users/${user.id}/dashboard`)
    subscriptions.value = dashboardRes.data.subscriptions || []
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to delete subscription')
  }
}
</script>

