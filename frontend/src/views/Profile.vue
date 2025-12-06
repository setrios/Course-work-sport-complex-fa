<template>
  <div class="space-y-6">
    <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Profile</h2>

    <div v-if="loading" class="text-center py-8 text-gray-600 dark:text-gray-400">Loading...</div>
    <div v-else-if="user" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
      <div class="space-y-4">
        <div>
          <label class="text-sm font-medium text-gray-600 dark:text-gray-400">ID</label>
          <p class="text-gray-900 dark:text-white">{{ user.id }}</p>
        </div>
        <div>
          <label class="text-sm font-medium text-gray-600 dark:text-gray-400">Full Name</label>
          <p class="text-gray-900 dark:text-white">{{ user.full_name }}</p>
        </div>
        <div>
          <label class="text-sm font-medium text-gray-600 dark:text-gray-400">Email</label>
          <p class="text-gray-900 dark:text-white">{{ user.email }}</p>
        </div>
        <div>
          <label class="text-sm font-medium text-gray-600 dark:text-gray-400">Role</label>
          <p class="text-gray-900 dark:text-white capitalize">{{ user.role }}</p>
        </div>

      </div>

      <div class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Update Profile</h3>
        <form @submit.prevent="handleUpdate" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Full Name
            </label>
            <input
              v-model="updateForm.full_name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Email
            </label>
            <input
              v-model="updateForm.email"
              type="email"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            />
          </div>

          <div v-if="error" class="text-red-600 dark:text-red-400 text-sm">{{ error }}</div>
          <div v-if="success" class="text-green-600 dark:text-green-400 text-sm">{{ success }}</div>
          <button
            type="submit"
            :disabled="updating"
            class="px-4 py-2 bg-accent hover:bg-accent-dark text-white rounded-md transition-colors disabled:opacity-50"
          >
            {{ updating ? 'Updating...' : 'Update' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { authService } from '../services/auth'
import api from '../services/api'

const user = ref(null)
const loading = ref(true)
const updating = ref(false)
const error = ref('')
const success = ref('')

const updateForm = ref({
  full_name: '',
  email: '',
})

onMounted(async () => {
  try {
    const currentUser = await authService.getCurrentUser()
    user.value = currentUser
    updateForm.value = {
      full_name: currentUser.full_name || '',
      email: currentUser.email || '',
    }
  } catch (error) {
    console.error('Failed to load profile:', error)
  } finally {
    loading.value = false
  }
})

const handleUpdate = async () => {
  updating.value = true
  error.value = ''
  success.value = ''
  
  try {
    const endpoint = user.value.role === 'trainer' ? `/trainers/${user.value.id}` : `/clients/${user.value.id}`
    const payload = {}
    
    if (updateForm.value.full_name) payload.full_name = updateForm.value.full_name
    if (updateForm.value.email) payload.email = updateForm.value.email
    
    await api.put(endpoint, payload)
    success.value = 'Profile updated successfully'
    
    const updatedUser = await authService.getCurrentUser()
    user.value = updatedUser
  } catch (err) {
    error.value = err.response?.data?.detail || 'Update failed'
  } finally {
    updating.value = false
  }
}
</script>

