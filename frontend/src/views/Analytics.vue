<template>
  <div class="space-y-6">
    <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Analytics</h2>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Popular Services -->
      <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Popular Services</h3>
        <div v-if="loadingServices" class="text-center py-4 text-gray-600 dark:text-gray-400">Loading...</div>
        <div v-else-if="popularServices.length === 0" class="text-center py-4 text-gray-600 dark:text-gray-400">
          No data available
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="(item, index) in popularServices"
            :key="index"
            class="flex justify-between items-center"
          >
            <span class="text-sm text-gray-900 dark:text-white">{{ item.service }}</span>
            <span class="text-sm font-semibold text-accent">{{ item.visitors_count }}</span>
          </div>
        </div>
      </div>

      <!-- Popular Trainers -->
      <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Popular Trainers</h3>
        <div v-if="loadingTrainers" class="text-center py-4 text-gray-600 dark:text-gray-400">Loading...</div>
        <div v-else-if="popularTrainers.length === 0" class="text-center py-4 text-gray-600 dark:text-gray-400">
          No data available
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="(item, index) in popularTrainers"
            :key="index"
            class="flex justify-between items-center"
          >
            <span class="text-sm text-gray-900 dark:text-white">{{ item.trainer }}</span>
            <span class="text-sm font-semibold text-accent">{{ item.sessions_count }}</span>
          </div>
        </div>
      </div>

      <!-- Subscription Stats -->
      <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Subscription Stats</h3>
        <div v-if="loadingSubscriptions" class="text-center py-4 text-gray-600 dark:text-gray-400">Loading...</div>
        <div v-else-if="subscriptionStats.length === 0" class="text-center py-4 text-gray-600 dark:text-gray-400">
          No data available
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="(item, index) in subscriptionStats"
            :key="index"
            class="border-b border-gray-200 dark:border-gray-700 pb-2 last:border-0"
          >
            <p class="text-sm font-medium text-gray-900 dark:text-white">{{ item.service }}</p>
            <p class="text-xs text-gray-600 dark:text-gray-400">{{ item.plan_type }}: {{ item.subscriptions_count }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const popularServices = ref([])
const popularTrainers = ref([])
const subscriptionStats = ref([])
const loadingServices = ref(true)
const loadingTrainers = ref(true)
const loadingSubscriptions = ref(true)

onMounted(async () => {
  try {
    const [servicesRes, trainersRes, subscriptionsRes] = await Promise.all([
      api.get('/analytics/popular-services'),
      api.get('/analytics/popular-trainers'),
      api.get('/analytics/popular-subscriptions'),
    ])
    
    popularServices.value = servicesRes.data.data || []
    popularTrainers.value = trainersRes.data.data || []
    subscriptionStats.value = subscriptionsRes.data.data || []
  } catch (error) {
    console.error('Failed to load analytics:', error)
  } finally {
    loadingServices.value = false
    loadingTrainers.value = false
    loadingSubscriptions.value = false
  }
})
</script>

