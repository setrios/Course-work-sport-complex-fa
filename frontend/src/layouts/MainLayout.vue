<template>
  <div class="min-h-screen bg-white dark:bg-gray-900 flex flex-col md:flex-row">
    <!-- Sidebar -->
    <aside class="w-full md:w-64 bg-gray-50 dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 md:fixed md:h-screen overflow-y-auto z-20">
      <div class="p-4">
        <h1 class="text-xl font-bold text-gray-900 dark:text-white mb-6">Sport Complex</h1>
        <nav class="space-y-1">
          <router-link
            v-for="item in menuItems"
            :key="item.path"
            :to="item.path"
            class="flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
            :class="[
              $route.path === item.path || $route.path.startsWith(item.path + '/')
                ? 'bg-accent text-white'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            ]"
          >
            <span>{{ item.label }}</span>
          </router-link>
        </nav>
      </div>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 md:ml-64 flex flex-col min-h-screen">
      <div class="flex-1">
        <!-- Header -->
        <header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-10">
          <div class="px-6 py-4 flex justify-between items-center">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
              {{ currentPageTitle }}
            </h2>
            <div class="flex items-center gap-4">
              <span class="text-sm text-gray-600 dark:text-gray-400">
                {{ currentUser?.full_name || currentUser?.email }}
              </span>
              <button
                @click="handleLogout"
                class="px-3 py-1 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </header>

        <!-- Page Content -->
        <main class="p-6">
          <router-view />
        </main>
      </div>

      <!-- Footer with Theme Toggle -->
      <footer class="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-6 py-4 mt-auto">
        <div class="flex justify-between items-center">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            © 2024 Sport Complex. All rights reserved.
          </p>
          <button
            @click="toggleTheme"
            class="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors"
          >
            <svg v-if="isDark" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
            <span>{{ isDark ? 'Light' : 'Dark' }} Mode</span>
          </button>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authService } from '../services/auth'
import { useTheme } from '../composables/useTheme'
import api from '../services/api'

const router = useRouter()
const route = useRoute()
const { isDark, toggleTheme } = useTheme()

const currentUser = ref(null)

const menuItems = computed(() => {
  const user = authService.getUser()
  const items = [
    { path: '/', label: 'Dashboard' },
    { path: '/sessions', label: 'Sessions' },
    { path: '/services', label: 'Services' },
  ]

  // Only show subscriptions for clients and admins (not trainers)
  if (user?.role !== 'trainer') {
    items.push({ path: '/subscriptions', label: 'Subscriptions' })
  }

  items.push(
    { path: '/products', label: 'Products' },
    { path: '/medical', label: 'Medical' },
    { path: '/profile', label: 'Profile' },
  )

  if (user?.role === 'admin') {
    items.splice(1, 0, { path: '/clients', label: 'Clients' })
    items.splice(2, 0, { path: '/trainers', label: 'Trainers' })
    items.push({ path: '/analytics', label: 'Analytics' })
  }

  return items
})

const currentPageTitle = computed(() => {
  const routeName = route.name
  const titles = {
    Dashboard: 'Dashboard',
    Clients: 'Clients',
    ClientDetail: 'Client Details',
    Trainers: 'Trainers',
    TrainerDetail: 'Trainer Details',
    Sessions: 'Training Sessions',
    Services: 'Services',
    Subscriptions: 'Subscriptions',
    Products: 'Products',
    Medical: 'Medical Documents',
    Analytics: 'Analytics',
    Profile: 'Profile',
  }
  return titles[routeName] || 'Sport Complex'
})

const handleLogout = () => {
  authService.logout()
  router.push('/login')
}

onMounted(async () => {
  try {
    const user = await authService.getCurrentUser()
    currentUser.value = user
  } catch (error) {
    console.error('Failed to fetch user:', error)
  }
})
</script>

