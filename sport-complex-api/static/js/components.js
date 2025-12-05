// UI Components

// Toast Notification
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Modal
function showModal(title, content) {
    const container = document.getElementById('modal-container');

    const modalHTML = `
        <div class="modal-overlay" onclick="closeModal(event)">
            <div class="modal" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <span class="modal-close" onclick="closeModal()">&times;</span>
                    ${title}
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        </div>
    `;

    container.innerHTML = modalHTML;
}

function closeModal(event) {
    if (!event || event.target.classList.contains('modal-overlay')) {
        document.getElementById('modal-container').innerHTML = '';
    }
}

// Product Card Component
function createProductCard(product) {
    const icon = {
        'sports_nutrition': '🥤',
        'supplements': '💊',
        'water': '💧',
        'snacks': '🍫',
        'accessories': '🎽'
    }[product.category_id] || '📦';

    return `
        <div class="card product-card">
            <div class="product-image">${icon}</div>
            <div class="product-info">
                <h3>${product.name}</h3>
                ${product.brand ? `<p class="text-muted">${product.brand}</p>` : ''}
                <div class="product-price">${product.price} грн</div>
                <div class="product-stock">
                    ${product.quantity_in_stock > 0
            ? `✅ В наявності: ${product.quantity_in_stock}`
            : '❌ Немає в наявності'}
                </div>
                ${product.quantity_in_stock > 0
            ? `<button class="btn" onclick="app.addToCart(${product.id}, '${product.name}', ${product.price})">
                        🛒 Додати в кошик
                       </button>`
            : '<button class="btn" disabled>Немає в наявності</button>'}
            </div>
        </div>
    `;
}

// Trainer Card Component
function createTrainerCard(trainer) {
    const specializationIcon = {
        'fitness': '🏃',
        'gym': '🏋️',
        'pool': '🏊',
        'massage': '💆'
    }[trainer.specialization] || '👤';

    const rating = '⭐'.repeat(Math.round(trainer.rating || 0));

    return `
        <div class="card">
            <div class="product-image">${specializationIcon}</div>
            <div class="product-info">
                <h3>${trainer.first_name} ${trainer.last_name}</h3>
                <p class="text-muted">${trainer.specialization}</p>
                ${rating ? `<div class="mt-1">${rating} (${trainer.rating}/5)</div>` : ''}
                ${trainer.experience_years ? `<p>📅 Досвід: ${trainer.experience_years} років</p>` : ''}
                ${trainer.hourly_rate ? `<div class="product-price">${trainer.hourly_rate} грн/год</div>` : ''}
                ${trainer.bio ? `<p class="text-muted mt-1">${trainer.bio.substring(0, 100)}...</p>` : ''}
                <button class="btn mt-1" onclick="app.viewTrainer(${trainer.id})">
                    Переглянути профіль
                </button>
            </div>
        </div>
    `;
}

// Client Row Component
function createClientRow(client) {
    return `
        <tr>
            <td>${client.id}</td>
            <td>${client.first_name} ${client.last_name}</td>
            <td>${client.phone || '-'}</td>
            <td>${client.registration_date || '-'}</td>
            <td>
                <button class="btn btn-secondary" onclick="app.viewClient(${client.id})">
                    📋 Переглянути
                </button>
            </td>
        </tr>
    `;
}

// Stat Card Component
function createStatCard(icon, value, label, gradient = null) {
    const style = gradient
        ? `background: linear-gradient(135deg, ${gradient.from}, ${gradient.to});`
        : '';

    return `
        <div class="stat-card" style="${style}">
            <div class="stat-icon" style="font-size: 3rem;">${icon}</div>
            <div class="stat-value">${value}</div>
            <div class="stat-label">${label}</div>
        </div>
    `;
}

// Loading Spinner
function showLoading() {
    return `
        <div class="loading">
            <div class="spinner"></div>
            <p>Завантаження...</p>
        </div>
    `;
}

// Empty State
function showEmptyState(message, icon = '📭') {
    return `
        <div class="text-center" style="padding: 4rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">${icon}</div>
            <h3>${message}</h3>
        </div>
    `;
}

// Export components
window.components = {
    showToast,
    showModal,
    closeModal,
    createProductCard,
    createTrainerCard,
    createClientRow,
    createStatCard,
    showLoading,
    showEmptyState
};
