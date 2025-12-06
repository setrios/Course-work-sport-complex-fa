<template>
  <div class="min-h-screen bg-white dark:bg-gray-900 flex items-center justify-center px-4">
    <div class="max-w-md w-full">
      <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-8">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 text-center">Sport Complex</h1>
        <h2 class="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-6 text-center">Register</h2>
        
        <form @submit.prevent="handleRegister" class="space-y-4">
          <div>
            <label for="full_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Full Name
            </label>
            <input
              id="full_name"
              v-model="form.full_name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
              placeholder="John Doe"
            />
          </div>

          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Email
            </label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
              placeholder="your@email.com"
            />
          </div>
          
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Password
            </label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
              placeholder="••••••••"
            />
          </div>

          <div>
            <label for="role" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Register as
            </label>
            <select
              id="role"
              v-model="form.role"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            >
              <option value="client">Client</option>
              <option value="trainer">Trainer</option>
            </select>
          </div>

          <div v-if="form.role === 'trainer'">
            <label for="specialization" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Specialization (optional)
            </label>
            <input
              id="specialization"
              v-model="form.specialization"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
              placeholder="e.g., Yoga, Fitness"
            />
          </div>

          <div v-if="error" class="text-red-600 dark:text-red-400 text-sm">
            {{ error }}
          </div>

          <div v-if="success" class="text-green-600 dark:text-green-400 text-sm">
            {{ success }}
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-accent hover:bg-accent-dark text-white font-medium py-2 px-4 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ loading ? 'Registering...' : 'Register' }}
          </button>
        </form>

        <p class="mt-4 text-center text-sm text-gray-600 dark:text-gray-400">
          Already have an account?
          <router-link to="/login" class="text-accent hover:underline">Login</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const success = ref('')

const form = ref({
  full_name: '',
  email: '',
  password: '',
  role: 'client',
  specialization: '',
})

const handleRegister = async () => {
  loading.value = true
  error.value = ''
  success.value = ''
  
  try {
    const endpoint = form.value.role === 'trainer' ? '/trainers/' : '/clients/'
    const payload = {
      full_name: form.value.full_name,
      email: form.value.email,
      password: form.value.password,
    }
    
    if (form.value.role === 'trainer') {
      payload.specialization = form.value.specialization || null
    }
    
    await api.post(endpoint, payload)
    success.value = 'Registration successful! Redirecting to login...'
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Registration failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

