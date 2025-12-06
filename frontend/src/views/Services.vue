<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Services</h2>
      <button
        v-if="isAdmin"
        @click="showCreateModal = true"
        class="px-4 py-2 bg-accent hover:bg-accent-dark text-white rounded-md transition-colors"
      >
        Create Service
      </button>
    </div>

    <!-- Create Service Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showCreateModal = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Create Service</h3>
        <form @submit.prevent="handleCreateService" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Name
            </label>
            <input
              v-model="serviceForm.name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            />
          </div>
          <div>
            <label class="flex items-center gap-2">
              <input
                v-model="serviceForm.requires_medical"
                type="checkbox"
                class="rounded border-gray-300 dark:border-gray-600 text-accent focus:ring-accent"
              />
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Requires Medical Certificate</span>
            </label>
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
      <div v-else-if="services.length === 0" class="text-center py-8 text-gray-600 dark:text-gray-400">
        No services found
      </div>
      <table v-else class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead class="bg-gray-50 dark:bg-gray-700">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">ID</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Name</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Requires Medical</th>
            <th v-if="isAdmin" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
          <tr v-for="service in services" :key="service.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">{{ service.id }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">{{ service.name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span
                :class="service.requires_medical ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'"
              >
                {{ service.requires_medical ? 'Yes' : 'No' }}
              </span>
            </td>
            <td v-if="isAdmin" class="px-6 py-4 whitespace-nowrap text-sm">
              <button
                @click="editService(service)"
                class="text-accent hover:underline mr-3"
              >
                Edit
              </button>
              <button
                @click="handleDeleteService(service.id)"
                class="text-red-600 dark:text-red-400 hover:underline"
              >
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Edit Service Modal -->
    <div
      v-if="showEditModal && editingService"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showEditModal = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Edit Service</h3>
        <form @submit.prevent="handleUpdateService" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Name
            </label>
            <input
              v-model="editForm.name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            />
          </div>
          <div>
            <label class="flex items-center gap-2">
              <input
                v-model="editForm.requires_medical"
                type="checkbox"
                class="rounded border-gray-300 dark:border-gray-600 text-accent focus:ring-accent"
              />
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Requires Medical Certificate</span>
            </label>
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

const services = ref([])
const loading = ref(true)
const creating = ref(false)
const updating = ref(false)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const editingService = ref(null)
const error = ref('')

const serviceForm = ref({
  name: '',
  requires_medical: false,
})

const editForm = ref({
  name: '',
  requires_medical: false,
})

const isAdmin = computed(() => {
  const user = authService.getUser()
  return user?.role === 'admin'
})

onMounted(async () => {
  await loadServices()
})

const loadServices = async () => {
  try {
    const response = await api.get('/services/')
    services.value = response.data
  } catch (error) {
    console.error('Failed to load services:', error)
  } finally {
    loading.value = false
  }
}

const handleCreateService = async () => {
  creating.value = true
  error.value = ''
  
  try {
    await api.post('/services/', serviceForm.value)
    showCreateModal.value = false
    serviceForm.value = { name: '', requires_medical: false }
    await loadServices()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create service'
  } finally {
    creating.value = false
  }
}

const editService = (service) => {
  editingService.value = service
  editForm.value = {
    name: service.name,
    requires_medical: service.requires_medical,
  }
  showEditModal.value = true
}

const handleUpdateService = async () => {
  updating.value = true
  error.value = ''
  
  try {
    await api.put(`/services/${editingService.value.id}`, editForm.value)
    showEditModal.value = false
    editingService.value = null
    await loadServices()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to update service'
  } finally {
    updating.value = false
  }
}

const handleDeleteService = async (serviceId) => {
  if (!confirm('Are you sure you want to delete this service?')) return
  
  try {
    await api.delete(`/services/${serviceId}`)
    await loadServices()
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to delete service')
  }
}
</script>

