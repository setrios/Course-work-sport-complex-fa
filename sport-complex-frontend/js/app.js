// Main Application
const app = {
    cart: [],
    currentPage: 'home',

    init() {
        // Set up navigation
        this.setupNavigation();

        // Load initial page
        this.navigate(window.location.hash || '#home');

        // Update cart display
        this.updateCartCount();
    },

    setupNavigation() {
        // Handle hash changes
        window.addEventListener('hashchange', () => {
            this.navigate(window.location.hash);
        });

        // Navigation link clicks
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                e.target.classList.add('active');
            });
        });
    },

    navigate(hash) {
        const page = hash.replace('#', '') || 'home';
        this.currentPage = page;

        // Route to appropriate page
        const routes = {
            'home': () => this.renderHome(),
            'shop': () => this.renderShop(),
            'trainers': () => this.renderTrainers(),
            'clients': () => this.renderClients(),
            'analytics': () => this.renderAnalytics()
        };

        const renderPage = routes[page];
        if (renderPage) {
            renderPage();
        } else {
            this.render404();
        }
    },

    async renderHome() {
        const appEl = document.getElementById('app');
        appEl.innerHTML = components.showLoading();

        try {
            const [products, trainers, bestsellers] = await Promise.all([
                api.getProducts({ limit: 4, is_featured: true }),
                api.getTrainers({ limit: 3 }),
                api.getBestsellers(3)
            ]);

            appEl.innerHTML = `
                <div class="container">
                    <h1 style="text-align: center; margin-bottom: 2rem; font-size: 2.5rem;">
                        💪 Ласкаво просимо до SportComplex
                    </h1>
                    
                    <div class="stats-grid">
                        ${components.createStatCard('🛒', bestsellers.bestsellers?.length || 0, 'Топ продуктів', { from: '#6366f1', to: '#8b5cf6' })}
                        ${components.createStatCard('👤', trainers.length, 'Активних тренерів', { from: '#8b5cf6', to: '#ec4899' })}
                        ${components.createStatCard('📦', products.length, 'Товарів в наявності', { from: '#ec4899', to: '#f59e0b' })}
                    </div>

                    <h2 style="margin: 3rem 0 1rem;">⭐ Рекомендовані продукти</h2>
                    <div class="card-grid">
                        ${products.map(p => components.createProductCard(p)).join('')}
                    </div>

                    <div style="text-align: center; margin-top: 2rem;">
                        <a href="#shop" class="btn" style="display: inline-block; text-decoration: none;">
                            Переглянути всі продукти →
                        </a>
                    </div>

                    <h2 style="margin: 3rem 0 1rem;">🏋️ Наші тренери</h2>
                    <div class="card-grid">
                        ${trainers.map(t => components.createTrainerCard(t)).join('')}
                    </div>
                </div>
            `;
        } catch (error) {
            appEl.innerHTML = `
                <div class="container">
                    ${components.showEmptyState('Помилка завантаження даних', '❌')}
                    <p class="text-center">Переконайтесь, що API сервер запущено на http://localhost:8000</p>
                </div>
            `;
        }
    },

    async renderShop() {
        const appEl = document.getElementById('app');
        appEl.innerHTML = components.showLoading();

        try {
            const products = await api.getProducts({ limit: 50 });

            if (products.length === 0) {
                appEl.innerHTML = `<div class="container">${components.showEmptyState('Немає товарів', '📭')}</div>`;
                return;
            }

            appEl.innerHTML = `
                <div class="container">
                    <h1 style="margin-bottom: 2rem;">🛒 Магазин спортивного харчування</h1>
                    
                    <div class="card-grid">
                        ${products.map(p => components.createProductCard(p)).join('')}
                    </div>
                </div>
            `;
        } catch (error) {
            appEl.innerHTML = `<div class="container">${components.showEmptyState('Помилка завантаження', '❌')}</div>`;
        }
    },

    async renderTrainers() {
        const appEl = document.getElementById('app');
        appEl.innerHTML = components.showLoading();

        try {
            const trainers = await api.getTrainers({ limit: 50 });

            if (trainers.length === 0) {
                appEl.innerHTML = `<div class="container">${components.showEmptyState('Немає тренерів', '👤')}</div>`;
                return;
            }

            appEl.innerHTML = `
                <div class="container">
                    <h1 style="margin-bottom: 2rem;">👤 Наші тренери</h1>
                    
                    <div class="card-grid">
                        ${trainers.map(t => components.createTrainerCard(t)).join('')}
                    </div>
                </div>
            `;
        } catch (error) {
            appEl.innerHTML = `<div class="container">${components.showEmptyState('Помилка завантаження', '❌')}</div>`;
        }
    },

    async renderClients() {
        const appEl = document.getElementById('app');
        appEl.innerHTML = components.showLoading();

        try {
            const clients = await api.getClients({ limit: 100 });

            appEl.innerHTML = `
                <div class="container">
                    <div class="flex-between" style="margin-bottom: 2rem;">
                        <h1>📋 Клієнти</h1>
                        <button class="btn" onclick="app.showAddClientForm()">
                            ➕ Додати клієнта
                        </button>
                    </div>

                    ${clients.length === 0
                    ? components.showEmptyState('Немає клієнтів', '📭')
                    : `<table class="table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Ім'я</th>
                                    <th>Телефон</th>
                                    <th>Дата реєстрації</th>
                                    <th>Дії</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${clients.map(c => components.createClientRow(c)).join('')}
                            </tbody>
                           </table>`
                }
                </div>
            `;
        } catch (error) {
            appEl.innerHTML = `<div class="container">${components.showEmptyState('Помилка завантаження', '❌')}</div>`;
        }
    },

    async renderAnalytics() {
        const appEl = document.getElementById('app');
        appEl.innerHTML = components.showLoading();

        try {
            const [bestsellers, orders] = await Promise.all([
                api.getBestsellers(10),
                api.getOrders({ limit: 10 })
            ]);

            appEl.innerHTML = `
                <div class="container">
                    <h1 style="margin-bottom: 2rem;">📊 Аналітика та статистика</h1>

                    <h2 style="margin: 2rem 0 1rem;">🏆 Топ-10 бестселерів</h2>
                    ${bestsellers.bestsellers && bestsellers.bestsellers.length > 0
                    ? `<table class="table">
                            <thead>
                                <tr>
                                    <th>Місце</th>
                                    <th>ID Продукту</th>
                                    <th>Кількість продажів</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${bestsellers.bestsellers.map((item, index) => `
                                    <tr>
                                        <td>${index + 1}</td>
                                        <td>#${item.product_id}</td>
                                        <td>${Math.round(item.sales_count)}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                           </table>`
                    : components.showEmptyState('Поки що немає даних про продажі', '📊')
                }

                    <h2 style="margin: 3rem 0 1rem;">📦 Останні замовлення</h2>
                    ${orders.length > 0
                    ? `<table class="table">
                            <thead>
                                <tr>
                                    <th>Номер замовлення</th>
                                    <th>Дата</th>
                                    <th>Сума</th>
                                    <th>Статус</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${orders.map(order => `
                                    <tr>
                                        <td>${order.order_number}</td>
                                        <td>${new Date(order.order_date).toLocaleDateString('uk-UA')}</td>
                                        <td>${order.total_amount} грн</td>
                                        <td>${order.status}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                           </table>`
                    : components.showEmptyState('Поки що немає замовлень', '📦')
                }
                </div>
            `;
        } catch (error) {
            appEl.innerHTML = `<div class="container">${components.showEmptyState('Помилка завантаження', '❌')}</div>`;
        }
    },

    // Shopping Cart
    addToCart(productId, productName, price) {
        const existing = this.cart.find(item => item.id === productId);

        if (existing) {
            existing.quantity++;
        } else {
            this.cart.push({
                id: productId,
                name: productName,
                price: price,
                quantity: 1
            });
        }

        this.updateCartCount();
        components.showToast(`${productName} додано в кошик`, 'success');
    },

    updateCartCount() {
        const count = this.cart.reduce((sum, item) => sum + item.quantity, 0);
        document.querySelector('.cart-count').textContent = count;
    },

    showCart() {
        if (this.cart.length === 0) {
            components.showModal('🛒 Кошик', '<p>Ваш кошик порожній</p>');
            return;
        }

        const total = this.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

        const content = `
            <table class="table">
                <thead>
                    <tr>
                        <th>Товар</th>
                        <th>Ціна</th>
                        <th>Кількість</th>
                        <th>Сума</th>
                    </tr>
                </thead>
                <tbody>
                    ${this.cart.map(item => `
                        <tr>
                            <td>${item.name}</td>
                            <td>${item.price} грн</td>
                            <td>${item.quantity}</td>
                            <td>${item.price * item.quantity} грн</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
            <div class="flex-between" style="margin-top: 1rem; font-size: 1.25rem; font-weight: bold;">
                <span>Всього:</span>
                <span>${total} грн</span>
            </div>
            <button class="btn mt-2" onclick="app.checkout()">Оформити замовлення</button>
        `;

        components.showModal('🛒 Кошик', content);
    },

    async checkout() {
        try {
            const orderData = {
                client_id: 1, // Demo client ID
                order_type: 'in_store',
                payment_method: 'card',
                items: this.cart.map(item => ({
                    product_id: item.id,
                    quantity: item.quantity
                }))
            };

            const order = await api.createOrder(orderData);

            components.showToast('Замовлення успішно створено! 🎉', 'success');
            this.cart = [];
            this.updateCartCount();
            components.closeModal();
        } catch (error) {
            components.showToast('Помилка при створенні замовлення', 'error');
        }
    },

    // Client Management
    showAddClientForm() {
        const content = `
            <form onsubmit="app.submitClient(event)" style="max-width: 400px;">
                <div class="form-group">
                    <label class="form-label">Ім'я</label>
                    <input type="text" class="form-input" name="first_name" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Прізвище</label>
                    <input type="text" class="form-input" name="last_name" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Телефон</label>
                    <input type="tel" class="form-input" name="phone" placeholder="+380...">
                </div>
                <button type="submit" class="btn">Створити клієнта</button>
            </form>
        `;

        components.showModal('➕ Додати нового клієнта', content);
    },

    async submitClient(event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        const data = {
            first_name: formData.get('first_name'),
            last_name: formData.get('last_name'),
            phone: formData.get('phone') || null
        };

        try {
            await api.createClient(data);
            components.showToast('Клієнта успішно створено!', 'success');
            components.closeModal();
            this.renderClients();
        } catch (error) {
            components.showToast('Помилка при створенні клієнта', 'error');
        }
    },

    async viewTrainer(trainerId) {
        try {
            const trainer = await api.getTrainer(trainerId);

            const content = `
                <div style="text-align: center;">
                    <div style="font-size: 5rem; margin-bottom: 1rem;">
                        ${trainer.specialization === 'fitness' ? '🏃' :
                    trainer.specialization === 'gym' ? '🏋️' :
                        trainer.specialization === 'pool' ? '🏊' : '💆'}
                    </div>
                    <h2>${trainer.first_name} ${trainer.last_name}</h2>
                    <p style="color: var(--text-muted);">${trainer.specialization}</p>
                    ${trainer.bio ? `<p style="margin-top: 1rem;">${trainer.bio}</p>` : ''}
                    ${trainer.experience_years ? `<p>📅 Досвід: ${trainer.experience_years} років</p>` : ''}
                    ${trainer.hourly_rate ? `<p>💰 Ціна: ${trainer.hourly_rate} грн/год</p>` : ''}
                    <p>⭐ Рейтинг: ${trainer.rating}/5 (${trainer.total_sessions} сесій)</p>
                </div>
            `;

            components.showModal('Профіль тренера', content);
        } catch (error) {
            components.showToast('Помилка завантаження профілю', 'error');
        }
    },

    async viewClient(clientId) {
        try {
            const client = await api.getClient(clientId);

            const content = `
                <h3>${client.first_name} ${client.last_name}</h3>
                <p>📞 Телефон: ${client.phone || '-'}</p>
                <p>📅 Дата реєстрації: ${client.registration_date || '-'}</p>
            `;

            components.showModal('Інформація про клієнта', content);
        } catch (error) {
            components.showToast('Помилка завантаження даних', 'error');
        }
    },

    render404() {
        document.getElementById('app').innerHTML = `
            <div class="container">
                ${components.showEmptyState('Сторінку не знайдено', '🔍')}
            </div>
        `;
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});

// Export for global access
window.app = app;
