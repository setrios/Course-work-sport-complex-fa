// Main Application
const app = {
    cart: [],
    currentPage: 'home',
    currentUser: null,

    init() {
        this.checkAuth();
        this.setupNavigation();
        this.navigate(window.location.hash || '#home');
        this.updateCartCount();
    },

    checkAuth() {
        const token = localStorage.getItem('auth_token');
        const user = localStorage.getItem('user_data');

        if (token && user) {
            this.currentUser = JSON.parse(user);
            this.updateAuthUI();
        }
    },

    updateAuthUI() {
        const authButton = document.getElementById('auth-button');
        const userInfo = document.getElementById('user-info');
        const userName = document.getElementById('user-name');

        if (this.currentUser) {
            userInfo.style.display = 'inline';
            userName.textContent = this.currentUser.name;
            authButton.textContent = '🚪 Вихід';
            authButton.onclick = () => this.logout();
        } else {
            userInfo.style.display = 'none';
            authButton.textContent = '🔐 Вхід';
            authButton.onclick = () => this.showLogin();
        }

        this.updateNavigation();
    },

    updateNavigation() {
        const clientsLink = document.querySelector('a[href="#clients"]');
        const bookingsLink = document.querySelector('a[href="#bookings"]');
        const analyticsLink = document.querySelector('a[href="#analytics"]');

        if (this.currentUser && this.currentUser.role === 'admin') {
            if (clientsLink) clientsLink.style.display = '';
            if (bookingsLink) bookingsLink.style.display = '';
            if (analyticsLink) analyticsLink.style.display = '';
        } else {
            if (clientsLink) clientsLink.style.display = 'none';
            if (bookingsLink) bookingsLink.style.display = 'none';
            if (analyticsLink) analyticsLink.style.display = 'none';
        }
    },

    setupNavigation() {
        window.addEventListener('hashchange', () => {
            this.navigate(window.location.hash);
        });

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

        const routes = {
            'home': () => this.renderHome(),
            'shop': () => this.renderShop(),
            'services': () => this.renderServices(),
            'trainers': () => this.renderTrainers(),
            'clients': () => this.renderClients(),
            'bookings': () => this.renderBookings(),
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
            const products = await api.getProducts({ limit: 20 });

            appEl.innerHTML = `
                <div class="container">
                    <h1 style="margin-bottom: 2rem;">🛒 Магазин спорттоварів</h1>
                    <div class="card-grid">
                        ${products.map(product => `
                            <div class="card">
                                <div class="product-image">${this.getProductIcon(product.category)}</div>
                                <h3>${product.name}</h3>
                                <p class="text-muted">${product.category}</p>
                                <p style="margin: 1rem 0;">${product.description || ''}</p>
                                <div class="flex-between">
                                    <strong>${product.price} грн</strong>
                                    <span class="text-muted">На складі: ${product.quantity_in_stock}</span>
                                </div>
                                <button 
                                    class="btn mt-1" 
                                    onclick="app.addToCart(${product.id}, '${product.name}', ${product.price})"
                                    ${product.quantity_in_stock === 0 ? 'disabled' : ''}
                                >
                                    ${product.quantity_in_stock === 0 ? '❌ Немає в наявності' : '➕ В кошик'}
                                </button>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        } catch (error) {
            appEl.innerHTML = `<div class="container">${components.showEmptyState('Помилка завантаження', '❌')}</div>`;
        }
    },

    async renderServices() {
        const appEl = document.getElementById('app');
        appEl.innerHTML = components.showLoading();

        try {
            const services = await api.getServices();

            appEl.innerHTML = `
                <div class="container">
                    <h1 style="margin-bottom: 2rem;">🏋️ Наші послуги</h1>
                    <div class="card-grid">
                        ${services.map(service => `
                            <div class="card">
                                <div class="product-image">${this.getServiceIcon(service.service_type)}</div>
                                <h3>${service.name}</h3>
                                <p class="text-muted">${service.service_type}</p>
                                <p style="margin: 1rem 0;">${service.description || ''}</p>
                                <div class="flex-between" style="margin: 1rem 0;">
                                    <span><strong>${service.price}</strong> грн</span>
                                    <span class="text-muted">⏱️ ${service.duration_minutes} хв</span>
                                </div>
                                <button class="btn mt-1" onclick="app.bookService(${service.id}, '${service.name}', ${service.price})">
                                    📅 Забронювати
                                </button>
                            </div>
                        `).join('')}
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
            const trainers = await api.getTrainers({ limit: 20 });
            let bookings = [];
            const isAdmin = this.currentUser && this.currentUser.role === 'admin';

            if (isAdmin) {
                bookings = await api.getBookings();
            }

            appEl.innerHTML = `
                <div class="container">
                    <h1 style="margin-bottom: 2rem;">👥 Наші тренери</h1>
                    <div class="card-grid">
                        ${trainers.map(trainer => {
                // Filter bookings for this trainer
                const trainerBookings = isAdmin ? bookings.filter(b =>
                    b.trainer_name &&
                    b.trainer_name.includes(trainer.last_name) &&
                    b.status !== 'cancelled'
                ).sort((a, b) => new Date(a.date + 'T' + a.time.substring(0, 5)) - new Date(b.date + 'T' + b.time.substring(0, 5))) : [];

                return `
                            <div class="card" onclick="app.viewTrainer(${trainer.id})" style="cursor: pointer;">
                                <div class="product-image">${this.getTrainerIcon(trainer.specialization)}</div>
                                <h3>${trainer.first_name} ${trainer.last_name}</h3>
                                <p class="text-muted">${trainer.specialization}</p>
                                ${trainer.bio ? `<p style="margin: 1rem 0;">${trainer.bio.substring(0, 100)}...</p>` : ''}
                                <div class="flex-between">
                                    <span>⭐ ${trainer.rating}/5</span>
                                    <span class="text-muted">${trainer.total_sessions} сесій</span>
                                </div>
                                <div style="margin-top: 1rem;">
                                    <strong>${trainer.hourly_rate}</strong> грн/год
                                </div>
                                ${isAdmin ? `
                                    <div style="margin-top: 1rem; border-top: 1px solid var(--border-color); padding-top: 0.5rem;">
                                        <p style="font-size: 0.85rem; font-weight: bold;">📅 Зайняті слоти:</p>
                                        ${trainerBookings.length > 0 ?
                            `<ul style="font-size: 0.8rem; list-style: none; padding: 0; max-height: 100px; overflow-y: auto;">
                                                ${trainerBookings.map(b => `
                                                    <li style="margin-bottom: 2px;">
                                                        <span style="color: var(--primary);">●</span> 
                                                        ${new Date(b.date).toLocaleDateString('uk-UA')} ${b.time}
                                                    </li>
                                                `).join('')}
                                            </ul>`
                            : '<p style="font-size: 0.8rem; color: var(--text-muted);">Вільний графік</p>'
                        }
                                    </div>
                                ` : ''}
                            </div>
                            `;
            }).join('')}
                    </div>
                </div>
            `;
        } catch (error) {
            appEl.innerHTML = `<div class="container">${components.showEmptyState('Помилка завантаження', '❌')}</div>`;
        }
    },

    async renderClients() {
        const appEl = document.getElementById('app');

        if (!this.currentUser || this.currentUser.role !== 'admin') {
            appEl.innerHTML = `
                <div class="container">
                    ${components.showEmptyState('Доступ заборонено', '🔒')}
                </div>
            `;
            return;
        }

        appEl.innerHTML = components.showLoading();

        try {
            const clients = await api.getClients({ limit: 50 });

            appEl.innerHTML = `
                <div class="container">
                    <div class="flex-between" style="margin-bottom: 2rem;">
                        <h1>👥 Клієнти</h1>
                        <button class="btn" onclick="app.showAddClientForm()">➕ Додати клієнта</button>
                    </div>
                    ${clients.length > 0
                    ? `<table class="table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Ім'я</th>
                                    <th>Прізвище</th>
                                    <th>Телефон</th>
                                    <th>Дія</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${clients.map(client => `
                                    <tr>
                                        <td>${client.id}</td>
                                        <td>${client.first_name}</td>
                                        <td>${client.last_name}</td>
                                        <td>${client.phone || '-'}</td>
                                        <td>
                                            <button class="btn btn-secondary sm" onclick="app.viewClient(${client.id})">
                                                👁️ Переглянути
                                            </button>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                           </table>`
                    : components.showEmptyState('Поки що немає клієнтів', '👥')
                }
                </div>
            `;
        } catch (error) {
            appEl.innerHTML = `<div class="container">${components.showEmptyState('Помилка завантаження', '❌')}</div>`;
        }
    },

    async renderBookings() {
        const appEl = document.getElementById('app');

        if (!this.currentUser || this.currentUser.role !== 'admin') {
            appEl.innerHTML = `
                <div class="container">
                    ${components.showEmptyState('Доступ заборонено', '🔒')}
                    <p class="text-center">Ця сторінка доступна тільки адміністраторам</p>
                </div>
            `;
            return;
        }

        appEl.innerHTML = components.showLoading();

        try {
            const bookings = await api.getBookings();

            appEl.innerHTML = `
                <div class="container">
                    <h1 style="margin-bottom: 2rem;">📅 Бронювання</h1>

                    ${bookings.length === 0
                    ? components.showEmptyState('Немає бронювань', '📭')
                    : `<table class="table">
                            <thead>
                                <tr>
                                    <th>Номер</th>
                                    <th>Послуга</th>
                                    <th>Тренер</th>
                                    <th>Дата</th>
                                    <th>Час</th>
                                    <th>Статус</th>
                                    <th>Примітки</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${bookings.map(b => `
                                    <tr>
                                        <td><strong>${b.booking_number}</strong></td>
                                        <td>${b.service_name}</td>
                                        <td>${b.trainer_name || '-'}</td>
                                        <td>${new Date(b.date).toLocaleDateString('uk-UA')}</td>
                                        <td>${b.time}</td>
                                        <td><span style="color: var(--success)">${b.status}</span></td>
                                        <td>${b.notes || '-'}</td>
                                    </tr>
                                `).join('')}
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

        if (!this.currentUser || this.currentUser.role !== 'admin') {
            appEl.innerHTML = `
                <div class="container">
                    ${components.showEmptyState('Доступ заборонено', '🔒')}
                </div>
            `;
            return;
        }

        appEl.innerHTML = components.showLoading();

        try {
            const [bestsellers, orders, products] = await Promise.all([
                api.getBestsellers(10),
                api.getOrders({ limit: 10 }),
                api.getProducts({ limit: 100 })
            ]);

            const productMap = {};
            products.forEach(p => productMap[p.id] = p);

            appEl.innerHTML = `
                <div class="container">
                    <h1 style="margin-bottom: 2rem;">📊 Аналітика та статистика</h1>

                    <h2 style="margin: 2rem 0 1rem;">🏆 Бестселери</h2>
                    ${bestsellers.bestsellers && bestsellers.bestsellers.length > 0
                    ? `<table class="table">
                            <thead>
                                <tr>
                                    <th>Місце</th>
                                    <th>Товар</th>
                                    <th>Продано</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${bestsellers.bestsellers.map((item, index) => {
                        const product = productMap[item.product_id];
                        return `
                                    <tr>
                                        <td><strong>${index + 1}</strong></td>
                                        <td>${product ? product.name : `Товар #${item.product_id}`}</td>
                                        <td><strong>${item.sales_count}</strong> шт</td>
                                    </tr>
                                `}).join('')}
                            </tbody>
                           </table>`
                    : components.showEmptyState('Поки що немає даних про продажі', '📊')
                }

                    <h2 style="margin: 3rem 0 1rem;">📦 Останні замовлення</h2>
                    ${orders.length > 0
                    ? `<table class="table">
                            <thead>
                                <tr>
                                    <th>Номер</th>
                                    <th>Дата</th>
                                    <th>Товари</th>
                                    <th>Сума</th>
                                    <th>Статус</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${orders.map(order => {
                        const items = order.items || [];
                        const itemsText = items.map(item => {
                            const product = productMap[item.product_id];
                            return `${product ? product.name : 'Товар #' + item.product_id} x${item.quantity}`;
                        }).join(', ');

                        const statusColor = order.status === 'completed' ? 'var(--success)' :
                            order.status === 'pending' ? 'var(--warning)' : 'var(--text-muted)';

                        return `
                                    <tr onclick="app.viewOrderDetails(${order.id})" style="cursor: pointer;">
                                        <td><strong>${order.order_number}</strong></td>
                                        <td>${new Date(order.order_date).toLocaleDateString('uk-UA')}</td>
                                        <td style="max-width: 300px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                            ${itemsText || 'Немає товарів'}
                                        </td>
                                        <td><strong>${order.total_amount}</strong> грн</td>
                                        <td><span style="color: ${statusColor};">⬤</span> ${order.status}</td>
                                    </tr>
                                `}).join('')}
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

    async viewOrderDetails(orderId) {
        try {
            const [orders, products] = await Promise.all([
                api.getOrders({}),
                api.getProducts({})
            ]);

            const order = orders.find(o => o.id === orderId);
            if (!order) {
                components.showToast('Замовлення не знайдено', 'error');
                return;
            }

            const productMap = {};
            products.forEach(p => productMap[p.id] = p);

            const items = order.items || [];

            const content = `
                <div>
                    <h3>Замовлення ${order.order_number}</h3>
                    <p><strong>Дата:</strong> ${new Date(order.order_date).toLocaleString('uk-UA')}</p>
                    <p><strong>Статус:</strong> ${order.status}</p>
                    
                    <h4 style="margin-top: 2rem;">Товари:</h4>
                    ${items.length > 0 ? `
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
                                ${items.map(item => {
                const product = productMap[item.product_id];
                return `
                                        <tr>
                                            <td>${product ? product.name : 'Товар #' + item.product_id}</td>
                                            <td>${item.price} грн</td>
                                            <td>${item.quantity}</td>
                                            <td><strong>${item.price * item.quantity}</strong> грн</td>
                                        </tr>
                                    `;
            }).join('')}
                            </tbody>
                        </table>
                    ` : '<p>Немає товарів</p>'}
                    
                    <div style="text-align: right; margin-top: 1rem; padding-top: 1rem; border-top: 2px solid var(--border);">
                        <h3>Всього: ${order.total_amount} грн</h3>
                    </div>
                </div>
            `;

            components.showModal('📦 Деталі замовлення', content);
        } catch (error) {
            components.showToast('Помилка завантаження деталей', 'error');
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
                client_id: 1,
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

            if (this.currentPage === 'shop') {
                this.renderShop();
            }
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
                        ${this.getTrainerIcon(trainer.specialization)}
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

    // Simple Service Booking
    async bookService(serviceId, serviceName, price) {
        try {
            const [services, trainers, bookings] = await Promise.all([
                api.getServices(),
                api.getTrainers(),
                api.getBookings()
            ]);

            const service = services.find(s => s.id === serviceId);
            const isGroup = serviceName.includes('Групове');

            const content = `
                <div style="max-width: 600px;">
                    <h3>📅 Бронювання послуги</h3>
                    <p><strong>Послуга:</strong> ${serviceName}</p>
                    <p><strong>Ціна:</strong> ${price} грн</p>
                    <p><strong>Тривалість:</strong> 60 хвилин</p>
                    
                    <form id="booking-form" onsubmit="event.preventDefault(); app.submitBooking('${serviceName}')" style="margin-top: 2rem;">
                        <input type="hidden" name="time" id="selected-time">
                        
                        ${!isGroup ? `
                        <div class="form-group">
                            <label class="form-label">👤 Оберіть тренера</label>
                            <select class="form-input" name="trainer_id" onchange="app.renderSlots(this.value, '${serviceName}', '${new Date().toISOString().split('T')[0]}')">
                                <option value="">-- Оберіть тренера --</option>
                                ${trainers.map(t => `<option value="${t.id}">${t.first_name} ${t.last_name} (${t.specialization})</option>`).join('')}
                            </select>
                        </div>` : ''}

                        <div class="form-group">
                            <label class="form-label">📅 Дата</label>
                            <input type="date" class="form-input" name="date" 
                                   value="${new Date().toISOString().split('T')[0]}"
                                   min="${new Date().toISOString().split('T')[0]}"
                                   onchange="app.renderSlots(document.querySelector('[name=trainer_id]')?.value, '${serviceName}', this.value)">
                        </div>

                        <div class="form-group">
                            <label class="form-label">⏰ Оберіть слот</label>
                            <div id="slots-container" class="slots-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 10px;">
                                <!-- Slots rendered dynamically -->
                                <p class="text-muted">Оберіть тренера та дату, щоб побачити доступні слоти</p>
                            </div>
                        </div>

                        <div class="form-group">
                            <label class="form-label">📝 Примітки</label>
                            <textarea class="form-input" name="notes" rows="2"></textarea>
                        </div>

                        <button type="submit" class="btn" id="submit-btn" disabled>✅ Підтвердити</button>
                    </form>
                </div>
            `;

            components.showModal('📅 Бронювання', content);

            // Store bookings globally for slot rendering
            this.currentBookings = bookings;

            // Initial render for Group training (no trainer needed)
            if (isGroup) {
                this.renderSlots(null, serviceName, new Date().toISOString().split('T')[0]);
            }

        } catch (error) {
            components.showToast('Помилка завантаження даних', 'error');
            console.error(error);
        }
    },

    renderSlots(trainerId, serviceName, date) {
        const container = document.getElementById('slots-container');
        const submitBtn = document.getElementById('submit-btn');
        const isGroup = serviceName.includes('Групове');

        if (!isGroup && !trainerId) {
            container.innerHTML = '<p class="text-muted">Спочатку оберіть тренера</p>';
            return;
        }

        let slotsHtml = '';
        const startHour = 8;
        const endHour = 20; // Last booking starts at 20:00

        for (let h = startHour; h <= endHour; h++) {
            const timeStr = `${h.toString().padStart(2, '0')}:00`;
            const slotEndStr = `${(h + 1).toString().padStart(2, '0')}:00`;

            let isAvailable = true;
            let cssClass = 'btn-outline';

            // Rule: Group vs Personal Hours
            if (isGroup) {
                if (h !== 10 && h !== 11) isAvailable = false; // Only 10-12
            } else {
                if (h === 10 || h === 11) isAvailable = false; // Reserved for Group
            }

            // Rule: Conflict Check (Personal only)
            if (isAvailable && !isGroup && trainerId) {
                // Re-implementing check properly
                const trainerSelect = document.querySelector('[name=trainer_id]');
                const selectedTrainerName = trainerSelect ? trainerSelect.options[trainerSelect.selectedIndex].text.split(' (')[0] : '';

                // Check if slot matches time AND trainer name (partial match on Last Name to catch collisions)
                const collision = this.currentBookings.find(b =>
                    b.date === date &&
                    b.trainer_name &&
                    b.trainer_name.includes(selectedTrainerName.split(' ')[1]) &&
                    b.status !== 'cancelled' &&
                    (b.time === timeStr || b.time.startsWith(timeStr))
                );

                if (collision) {
                    isAvailable = false;
                    cssClass = 'btn-secondary'; // Visually disabled
                }
            }

            if (isAvailable) {
                slotsHtml += `
                    <button type="button" class="btn ${cssClass}" 
                        onclick="app.selectSlot(this, '${timeStr}')"
                        style="width: 100%; margin: 0;">
                        ${timeStr} - ${slotEndStr}
                    </button>`;
            } else {
                slotsHtml += `
                    <button type="button" class="btn btn-secondary" disabled 
                        style="width: 100%; margin: 0; opacity: 0.5;">
                        ${timeStr} - ${slotEndStr}
                    </button>`;
            }
        }

        container.innerHTML = slotsHtml;
    },

    selectSlot(btn, time) {
        // Visual selection
        document.querySelectorAll('#slots-container .btn').forEach(b => {
            if (!b.disabled) b.className = 'btn btn-outline';
        });
        btn.className = 'btn btn-primary'; // Highlight selected

        // save value
        document.getElementById('selected-time').value = time;
        document.getElementById('submit-btn').removeAttribute('disabled');
    },

    async submitBooking(serviceName) {
        const form = document.getElementById('booking-form');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const formData = new FormData(form);
        const data = {
            service_name: serviceName,
            trainer_id: formData.get('trainer_id'),
            date: formData.get('date'),
            time: formData.get('time'),
            notes: formData.get('notes')
        };

        try {
            const booking = await api.createBooking(data);
            components.showToast(`Бронювання ${booking.booking_number} створено!`, 'success');
            components.closeModal();

            // Redirect to bookings if admin
            if (this.currentUser && this.currentUser.role === 'admin') {
                window.location.hash = '#bookings';
            }
        } catch (error) {
            components.showToast(error.message || 'Помилка створення бронювання', 'error');
        }
    },

    // Authentication
    showLogin() {
        const content = `
            <div style="max-width: 400px;">
                <form onsubmit="app.handleLogin(event)">
                    <div class="form-group">
                        <label class="form-label">Email</label>
                        <input type="email" class="form-input" name="email" required value="admin@sportcomplex.com">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Пароль</label>
                        <input type="password" class="form-input" name="password" required value="admin123">
                    </div>
                    <button type="submit" class="btn">Увійти</button>
                </form>
                <hr style="margin: 2rem 0;">
                <p style="text-align: center;">Немає акаунту?</p>
                <button class="btn btn-secondary" onclick="app.showRegister()" style="width: 100%;">
                    Зареєструватися
                </button>
                <p style="text-align: center; color: var(--text-muted); font-size: 0.875rem; margin-top: 1rem;">
                    Demo: admin@sportcomplex.com / admin123
                </p>
            </div>
        `;

        components.showModal('🔐 Вхід у систему', content);
    },

    showRegister() {
        const content = `
            <div style="max-width: 400px;">
                <form onsubmit="app.handleRegister(event)">
                    <div class="form-group">
                        <label class="form-label">Email</label>
                        <input type="email" class="form-input" name="email" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Пароль</label>
                        <input type="password" class="form-input" name="password" required>
                    </div>
                    <button type="submit" class="btn">Зареєструватися</button>
                </form>
                <hr style="margin: 2rem 0;">
                <p style="text-align: center;">Вже є акаунт?</p>
                <button class="btn btn-secondary" onclick="app.showLogin()" style="width: 100%;">
                    Увійти
                </button>
            </div>
        `;

        components.showModal('📝 Реєстрація', content);
    },

    async handleLogin(event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        const data = {
            email: formData.get('email'),
            password: formData.get('password')
        };

        try {
            const response = await api.login(data);

            if (response.detail) {
                components.showToast('Невірний email або пароль', 'error');
                return;
            }

            localStorage.setItem('auth_token', response.access_token);
            localStorage.setItem('user_data', JSON.stringify(response.user));

            this.currentUser = response.user;
            this.updateAuthUI();

            components.showToast(`Ласкаво просимо, ${response.user.name}!`, 'success');
            components.closeModal();
        } catch (error) {
            components.showToast('Помилка входу', 'error');
        }
    },

    async handleRegister(event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        const data = {
            email: formData.get('email'),
            password: formData.get('password')
        };

        try {
            const response = await api.register(data);

            if (response.detail) {
                components.showToast(response.detail, 'error');
                return;
            }

            localStorage.setItem('auth_token', response.access_token);
            localStorage.setItem('user_data', JSON.stringify(response.user));

            this.currentUser = response.user;
            this.updateAuthUI();

            components.showToast(`Вітаємо, ${response.user.name}!`, 'success');
            components.closeModal();
        } catch (error) {
            components.showToast('Помилка реєстрації', 'error');
        }
    },

    logout() {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
        this.currentUser = null;
        this.updateAuthUI();
        components.showToast('Ви вийшли з системи', 'success');
    },

    render404() {
        document.getElementById('app').innerHTML = `
            <div class="container">
                ${components.showEmptyState('Сторінку не знайдено', '🔍')}
            </div>
        `;
    },

    // Helper methods
    getProductIcon(category) {
        const icons = {
            'supplements': '💊',
            'equipment': '🏋️',
            'apparel': '👕',
            'accessories': '🎒'
        };
        return icons[category] || '📦';
    },

    getServiceIcon(type) {
        const icons = {
            'training': '🏋️',
            'pool': '🏊',
            'massage': '💆',
            'consultation': '👨‍⚕️'
        };
        return icons[type] || '🎯';
    },

    getTrainerIcon(specialization) {
        const icons = {
            'fitness': '🏃',
            'gym': '🏋️',
            'pool': '🏊',
            'massage': '💆'
        };
        return icons[specialization] || '👤';
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});

// Export for global access
window.app = app;
