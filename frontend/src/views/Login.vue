<template>
  <div class="min-h-screen bg-white dark:bg-gray-900 flex items-center justify-center px-4">
    <div class="max-w-md w-full">
      <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-8">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 text-center">Sport Complex</h1>
        <h2 class="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-6 text-center">Login</h2>
        
        <form @submit.prevent="handleLogin" class="space-y-4">
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

          <div v-if="error" class="text-red-600 dark:text-red-400 text-sm">
            {{ error }}
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-accent hover:bg-accent-dark text-white font-medium py-2 px-4 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ loading ? 'Logging in...' : 'Login' }}
          </button>
        </form>

        <p class="mt-4 text-center text-sm text-gray-600 dark:text-gray-400">
          Don't have an account?
          <router-link to="/register" class="text-accent hover:underline">Register</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '../services/auth'

const router = useRouter()
const loading = ref(false)
const error = ref('')

const form = ref({
  email: '',
  password: '',
})

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  
  try {
    await authService.login(form.value.email, form.value.password)
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Login failed. Please check your credentials.'
  } finally {
    loading.value = false
  }
}
</script>

