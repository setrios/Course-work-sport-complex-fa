// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// API Service
const api = {
    // Generic fetch wrapper
    async fetch(endpoint, options = {}) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    // Products
    async getProducts(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.fetch(`/products?${query}`);
    },

    async getProduct(id) {
        return this.fetch(`/products/${id}`);
    },

    async createProduct(data) {
        return this.fetch('/products', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    // Trainers
    async getTrainers(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.fetch(`/trainers?${query}`);
    },

    async getTrainer(id) {
        return this.fetch(`/trainers/${id}`);
    },

    async createTrainer(data) {
        return this.fetch('/trainers', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async getTrainerSchedule(trainerId) {
        return this.fetch(`/trainers/${trainerId}/schedules`);
    },

    // Clients
    async getClients(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.fetch(`/clients?${query}`);
    },

    async getClient(id) {
        return this.fetch(`/clients/${id}`);
    },

    async createClient(data) {
        return this.fetch('/clients', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async getClientSessions(clientId) {
        return this.fetch(`/clients/${clientId}/sessions`);
    },

    async getClientOrders(clientId) {
        return this.fetch(`/clients/${clientId}/orders`);
    },

    // Orders
    async createOrder(data) {
        return this.fetch('/orders', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async getOrders(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.fetch(`/orders?${query}`);
    },

    // Services
    async getServices() {
        return this.fetch('/services');
    },

    // Analytics
    async getBestsellers(limit = 10) {
        return this.fetch(`/analytics/bestsellers?limit=${limit}`);
    },

    async getOnlineUsers() {
        return this.fetch('/analytics/online-users');
    },

    // Recommendations
    async getProductRecommendations(clientId, limit = 5) {
        return this.fetch(`/recommendations/products/${clientId}?limit=${limit}`);
    },

    async getTrainerRecommendations(clientId, limit = 5) {
        return this.fetch(`/recommendations/trainers/${clientId}?limit=${limit}`);
    },

    // Bookings
    async createBooking(data) {
        return this.fetch('/bookings', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async getBookings() {
        return this.fetch('/bookings');
    },

    // Authentication
    async login(data) {
        return this.fetch('/auth/login', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async register(data) {
        return this.fetch('/auth/register', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
};

// Export for use in other files
window.api = api;
