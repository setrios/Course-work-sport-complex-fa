// ==========================================
// API Configuration & Utilities
// ==========================================

const API_BASE_URL = 'http://127.0.0.1:8000';

// Get Authorization header
function getAuthHeaders() {
    const token = localStorage.getItem('authToken');
    const headers = {
        'Content-Type': 'application/json'
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

// Generic fetch wrapper
async function apiFetch(endpoint, options = {}, skipLogoutHandler = false) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = getAuthHeaders();

    try {
        console.log(`[API Request] ${options.method || 'GET'} ${url}`);
        console.log(`[API Headers] ${JSON.stringify(headers)}`);
        if (options.body) {
            try {
                const bodyObj = typeof options.body === 'string' ? JSON.parse(options.body) : options.body;
                console.log(`[API Body] ${JSON.stringify(bodyObj)}`);
            } catch (e) {
                console.log(`[API Body] ${options.body}`);
            }
        } else {
            console.log(`[API Body] none`);
        }

        const response = await fetch(url, {
            ...options,
            headers: { ...headers, ...options.headers }
        });

        // Log the request for debugging
        console.log(`[API] ${options.method || 'GET'} ${endpoint} - Status: ${response.status}`);

        if (response.status === 401 && !skipLogoutHandler) {
            // Token expired or invalid - only handle logout for non-logout endpoints
            if (endpoint !== '/auth/logout') {
                // Clear token and update UI without making another API call
                localStorage.removeItem('authToken');
                localStorage.removeItem('authRole');
                
                if (typeof showLoginUI === 'function') {
                    showLoginUI();
                }
            }
            throw new Error('Сесія закінчилася. Будь ласка, увійдіть знову.');
        }

        if (!response.ok) {
            let errorDetail = `API Error: ${response.status}`;
            try {
                const errorData = await response.json();
                errorDetail = errorData.detail || errorDetail;
                if (errorData.errors) {
                    errorDetail += ` - Validation errors: ${JSON.stringify(errorData.errors)}`;
                }
            } catch (e) {
                // Could not parse error response
            }
            console.error(`[API Error] ${errorDetail}`);
            throw new Error(errorDetail);
        }

        const responseData = await response.json();
        console.log(`[API Response] ${endpoint}:`, responseData);
        return responseData;
    } catch (error) {
        console.error('[API Fetch Error]', error.message, error);
        throw error;
    }
}

// GET request
async function apiGet(endpoint) {
    return apiFetch(endpoint, { method: 'GET' });
}

// POST request
async function apiPost(endpoint, data) {
    return apiFetch(endpoint, {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

// PUT request
async function apiPut(endpoint, data) {
    return apiFetch(endpoint, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

// DELETE request
async function apiDelete(endpoint) {
    return apiFetch(endpoint, { method: 'DELETE' });
}

// Specific API endpoints
const API = {
    // Health
    health: () => fetch(`${API_BASE_URL}/health`).then(r => r.json()),

    // Auth
    login: (username, password) => apiPost('/auth/login', { username, password }),
    logout: () => apiPost('/auth/logout', {}),
    me: () => apiGet('/auth/me'),

    // Sport Clients
    clients: {
        list: () => apiGet('/sport/clients'),
        create: (data) => apiPost('/sport/clients', data),
        get: (id) => apiGet(`/sport/clients/${id}`),
        update: (id, data) => apiFetch(`/sport/clients/${id}`, {
            method: 'PUT',
            headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }),
        delete: (id) => apiFetch(`/sport/clients/${id}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        }),
    },

    // Sport Trainers
    trainers: {
        list: () => apiGet('/sport/trainers'),
        create: (data) => apiPost('/sport/trainers', data),
        update: (id, data) => apiPut(`/sport/trainers/${id}`, data),
        delete: (id) => apiDelete(`/sport/trainers/${id}`),
    },

    // Sport Services
    services: {
        list: () => apiGet('/sport/services'),
        create: (data) => apiPost('/sport/services', data),
        update: (id, data) => apiPut(`/sport/services/${id}`, data),
        delete: (id) => apiDelete(`/sport/services/${id}`),
    },

    // Bookings for current user
    bookings: {
        list: () => apiGet('/sport/user/bookings'),
        create: (data) => apiPost('/sport/user/bookings', data),
        delete: (bookingId) => apiDelete(`/sport/user/bookings/${bookingId}`),
    },

    // Memberships
    memberships: {
        list: () => apiGet('/sport/memberships'),
        create: (data) => apiPost('/sport/memberships', data),
        update: (id, data) => apiPut(`/sport/memberships/${id}`, data),
        delete: (id) => apiDelete(`/sport/memberships/${id}`),
    },

    // Current user membership
    userMembership: () => apiGet('/sport/user/membership'),

    // Current user profile
    userProfile: {
        get: () => apiGet('/sport/user/profile'),
        update: (data) => apiPut('/sport/user/profile', data),
    },

    // Visits
    visits: {
        list: () => apiGet('/sport/visits'),
        create: (data) => apiPost('/sport/visits', data),
    },

    // Sport analytics & reports
    sportAnalytics: () => apiGet('/sport/analytics'),
    sportReports: () => apiGet('/sport/reports'),

    // E-commerce
    suppliers: {
        list: () => apiGet('/suppliers/'),
        create: (data) => apiPost('/suppliers/', data),
    },

    categories: {
        list: () => apiGet('/categories/'),
        create: (data) => apiPost('/categories/', data),
    },

    products: {
        list: () => apiGet('/products/assortment'),
        search: (query) => apiGet(`/products/search/${encodeURIComponent(query)}`),
        byArticle: (article) => apiGet(`/products/by-article/${encodeURIComponent(article)}`),
        stockExtremes: () => apiGet('/products/stock-extremes'),
        getImage: (article) => apiGet(`/products/image/${encodeURIComponent(article)}`),
        uploadImage: (article, imageBase64, mimeType) => apiPost('/products/upload-image/', {
            article,
            image_base64: imageBase64,
            mime_type: mimeType
        }),
        create: (data) => apiPost('/products/', data),
        update: (article, data) => apiFetch(`/products/${encodeURIComponent(article)}`, {
            method: 'PUT',
            headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }),
        delete: (article) => apiFetch(`/products/${encodeURIComponent(article)}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        }),
    },

    orders: {
        lowStock: () => apiGet('/orders/low-stock-report'),
    },

    // Database Queries (Admin only)
    dbQueries: {
        products: () => apiGet('/db/products/images'),
        assortment: () => apiGet('/db/assortment'),
        priceQty: () => apiGet('/db/price-availability'),
        minMax: () => apiGet('/db/min-max-products'),
        suppliers: () => apiGet('/db/suppliers'),
        inventory: (article) => apiGet(`/db/inventory-history${article ? `?article=${encodeURIComponent(article)}` : ''}`),
        orders: (productId, quantity) => apiPost('/db/generate-order', { product_id: productId, quantity }),
        generateOrder: (payload) => apiPost('/db/generate-order', payload),
        syncProducts: () => apiGet('/db/sync-products')
    }
};

// Utility functions
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('uk-UA');
}

function formatDateTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('uk-UA') + ' ' + date.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' });
}

function formatPrice(price) {
    return new Intl.NumberFormat('uk-UA', {
        style: 'currency',
        currency: 'UAH'
    }).format(price);
}
