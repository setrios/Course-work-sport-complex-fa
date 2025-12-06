<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Products</h2>
      <button
        v-if="isAdmin"
        @click="showCreateModal = true"
        class="px-4 py-2 bg-accent hover:bg-accent-dark text-white rounded-md transition-colors"
      >
        Add Product
      </button>
    </div>

    <!-- Create Product Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showCreateModal = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Add Product</h3>
        <form @submit.prevent="handleCreateProduct" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Name
            </label>
            <input
              v-model="productForm.name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Price
            </label>
            <input
              v-model.number="productForm.price"
              type="number"
              step="0.01"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Stock
            </label>
            <input
              v-model.number="productForm.stock"
              type="number"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Description
            </label>
            <textarea
              v-model="productForm.description"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            ></textarea>
          </div>
          <div>
            <label class="flex items-center gap-2">
              <input
                v-model="productForm.available"
                type="checkbox"
                class="rounded border-gray-300 dark:border-gray-600 text-accent focus:ring-accent"
              />
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Available</span>
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

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="product in products"
        :key="product.id"
        class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6"
      >
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">{{ product.name }}</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">{{ product.description || 'No description' }}</p>
        <p class="text-xl font-bold text-gray-900 dark:text-white mb-2">${{ product.price.toFixed(2) }}</p>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Stock: <span :class="product.stock > 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
            {{ product.stock }}
          </span>
        </p>
        <div v-if="isAdmin" class="flex gap-2">
          <button
            @click="editProduct(product)"
            class="flex-1 px-3 py-2 bg-accent hover:bg-accent-dark text-white rounded-md transition-colors text-sm"
          >
            Edit
          </button>
          <button
            @click="handleDeleteProduct(product.id)"
            class="px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md transition-colors text-sm"
          >
            Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Edit Product Modal -->
    <div
      v-if="showEditModal && editingProduct"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showEditModal = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Edit Product</h3>
        <form @submit.prevent="handleUpdateProduct" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Name
            </label>
            <input
              v-model="editForm.name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Price
            </label>
            <input
              v-model.number="editForm.price"
              type="number"
              step="0.01"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Stock
            </label>
            <input
              v-model.number="editForm.stock"
              type="number"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Description
            </label>
            <textarea
              v-model="editForm.description"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-accent"
            ></textarea>
          </div>
          <div>
            <label class="flex items-center gap-2">
              <input
                v-model="editForm.available"
                type="checkbox"
                class="rounded border-gray-300 dark:border-gray-600 text-accent focus:ring-accent"
              />
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Available</span>
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

const products = ref([])
const loading = ref(true)
const creating = ref(false)
const updating = ref(false)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const editingProduct = ref(null)
const error = ref('')

const productForm = ref({
  name: '',
  price: 0,
  stock: 0,
  description: '',
  available: true,
})

const editForm = ref({
  name: '',
  price: 0,
  stock: 0,
  description: '',
  available: true,
})

const isAdmin = computed(() => {
  const user = authService.getUser()
  return user?.role === 'admin'
})

onMounted(async () => {
  await loadProducts()
})

const loadProducts = async () => {
  try {
    const response = await api.get('/products/')
    products.value = response.data
  } catch (error) {
    console.error('Failed to load products:', error)
  } finally {
    loading.value = false
  }
}

const handleCreateProduct = async () => {
  creating.value = true
  error.value = ''
  
  try {
    await api.post('/products/', productForm.value)
    showCreateModal.value = false
    productForm.value = { name: '', price: 0, stock: 0, description: '', available: true }
    await loadProducts()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create product'
  } finally {
    creating.value = false
  }
}

const editProduct = (product) => {
  editingProduct.value = product
  editForm.value = {
    name: product.name,
    price: product.price,
    stock: product.stock,
    description: product.description || '',
    available: product.available,
  }
  showEditModal.value = true
}

const handleUpdateProduct = async () => {
  updating.value = true
  error.value = ''
  
  try {
    const payload = {}
    if (editForm.value.name) payload.name = editForm.value.name
    if (editForm.value.price !== undefined) payload.price = editForm.value.price
    if (editForm.value.stock !== undefined) payload.stock = editForm.value.stock
    if (editForm.value.description !== undefined) payload.description = editForm.value.description
    if (editForm.value.available !== undefined) payload.available = editForm.value.available
    
    await api.put(`/products/${editingProduct.value.id}`, payload)
    showEditModal.value = false
    editingProduct.value = null
    await loadProducts()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to update product'
  } finally {
    updating.value = false
  }
}

const handleDeleteProduct = async (productId) => {
  if (!confirm('Are you sure you want to delete this product?')) return
  
  try {
    await api.delete(`/products/${productId}`)
    await loadProducts()
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to delete product')
  }
}
</script>

