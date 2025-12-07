// ==========================================
// Global State
// ==========================================

let currentUserRole = 'user';  // 'user' or 'admin'

// ==========================================
// UTILITY FUNCTIONS
// ==========================================

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isValidPhone(phone) {
    return /^[\d\s+\-()]{10,}$/.test(phone);
}

function getFormValue(elementId) {
    const element = document.getElementById(elementId);
    return element ? element.value.trim() : '';
}

function setFormValue(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) element.value = value || '';
}

function formatPrice(price) {
    return new Intl.NumberFormat('uk-UA', { style: 'currency', currency: 'UAH' }).format(price || 0);
}

function showNotification(message, type = 'info') {
    let container = document.getElementById('notificationContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notificationContainer';
        container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; max-width: 420px;';
        document.body.appendChild(container);
    }

    const notification = document.createElement('div');
    notification.style.cssText = `
        padding: 1rem;
        margin-bottom: 10px;
        border-radius: 5px;
        font-weight: 500;
        animation: slideIn 0.3s ease-in-out;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    `;

    const colors = {
        success: { bg: '#d5f4e6', text: '#27ae60', border: '#27ae60' },
        danger: { bg: '#fadbd8', text: '#c0392b', border: '#c0392b' },
        warning: { bg: '#fdeaa8', text: '#d68910', border: '#d68910' },
        info: { bg: '#d6eaf8', text: '#2874a6', border: '#2874a6' }
    };

    const color = colors[type] || colors.info;
    notification.style.backgroundColor = color.bg;
    notification.style.color = color.text;
    notification.style.borderLeft = `4px solid ${color.border}`;
    notification.textContent = message;

    container.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in-out';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// ==========================================
// USER SERVICES & BOOKINGS
// ==========================================

function loadUserServices() {
    try {
        const servicesGrid = document.getElementById('userServicesGrid');
        if (!servicesGrid) return;

        API.services.list()
            .then(services => {
                const list = services || [];
                if (!list.length) {
                    servicesGrid.innerHTML = '<p style="color: #7f8c8d; text-align: center;">Послуги тимчасово недоступні</p>';
                    return;
                }

                servicesGrid.innerHTML = list.map(service => `
                    <div class="service-card">
                        <h3>${service.service_name}</h3>
                        <p style="color: #7f8c8d; margin: 0.5rem 0;">⏱️ 60 хвилин</p>
                        <p style="color: #27ae60; font-weight: bold; font-size: 1.2rem; margin: 1rem 0;">₴${service.price}</p>
                        <p style="color: #7f8c8d; font-size: 0.9rem;">${service.requires_medical_certificate ? 'Потрібна медична довідка' : 'Без довідки'}</p>
                        <button class="btn-success" style="width: 100%; margin-top: 1rem;" onclick="bookService(${service.service_id}, '${service.service_name}', ${service.price})">📅 Забронювати</button>
                    </div>
                `).join('');

                // Extra curated examples
                servicesGrid.innerHTML += `
                    <div class="service-card" style="background:#f9f9f9;">
                        <h3>CrossFit інтенсив</h3>
                        <p style="color: #7f8c8d; margin: 0.5rem 0;">⏱️ 50 хвилин</p>
                        <p style="color: #27ae60; font-weight: bold; font-size: 1.2rem; margin: 1rem 0;">₴220</p>
                        <p style="color: #7f8c8d; font-size: 0.9rem;">Високоінтенсивні комплекси з тренером</p>
                        <button class="btn-success" style="width: 100%; margin-top: 1rem;" onclick="bookService(8, 'CrossFit інтенсив', 220)">📅 Забронювати</button>
                    </div>
                    <div class="service-card" style="background:#f9f9f9;">
                        <h3>Пілатес для спини</h3>
                        <p style="color: #7f8c8d; margin: 0.5rem 0;">⏱️ 45 хвилин</p>
                        <p style="color: #27ae60; font-weight: bold; font-size: 1.2rem; margin: 1rem 0;">₴140</p>
                        <p style="color: #7f8c8d; font-size: 0.9rem;">Мʼяка стабілізація та мобільність</p>
                        <button class="btn-success" style="width: 100%; margin-top: 1rem;" onclick="bookService(9, 'Пілатес для спини', 140)">📅 Забронювати</button>
                    </div>
                `;

                showNotification('🎯 Послуги завантажені', 'info');
            })
            .catch(err => {
                console.error('Помилка завантаження послуг:', err);
                servicesGrid.innerHTML = '<p style="color: #e74c3c; text-align: center;">Не вдалось завантажити послуги</p>';
                showNotification('❌ Помилка завантаження послуг', 'error');
            });
    } catch (error) {
        console.error('Помилка завантаження послуг:', error);
    }
}

function bookService(serviceId, serviceName, price) {
    const bookingDate = prompt(`Забронювати "${serviceName}" (₴${price})?\n\nОберіть дату (YYYY-MM-DD):`);
    if (!bookingDate) return;

    API.bookings.create({ service_id: serviceId, booking_date: bookingDate })
        .then(() => {
            showNotification(`✅ Ви забронювали "${serviceName}" на ${bookingDate}`, 'success');
            loadUserBookings();
        })
        .catch(err => {
            console.error('Не вдалося створити бронювання', err);
            showNotification('❌ Не вдалося створити бронювання', 'error');
        });
}

// ==========================================
// Page Navigation & Management
// ==========================================

function switchPage(pageName) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.style.display = 'none';
    });

    // Deactivate all nav buttons
    document.querySelectorAll('nav button').forEach(btn => {
        btn.classList.remove('active');
    });

    // Prevent non-admin users from accessing database queries
    if (pageName === 'dbqueries' && currentUserRole !== 'admin') {
        showNotification('❌ Доступ заборонено. Тільки адміністратори можуть переглядати запити БД', 'danger');
        return;
    }
    
    // Determine if it's user or admin page
    let pageId = pageName + 'Page';

    if (pageName === 'home') {
        // Show role-specific home page
        pageId = currentUserRole === 'admin' ? 'homePageAdmin' : 'homePageUser';
    } else if (currentUserRole === 'user') {
        // Map user pages to actual ids
        const userPageMap = {
            services: 'servicesPageUser',
            myBookings: 'myBookingsPage',
            profile: 'profilePage',
        };
        pageId = userPageMap[pageName] || pageName + 'PageUser';
    } else if (currentUserRole === 'admin') {
        // Admin pages have different naming
        if (['clients', 'trainers', 'services', 'memberships', 'analytics'].includes(pageName)) {
            pageId = pageName + 'Page';
        } else if (pageName === 'statistics') {
            pageId = 'statisticsPage';
        } else if (pageName === 'inventory') {
            pageId = 'inventoryPage';
        } else if (pageName === 'dbqueries') {
            pageId = 'dbqueriesPage';
        }
    }

    // Show selected page
    const selectedPage = document.getElementById(pageId);
    if (selectedPage) {
        selectedPage.style.display = 'block';
    }

    // Activate corresponding nav button
    const navBtn = document.querySelector(`[data-page="${pageName}"]`);
    if (navBtn) {
        navBtn.classList.add('active');
    }

    // Load page-specific data
    loadPageData(pageName);
}

function loadPageData(pageName) {
    switch (pageName) {
        // USER pages
        case 'myBookings':
            loadUserBookings();
            break;
        case 'profile':
            loadUserProfile();
            break;
        case 'services':
            if (currentUserRole === 'admin') {
                loadAdminServices();
            } else {
                loadUserServices();
            }
            break;
        // ADMIN pages
        case 'statistics':
            loadAdminStatistics();
            break;
        case 'inventory':
            loadInventory();
            break;
        case 'clients':
            if (currentUserRole === 'admin') loadClients();
            break;
        case 'trainers':
            loadTrainers();
            break;
        case 'memberships':
            loadMemberships();
            break;
        case 'analytics':
            loadAnalytics();
            break;
        case 'dbqueries':
            loadDBQueries();
            break;
    }
}

// ==========================================
// Initialize on page load
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    // Update navigation based on user role
    updateNavigationForRole();
    switchPage('home');
});

function updateNavigationForRole() {
    const userRole = localStorage.getItem('authRole') || 'user';
    currentUserRole = userRole;

    const userNav = document.getElementById('userNav');
    const adminNav = document.getElementById('adminNav');

    if (userRole === 'admin') {
        userNav.style.display = 'none';
        adminNav.style.display = 'block';
    } else {
        userNav.style.display = 'block';
        adminNav.style.display = 'none';
    }
    
    // Hide database queries button for non-admin users (security measure)
    const dbQueriesBtn = document.querySelector('[data-page="dbqueries"]');
    if (dbQueriesBtn) {
        if (userRole === 'admin') {
            dbQueriesBtn.style.display = 'inline-block';
        } else {
            dbQueriesBtn.style.display = 'none';
        }
    }
}

function loadUserBookings() {
    try {
        const bookingsTable = document.getElementById('userBookingsTable');
        if (!bookingsTable) return;
        
        // Fetch bookings from API
        API.bookings.list()
            .then(response => {
                const bookings = (response && response.bookings) || [];
                
                if (bookings.length === 0) {
                    bookingsTable.innerHTML = `
                        <tr>
                            <td colspan="5" style="text-align: center; padding: 2rem; color: #7f8c8d;">
                                Немає активних бронювань. <a href="#" onclick="switchPage('services'); return false;" style="color: var(--primary-color); cursor: pointer;">Забронюйте послугу →</a>
                            </td>
                        </tr>
                    `;
                } else {
                    bookingsTable.innerHTML = bookings.map(booking => `
                        <tr>
                            <td>${booking.service_name || 'N/A'}</td>
                            <td>${booking.booking_date || 'N/A'}</td>
                            <td>${booking.trainer_name || '-'}</td>
                            <td><span class="badge badge-success">✓ ${booking.status || 'Підтверджено'}</span></td>
                            <td><button class="btn-sm btn-danger" onclick="cancelBooking(${booking.booking_id || 0})">Скасувати</button></td>
                        </tr>
                    `).join('');
                }
                showNotification('🎫 Бронювання завантажені', 'info');
            })
            .catch(error => {
                console.error('Помилка завантаження бронювань:', error);
                bookingsTable.innerHTML = `
                    <tr>
                        <td colspan="5" style="text-align: center; padding: 2rem; color: #e74c3c;">
                            Помилка завантаження. Спробуйте пізніше.
                        </td>
                    </tr>
                `;
                showNotification('❌ Помилка завантаження бронювань', 'error');
            });
    } catch (error) {
        console.error('Помилка завантаження бронювань:', error);
    }
}

function cancelBooking(serviceId) {
    const bookingId = serviceId;
    if (!bookingId) {
        showNotification('❌ Некоректне бронювання', 'error');
        return;
    }

    if (!confirm('Скасувати бронювання?')) return;

    API.bookings.delete(bookingId)
        .then(() => {
            showNotification('Бронювання скасовано', 'info');
            loadUserBookings();
        })
        .catch(err => {
            console.error('Помилка скасування бронювання:', err);
            showNotification('❌ Не вдалося скасувати бронювання', 'error');
        });
}

function loadUserProfile() {
    try {
        const username = localStorage.getItem('authUsername') || 'користувач';
        const userProfileUsername = document.getElementById('profileUsername');
        const emailInput = document.getElementById('profileEmail');
        const phoneInput = document.getElementById('profilePhone');

        if (userProfileUsername) userProfileUsername.textContent = username;

        const statusEl = document.getElementById('profileMembershipStatus');
        const typeEl = document.getElementById('profileMembershipType');
        const daysEl = document.getElementById('profileDaysLeft');
        const priceEl = document.getElementById('profileMembershipPrice');

        const profilePromise = API.userProfile.get()
            .then(data => {
                const contact = data?.contact_info || {};
                if (userProfileUsername && data?.username) {
                    userProfileUsername.textContent = data.username;
                }
                if (emailInput) emailInput.value = contact.email || '';
                if (phoneInput) phoneInput.value = contact.phone || '';
            })
            .catch(err => {
                console.error('Помилка завантаження профіля користувача:', err);
            });

        const membershipPromise = API.userMembership()
            .then(resp => {
                const m = resp && resp.membership;
                if (!m) {
                    if (statusEl) {
                        statusEl.textContent = 'Немає активного абонемента';
                        statusEl.style.color = '#7f8c8d';
                    }
                    if (typeEl) typeEl.textContent = '-';
                    if (priceEl) priceEl.textContent = '-';
                    if (daysEl) daysEl.textContent = '-';
                    return;
                }

                const statusText = m.status || 'невідомо';
                if (statusEl) {
                    statusEl.textContent = statusText;
                    statusEl.style.color = statusText === 'active' ? '#27ae60' : '#c0392b';
                }
                if (typeEl) typeEl.textContent = m.subscription_type || '-';
                if (priceEl) priceEl.textContent = typeof m.price === 'number' ? `${m.price} грн` : (m.price || '-');
                if (daysEl) {
                    const days = typeof m.days_left === 'number' ? m.days_left : null;
                    daysEl.textContent = days !== null ? `${days} днів` : '-';
                    daysEl.style.color = days !== null && days >= 0 ? '#27ae60' : '#c0392b';
                }
            })
            .catch(err => {
                console.error('Помилка завантаження абонемента:', err);
                if (statusEl) {
                    statusEl.textContent = 'Помилка завантаження';
                    statusEl.style.color = '#c0392b';
                }
            });

        Promise.all([profilePromise, membershipPromise]).finally(() => {
            showNotification('👤 Профіль завантажений', 'info');
        });
    } catch (error) {
        console.error('Помилка завантаження профіля:', error);
    }
}

function updateUserProfile() {
    const email = document.getElementById('profileEmail').value.trim();
    const phone = document.getElementById('profilePhone').value.trim();

    const payload = {};
    if (email) payload.email = email;
    if (phone) payload.phone = phone;

    if (!payload.email && !payload.phone) {
        showNotification('⚠️ Заповніть хоча б одне поле', 'warning');
        return;
    }

    API.userProfile.update(payload)
        .then(() => {
            showNotification('✅ Профіль оновлено успішно', 'success');
        })
        .catch(err => {
            console.error('Помилка оновлення профіля:', err);
            showNotification('❌ Не вдалося оновити профіль', 'error');
        });
}

// ==========================================
// ADMIN PAGES
// ==========================================

function loadAdminStatistics() {
    try {
        showNotification('📊 Статистика завантажена', 'info');
    } catch (error) {
        console.error('Помилка завантаження статистики:', error);
    }
}

async function loadInventory() {
    try {
        const response = await API.products.list();
        const inventoryTable = document.getElementById('inventoryTable');
        inventoryTable.innerHTML = '';

        // Handle both paginated and legacy response formats
        const products = Array.isArray(response) ? response : (response.items || []);

        if (products.length === 0) {
            inventoryTable.innerHTML = '<tr><td colspan="7" style="text-align:center; padding: 2rem;">Немає товарів</td></tr>';
            return;
        }

        products.forEach(product => {
            const status = product.quantity > (product.min_stock || 10) ? 'badge-success' : 'badge-warning';
            const statusText = product.quantity > (product.min_stock || 10) ? '✓ В наявності' : '⚠ Мало';
            const row = `
                <tr>
                    <td>${product.article || '-'}</td>
                    <td>${product.name || '-'}</td>
                    <td>${product.category || '-'}</td>
                    <td>₴${(product.price_uah || 0).toFixed(0)}</td>
                    <td>${product.quantity || 0}</td>
                    <td><span class="badge ${status}">${statusText}</span></td>
                    <td>
                        <button class="btn-sm btn-primary" onclick="editProduct('${product.article}')">Редаг.</button>
                        <button class="btn-sm btn-danger" onclick="deleteProduct('${product.article}')">Видал.</button>
                    </td>
                </tr>
            `;
            inventoryTable.innerHTML += row;
        });

        // Show pagination info if available
        if (response.total !== undefined) {
            console.log(`Loaded ${products.length} of ${response.total} products (page ${response.page}/${response.total_pages})`);
        }
    } catch (error) {
        console.error('[LoadInventory] Error:', error);
        showNotification('Помилка завантаження товарів: ' + error.message, 'danger');
    }
}

function showInventoryForm() {
    const form = document.getElementById('inventoryForm');
    if (form) {
        if (form.style.display === 'none') {
            form.style.display = 'block';
            loadCategoriesAndSuppliers();
        } else {
            form.style.display = 'none';
        }
    }
}

async function loadCategoriesAndSuppliers() {
    try {
        const [categories, suppliers] = await Promise.all([
            API.categories.list(),
            API.suppliers.list()
        ]);

        // Populate add form
        const categorySelect = document.getElementById('productCategory');
        const supplierSelect = document.getElementById('productSupplier');
        
        categorySelect.innerHTML = '<option value="">Оберіть категорію</option>' +
            categories.map(c => `<option value="${c.name}">${c.name}</option>`).join('');
        
        supplierSelect.innerHTML = '<option value="">Оберіть постачальника</option>' +
            suppliers.map(s => `<option value="${s.name}">${s.name}</option>`).join('');

        // Populate edit form
        const editCategorySelect = document.getElementById('editProductCategory');
        const editSupplierSelect = document.getElementById('editProductSupplier');
        
        editCategorySelect.innerHTML = '<option value="">Оберіть категорію</option>' +
            categories.map(c => `<option value="${c.name}">${c.name}</option>`).join('');
        
        editSupplierSelect.innerHTML = '<option value="">Оберіть постачальника</option>' +
            suppliers.map(s => `<option value="${s.name}">${s.name}</option>`).join('');

    } catch (error) {
        console.error('[LoadCategoriesAndSuppliers] Error:', error);
        showNotification('Помилка завантаження категорій/постачальників', 'danger');
    }
}

async function addProduct() {
    const article = document.getElementById('productArticle').value.trim();
    const name = document.getElementById('productName').value.trim();
    const category = document.getElementById('productCategory').value;
    const price = parseFloat(document.getElementById('productPrice').value);
    const quantity = parseInt(document.getElementById('productQuantity').value);
    const supplier = document.getElementById('productSupplier').value;

    if (!article || !name || !category || !supplier || isNaN(price) || isNaN(quantity)) {
        showNotification('⚠️ Заповніть обов\'язкові поля', 'warning');
        return;
    }

    if (price <= 0 || quantity < 0) {
        showNotification('⚠️ Ціна повинна бути додатною', 'warning');
        return;
    }

    try {
        const payload = {
            article: article,
            name: name,
            category_name: category,
            supplier_name: supplier,
            price: price,
            quantity: quantity,
            min_stock: 10,
            delivery_days: 7
        };

        await API.products.create(payload);
        showNotification('✅ Товар доданий успішно', 'success');
        document.getElementById('inventoryForm').style.display = 'none';
        document.querySelectorAll('#inventoryForm input, #inventoryForm select').forEach(el => el.value = '');
        loadInventory();
    } catch (error) {
        console.error('[AddProduct] Error:', error);
        showNotification('Помилка додавання: ' + error.message, 'danger');
    }
}

let currentEditProductArticle = null;

async function editProduct(article) {
    try {
        const product = await API.products.byArticle(article);
        
        // Load categories and suppliers first
        await loadCategoriesAndSuppliers();
        
        document.getElementById('editProductArticle').value = product.article;
        document.getElementById('editProductName').value = product.name;
        document.getElementById('editProductCategory').value = product.category || '';
        document.getElementById('editProductPrice').value = product.price_uah || 0;
        document.getElementById('editProductQuantity').value = product.quantity || 0;
        document.getElementById('editProductSupplier').value = product.supplier || '';
        
        currentEditProductArticle = article;
        document.getElementById('editProductModal').style.display = 'flex';
    } catch (error) {
        console.error('[EditProduct] Error:', error);
        showNotification('Помилка завантаження товару: ' + error.message, 'danger');
    }
}

function closeEditProductModal() {
    document.getElementById('editProductModal').style.display = 'none';
    currentEditProductArticle = null;
}

async function updateProduct() {
    if (!currentEditProductArticle) {
        showNotification('Помилка: товар не вибран', 'danger');
        return;
    }

    const name = document.getElementById('editProductName').value.trim();
    const category = document.getElementById('editProductCategory').value;
    const price = parseFloat(document.getElementById('editProductPrice').value);
    const quantity = parseInt(document.getElementById('editProductQuantity').value);
    const supplier = document.getElementById('editProductSupplier').value;

    if (!name || !category || !supplier || isNaN(price) || isNaN(quantity)) {
        showNotification('⚠️ Заповніть обов\'язкові поля', 'warning');
        return;
    }

    if (price <= 0 || quantity < 0) {
        showNotification('⚠️ Ціна повинна бути додатною', 'warning');
        return;
    }

    try {
        const payload = {
            article: document.getElementById('editProductArticle').value,
            name: name,
            category_name: category,
            supplier_name: supplier,
            price: price,
            quantity: quantity,
            min_stock: 10,
            delivery_days: 7
        };

        await API.products.update(currentEditProductArticle, payload);
        showNotification('✓ Товар оновлено', 'success');
        closeEditProductModal();
        loadInventory();
    } catch (error) {
        console.error('[UpdateProduct] Error:', error);
        showNotification('Помилка оновлення: ' + error.message, 'danger');
    }
}

async function deleteProduct(article) {
    if (!confirm('Видалити цей товар?')) return;
    try {
        await API.products.delete(article);
        showNotification('✓ Товар видалено успішно', 'success');
        loadInventory();
    } catch (error) {
        console.error('[DeleteProduct] Error:', error);
        showNotification('Помилка видалення: ' + error.message, 'danger');
    }
}

function loadAdminServices() {
    try {
        loadServices();
    } catch (error) {
        console.error('Помилка завантаження послуг:', error);
    }
}

// ==========================================
// SHARED PAGES (User & Admin)
// ==========================================

async function loadClients() {
    try {
        const response = await API.clients.list();
        const clientsTable = document.getElementById('clientsTable');
        clientsTable.innerHTML = '';

        // Handle both paginated and legacy response formats
        const clients = Array.isArray(response) ? response : (response.items || []);

        if (clients.length === 0) {
            clientsTable.innerHTML = '<tr><td colspan="5" style="text-align:center; padding: 2rem;">Немає клієнтів</td></tr>';
            return;
        }

        clients.forEach(client => {
            const contact = client.contact_info || {};
            const row = `
                <tr>
                    <td>${client.full_name}</td>
                    <td>${formatDate(client.birth_date)}</td>
                    <td>${contact.phone || '-'}</td>
                    <td>${contact.email || '-'}</td>
                    <td>
                        <button class="btn-sm btn-primary" onclick="editClient('${client.client_id || ''}')">Редагувати</button>
                        <button class="btn-sm btn-danger" onclick="if(confirm('Видалити клієнта?')) deleteClientDirect('${client.client_id || ''}')">Видалити</button>
                    </td>
                </tr>
            `;
            clientsTable.innerHTML += row;
        });

        // Show pagination info if available
        if (response.total !== undefined) {
            console.log(`Loaded ${clients.length} of ${response.total} clients (page ${response.page}/${response.total_pages})`);
        }
    } catch (error) {
        showNotification('Помилка завантаження клієнтів: ' + error.message, 'danger');
    }
}

async function createClient() {
    const fullName = document.getElementById('clientName').value;
    const birthDate = document.getElementById('clientBirthDate').value;
    const phone = document.getElementById('clientPhone').value;
    const email = document.getElementById('clientEmail').value;
    const username = document.getElementById('clientUsername').value;
    const password = document.getElementById('clientPassword').value;

    console.log('[CreateClient] Form values:', { fullName, birthDate, phone, email, username });

    if (!fullName || !birthDate || !username || !password) {
        showNotification('Заповніть обов\'язкові поля (ПІБ, дата, ім\'я користувача, пароль)', 'warning');
        return;
    }

    if (username.length < 3) {
        showNotification('Ім\'я користувача повинно мати мінімум 3 символи', 'warning');
        return;
    }

    if (password.length < 6) {
        showNotification('Пароль повинен мати мінімум 6 символів', 'warning');
        return;
    }

    try {
        // Build contact_info object - only include non-empty values
        const contact_info = {};
        if (phone && phone.trim()) contact_info.phone = phone.trim();
        if (email && email.trim()) contact_info.email = email.trim();
        
        const payload = {
            full_name: fullName,
            birth_date: birthDate,
            gender: 'MALE',
            contact_info: Object.keys(contact_info).length > 0 ? contact_info : null,
            username: username,
            password: password
        };

        console.log('[CreateClient] Sending payload:', payload);
        
        await API.clients.create(payload);
        showNotification('Клієнт та облік користувача створені успішно', 'success');
        document.getElementById('clientForm').reset();
        document.getElementById('clientForm').style.display = 'none';
        loadClients();
    } catch (error) {
        console.error('[CreateClient] Error:', error);
        showNotification('Помилка: ' + error.message, 'danger');
    }
}

// Current client being edited
let currentEditClientId = null;

async function editClient(clientId) {
    try {
        console.log('[EditClient] Loading client:', clientId);
        const client = await API.clients.get(clientId);
        
        // Populate form
        document.getElementById('editClientName').value = client.full_name;
        document.getElementById('editClientBirthDate').value = client.birth_date;
        document.getElementById('editClientPhone').value = client.contact_info?.phone || '';
        document.getElementById('editClientEmail').value = client.contact_info?.email || '';
        document.getElementById('editClientUsername').value = client.username || '';
        document.getElementById('editClientPassword').value = '';
        document.getElementById('editClientGender').value = client.gender || 'MALE';
        
        currentEditClientId = clientId;
        
        // Show modal
        const modal = document.getElementById('editClientModal');
        modal.style.display = 'flex';
    } catch (error) {
        console.error('[EditClient] Error:', error);
        showNotification('Помилка завантаження клієнта: ' + error.message, 'danger');
    }
}

function closeEditModal() {
    document.getElementById('editClientModal').style.display = 'none';
    document.getElementById('editClientForm').reset();
    currentEditClientId = null;
}

async function updateClient() {
    if (!currentEditClientId) {
        showNotification('Помилка: клієнт не вибран', 'danger');
        return;
    }

    const fullName = document.getElementById('editClientName').value;
    const birthDate = document.getElementById('editClientBirthDate').value;
    const phone = document.getElementById('editClientPhone').value;
    const email = document.getElementById('editClientEmail').value;
    const username = document.getElementById('editClientUsername').value;
    const password = document.getElementById('editClientPassword').value;
    const gender = document.getElementById('editClientGender').value;

    if (!fullName || !birthDate || !username) {
        showNotification('Заповніть обов\'язкові поля (ПІБ, дата, ім\'я користувача)', 'warning');
        return;
    }

    if (password && password.length < 6) {
        showNotification('Пароль повинен мати мінімум 6 символів', 'warning');
        return;
    }

    try {
        const contact_info = {};
        if (phone) contact_info.phone = phone;
        if (email) contact_info.email = email;

        const payload = {
            full_name: fullName,
            birth_date: birthDate,
            gender: gender,
            contact_info: Object.keys(contact_info).length > 0 ? contact_info : null,
            username: username,
            password: password || undefined
        };

        console.log('[UpdateClient] Sending payload:', payload);
        await API.clients.update(currentEditClientId, payload);
        
        showNotification('Клієнт успішно оновлений', 'success');
        closeEditModal();
        loadClients();
    } catch (error) {
        console.error('[UpdateClient] Error:', error);
        showNotification('Помилка оновлення: ' + error.message, 'danger');
    }
}

async function confirmDeleteClient() {
    if (!currentEditClientId) {
        showNotification('Помилка: клієнт не вибран', 'danger');
        return;
    }

    const clientName = document.getElementById('editClientName').value;
    
    if (confirm(`Ви впевнені, що бажаєте видалити клієнта "${clientName}"?\n\nЦю дію неможливо скасувати!`)) {
        await deleteClient();
    }
}

async function deleteClient() {
    if (!currentEditClientId) {
        showNotification('Помилка: клієнт не вибран', 'danger');
        return;
    }

    try {
        console.log('[DeleteClient] Deleting client:', currentEditClientId);
        await API.clients.delete(currentEditClientId);
        
        showNotification('Клієнт успішно видалений', 'success');
        closeEditModal();
        loadClients();
    } catch (error) {
        console.error('[DeleteClient] Error:', error);
        showNotification('Помилка видалення: ' + error.message, 'danger');
    }
}

async function deleteClientDirect(clientId) {
    try {
        console.log('[DeleteClient] Deleting client:', clientId);
        await API.clients.delete(clientId);
        
        showNotification('Клієнт успішно видалений', 'success');
        loadClients();
    } catch (error) {
        console.error('[DeleteClient] Error:', error);
        showNotification('Помилка видалення: ' + error.message, 'danger');
    }
}

// ==========================================
// SPORT TRAINERS
// ==========================================

async function loadTrainers() {
    try {
        const data = await API.trainers.list();
        const trainersTable = document.getElementById('trainersTable');

        if (!data || data.length === 0) {
            trainersTable.innerHTML = '<tr><td colspan="5" style="text-align:center; padding: 2rem;">Немає тренерів</td></tr>';
            return;
        }

        const rows = data.map(trainer => `
            <tr>
                <td>${trainer.full_name || '-'}</td>
                <td>${trainer.specialization || '-'}</td>
                <td>${trainer.contact_info?.phone || '-'}</td>
                <td>${trainer.contact_info?.email || '-'}</td>
                <td>
                    <button class="btn-sm btn-primary" onclick="editTrainer(${trainer.trainer_id})">Редагувати</button>
                    <button class="btn-sm btn-danger" onclick="deleteTrainer(${trainer.trainer_id})">Видалити</button>
                </td>
            </tr>
        `).join('');
        trainersTable.innerHTML = rows;
    } catch (error) {
        showNotification('Помилка завантаження тренерів: ' + error.message, 'danger');
    }
}

async function createTrainer() {
    const fullName = document.getElementById('trainerName').value.trim();
    const specialization = document.getElementById('trainerSpec').value.trim();
    const phone = document.getElementById('trainerPhone').value.trim();
    const email = document.getElementById('trainerEmail').value.trim();

    if (!fullName || !specialization) {
        showNotification('Заповніть обов\'язкові поля (ПІБ, спеціалізація)', 'warning');
        return;
    }

    if (email && !isValidEmail(email)) {
        showNotification('Невірний формат email', 'warning');
        return;
    }

    try {
        console.log('[CreateTrainer] Creating trainer:', { fullName, specialization });
        const payload = {
            full_name: fullName,
            specialization: specialization,
            birth_date: '1990-01-01',
            gender: 'MALE',
            contact_info: {}
        };
        
        if (phone) payload.contact_info.phone = phone;
        if (email) payload.contact_info.email = email;
        
        await API.trainers.create(payload);
        showNotification('Тренер доданий успішно', 'success');
        document.getElementById('trainerForm').reset();
        loadTrainers();
    } catch (error) {
        console.error('[CreateTrainer] Error:', error);
        showNotification('Помилка: ' + error.message, 'danger');
    }
}

// ==========================================
// SPORT SERVICES
// ==========================================

async function loadServices() {
    try {
        const data = await API.services.list();
        const servicesTable = document.getElementById('servicesTable');
        servicesTable.innerHTML = '';

        if (data.length === 0) {
            servicesTable.innerHTML = '<tr><td colspan="5" style="text-align:center; padding: 2rem;">Немає послуг</td></tr>';
            return;
        }

        data.forEach(service => {
            const row = `
                <tr>
                    <td>${service.service_name}</td>
                    <td>${formatPrice(service.price)}</td>
                    <td>
                        <span class="badge ${service.requires_medical_certificate ? 'badge-warning' : 'badge-success'}">
                            ${service.requires_medical_certificate ? 'Потрібна мед. довідка' : 'Доступна'}
                        </span>
                    </td>
                    <td>
                        <button class="btn-sm btn-primary" onclick="editService(${service.service_id})">Редагувати</button>
                        <button class="btn-sm btn-danger" onclick="deleteService(${service.service_id})">Видалити</button>
                    </td>
                </tr>
            `;
            servicesTable.innerHTML += row;
        });
    } catch (error) {
        showNotification('Помилка завантаження послуг: ' + error.message, 'danger');
    }
}

async function createService() {
    const name = document.getElementById('serviceName').value.trim();
    const price = document.getElementById('servicePrice').value.trim();

    if (!name || !price) {
        showNotification('Заповніть обов\'язкові поля (назва, ціна)', 'warning');
        return;
    }

    if (isNaN(parseFloat(price)) || parseFloat(price) <= 0) {
        showNotification('Ціна повинна бути позитивним числом', 'warning');
        return;
    }

    try {
        console.log('[CreateService] Creating service:', { name, price });
        await API.services.create({
            service_name: name,
            price: parseFloat(price),
            requires_medical_certificate: false
        });
        showNotification('Послуга додана успішно', 'success');
        document.getElementById('serviceForm').reset();
        loadAdminServices();
    } catch (error) {
        console.error('[CreateService] Error:', error);
        showNotification('Помилка: ' + error.message, 'danger');
    }
}

// ==========================================
// MEMBERSHIPS
// ==========================================

// ==========================================
// ANALYTICS
// ==========================================


async function loadAnalytics() {
    try {
        const sportAnalytics = await API.sportAnalytics();
        const reports = await API.sportReports();
        const popularProducts = await API.products.stockExtremes();

        document.getElementById('totalClients').textContent = reports.total_clients ?? 0;
        document.getElementById('activeMembers').textContent = reports.total_revenue ? 'N/A' : 0;
        document.getElementById('totalRevenue').textContent = formatPrice(reports.total_revenue || 0);
        document.getElementById('monthlyRevenue').textContent = formatPrice(sportAnalytics.avg_revenue_per_client || 0);

        // Popular products placeholder
        if (popularProducts) {
            const servicesList = document.getElementById('popularServices');
            servicesList.innerHTML = '';
            ['minimum', 'maximum'].forEach(key => {
                const item = popularProducts[key];
                if (item) {
                    servicesList.innerHTML += `<li>${key.toUpperCase()}: ${item.name} (арт. ${item.article}) — ${item.quantity} шт</li>`;
                }
            });
        }
    } catch (error) {
        showNotification('Помилка завантаження аналітики: ' + error.message, 'danger');
    }
}

// ==========================================
// UTILITY FUNCTIONS
// ==========================================

function freezeMembership(id) {
    showNotification('Заморозка абонемента недоступна в цій версії API', 'warning');
}

function checkOutVisit(id) {
    showNotification('Закриття відвідування недоступне (немає ендпоінта)', 'warning');
}

// ==========================================
// DATABASE QUERIES
// ==========================================

function loadDBQueries() {
    try {
        showNotification('🔍 Запити до баз даних завантажені', 'info');
        // Load default tab data
        loadProductImages();
    } catch (error) {
        console.error('Помилка завантаження запитів БД:', error);
    }
}

// ========== PRODUCT IMAGES TAB ==========
async function loadProductImages() {
    const grid = document.getElementById('productImagesGrid');
    if (!grid) return;
    grid.innerHTML = '<div class="product-image-placeholder">Завантаження зображень...</div>';

    try {
        const response = await API.dbQueries.products();
        let products = [];
        if (Array.isArray(response)) {
            products = response;
        } else if (response.products && Array.isArray(response.products)) {
            products = response.products;
        } else if (response.items && Array.isArray(response.items)) {
            products = response.items;
        }

        grid.innerHTML = '';

        if (!products || products.length === 0) {
            grid.innerHTML = '<div class="product-image-placeholder">Немає товарів для відображення</div>';
            return;
        }

        products.forEach((p) => {
            const card = document.createElement('div');
            card.className = 'product-image-card';

            const thumb = document.createElement('div');
            thumb.className = 'product-image-thumb';
            thumb.textContent = '🖼️';

            const title = document.createElement('p');
            title.style.fontWeight = 'bold';
            title.style.margin = '0.5rem 0 0.2rem 0';
            title.textContent = p.name || '-';

            const subtitle = document.createElement('p');
            subtitle.style.color = '#7f8c8d';
            subtitle.style.fontSize = '0.9rem';
            subtitle.style.margin = '0';
            subtitle.textContent = p.article || '';

            card.appendChild(thumb);
            card.appendChild(title);
            card.appendChild(subtitle);
            grid.appendChild(card);

            // Fetch image per product; fallback to emoji if missing
            API.products.getImage(p.article)
                .then((imgData) => {
                    if (imgData && imgData.image_base64) {
                        const mime = imgData.mime_type || 'image/jpeg';
                        thumb.style.backgroundImage = `url(data:${mime};base64,${imgData.image_base64})`;
                        thumb.textContent = '';
                    } else {
                        thumb.textContent = '🚫';
                        thumb.title = 'Зображення відсутнє';
                    }
                })
                .catch(() => {
                    thumb.textContent = '🚫';
                    thumb.title = 'Зображення відсутнє';
                });
        });
    } catch (error) {
        console.error('[LoadProductImages] Error:', error);
        grid.innerHTML = `<div class="product-image-placeholder" style="color:red;">Помилка завантаження: ${error.message || error}</div>`;
    }
}

async function uploadProductImage(event) {
    event.preventDefault();

    if (currentUserRole !== 'admin') {
        showNotification('❌ Завантаження доступне лише адміністратору', 'danger');
        return false;
    }

    const articleInput = document.getElementById('productImageArticle');
    const fileInput = document.getElementById('productImageFile');
    const submitBtn = event?.target?.querySelector('button[type="submit"]');

    const article = articleInput?.value?.trim();
    const file = fileInput?.files?.[0];

    if (!article || !file) {
        showNotification('⚠️ Вкажіть артикул і виберіть файл', 'warning');
        return false;
    }

    if (file.size > 2 * 1024 * 1024) {
        showNotification('⚠️ Файл завеликий. Спробуйте до 2 МБ', 'warning');
        return false;
    }

    const mime = file.type || 'image/jpeg';

    try {
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Завантаження...';
        }

        const base64 = await fileToBase64(file);
        await API.products.uploadImage(article, base64, mime);

        showNotification('✓ Зображення завантажено', 'success');
        document.getElementById('productImageUploadForm')?.reset();
        loadProductImages();
    } catch (error) {
        console.error('[UploadProductImage] Error:', error);
        showNotification('❌ Не вдалося завантажити: ' + (error.message || error), 'danger');
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = '⬆️ Завантажити';
        }
    }

    return false;
}

function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            try {
                const result = reader.result || '';
                const base64 = result.toString().split(',')[1];
                resolve(base64);
            } catch (err) {
                reject(err);
            }
        };
        reader.onerror = (err) => reject(err);
        reader.readAsDataURL(file);
    });
}

// ========== ASSORTMENT TAB ==========
async function loadAssortmentData() {
    try {
        const response = await API.dbQueries.assortment();
        console.log('[LoadAssortment] Response:', response);
        
        // Handle different response formats
        let products = [];
        if (Array.isArray(response)) {
            products = response;
        } else if (response.assortment && Array.isArray(response.assortment)) {
            products = response.assortment;
        } else if (response.items && Array.isArray(response.items)) {
            products = response.items;
        }
        
        const table = document.getElementById('assortmentTable').querySelector('tbody');
        table.innerHTML = '';
        
        if (!products || products.length === 0) {
            table.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem;">Немає товарів</td></tr>';
            return;
        }
        
        // Get unique categories for filter
        const categories = [...new Set(products.map(p => p.category || 'N/A'))];
        const categorySelect = document.getElementById('assortmentCategory');
        categorySelect.innerHTML = '<option value="">Всі категорії</option>';
        categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat;
            option.textContent = cat;
            categorySelect.appendChild(option);
        });
        
        // Add event listener to category filter
        categorySelect.onchange = () => filterAssortmentByCategory(products);
        
        // Display products
        displayAssortmentProducts(products);
    } catch (error) {
        console.error('[LoadAssortment] Error:', error);
        const table = document.getElementById('assortmentTable').querySelector('tbody');
        table.innerHTML = '<tr><td colspan="6" style="text-align: center; color: red;">Помилка завантаження: ' + error.message + '</td></tr>';
    }
}

function filterAssortmentByCategory(products) {
    const selectedCategory = document.getElementById('assortmentCategory').value;
    const filtered = selectedCategory ? products.filter(p => p.category === selectedCategory) : products;
    displayAssortmentProducts(filtered);
}

function displayAssortmentProducts(products) {
    const table = document.getElementById('assortmentTable').querySelector('tbody');
    table.innerHTML = '';
    
    products.forEach(p => {
        const row = `
            <tr>
                <td>${p.article || '-'}</td>
                <td>${p.name || '-'}</td>
                <td>${p.category || '-'}</td>
                <td>${p.supplier || '-'}</td>
                <td>₴${(p.price_uah || 0).toFixed(0)}</td>
                <td>${p.quantity || 0}</td>
            </tr>
        `;
        table.innerHTML += row;
    });
}

// ========== INVENTORY STATUS TAB ==========
async function loadInventoryStatus() {
    try {
        const response = await API.dbQueries.assortment();
        console.log('[LoadInventoryStatus] Response:', response);
        
        // Handle different response formats
        let products = [];
        if (Array.isArray(response)) {
            products = response;
        } else if (response.assortment && Array.isArray(response.assortment)) {
            products = response.assortment;
        } else if (response.items && Array.isArray(response.items)) {
            products = response.items;
        }
        
        const statusFilter = document.getElementById('inventoryStatus')?.value || '';
        const table = document.getElementById('inventoryStatusTable').querySelector('tbody');
        table.innerHTML = '';
        
        if (!products || products.length === 0) {
            table.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem;">Немає товарів</td></tr>';
            return;
        }
        
        // Filter by status
        const filtered = products.filter(p => {
            const quantity = p.quantity || 0;
            const minStock = p.minimum || p.min_stock || 10;
            
            if (statusFilter === 'critical') return quantity < minStock / 2;
            if (statusFilter === 'low') return quantity >= minStock / 2 && quantity < minStock;
            if (statusFilter === 'normal') return quantity >= minStock;
            return true;
        });
        
        if (filtered.length === 0) {
            table.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem;">Немає товарів з цим статусом</td></tr>';
            return;
        }
        
        filtered.forEach(p => {
            const quantity = p.quantity || 0;
            const minStock = p.minimum || p.min_stock || 10;
            let statusBadge = '🟢 Нормально';
            let statusColor = '#27ae60';
            
            if (quantity < minStock / 2) {
                statusBadge = '🔴 Критично мало';
                statusColor = '#e74c3c';
            } else if (quantity < minStock) {
                statusBadge = '🟡 Мало';
                statusColor = '#f39c12';
            }
            
            const row = `
                <tr>
                    <td>${p.article || '-'}</td>
                    <td>${p.name || '-'}</td>
                    <td>${quantity}</td>
                    <td>${minStock}</td>
                    <td><span style="color: ${statusColor}; font-weight: bold;">${statusBadge}</span></td>
                    <td><button class="btn-sm btn-primary" onclick="editProduct('${p.article}')">Редаг.</button></td>
                </tr>
            `;
            table.innerHTML += row;
        });
    } catch (error) {
        console.error('[LoadInventoryStatus] Error:', error);
        const table = document.getElementById('inventoryStatusTable').querySelector('tbody');
        table.innerHTML = '<tr><td colspan="6" style="text-align: center; color: red;">Помилка завантаження: ' + error.message + '</td></tr>';
    }
}

// ========== PRICE & QUANTITY TAB ==========
async function loadPriceQty() {
    try {
        const response = await API.dbQueries.priceQty();
        console.log('[LoadPriceQty] Response:', response);
        
        // Handle different response formats
        let priceData = [];
        if (Array.isArray(response)) {
            priceData = response;
        } else if (response.price_matrix && Array.isArray(response.price_matrix)) {
            priceData = response.price_matrix;
        } else if (response.products && Array.isArray(response.products)) {
            priceData = response.products;
        } else if (response.items && Array.isArray(response.items)) {
            priceData = response.items;
        }
        
        const table = document.getElementById('priceQtyTable').querySelector('tbody');
        if (!table) return;
        
        table.innerHTML = '';
        
        if (!priceData || priceData.length === 0) {
            table.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem;">Немає товарів</td></tr>';
            return;
        }
        
        priceData.forEach(item => {
            const status = item.status === 'In Stock' ? '✓ На складі' : '✗ Низький запас';
            const statusColor = item.status === 'In Stock' ? '#27ae60' : '#e74c3c';
            const row = `
                <tr>
                    <td>${item.name || '-'}</td>
                    <td>${item.article || '-'}</td>
                    <td>${formatPrice(item.price || 0)}</td>
                    <td>${item.quantity || 0}</td>
                    <td><span style="color: ${statusColor}; font-weight: bold;">${status}</span></td>
                    <td>${formatPrice(item.total_value || 0)}</td>
                </tr>
            `;
            table.innerHTML += row;
        });
    } catch (error) {
        console.error('[LoadPriceQty] Error:', error);
        const table = document.getElementById('priceQtyTable')?.querySelector('tbody');
        if (table) {
            table.innerHTML = '<tr><td colspan="6" style="text-align: center; color: red;">Помилка завантаження: ' + error.message + '</td></tr>';
        }
    }
}

// ========== MIN/MAX PRODUCTS TAB ==========
async function loadMinMaxProducts() {
    try {
        const response = await API.dbQueries.minMax();
        console.log('[LoadMinMaxProducts] Response:', response);
        
        // Extract min/max products arrays from response
        let minProducts = [];
        let maxProducts = [];
        
        if (response.min_products && Array.isArray(response.min_products)) {
            minProducts = response.min_products;
        }
        if (response.max_products && Array.isArray(response.max_products)) {
            maxProducts = response.max_products;
        }
        
        // Populate min product (first item in min_products array)
        const minName = document.getElementById('minProductName');
        const minArticle = document.getElementById('minProductArticle');
        const minQty = document.getElementById('minProductQty');
        const minPrice = document.getElementById('minProductPrice');
        
        if (minProducts.length > 0) {
            const minProd = minProducts[0];
            if (minName) minName.textContent = minProd.name || '-';
            if (minArticle) minArticle.textContent = minProd.article || '-';
            if (minQty) minQty.textContent = minProd.quantity || 0;
            if (minPrice) minPrice.textContent = formatPrice(minProd.price || 0);
        }
        
        // Populate max product (first item in max_products array)
        const maxName = document.getElementById('maxProductName');
        const maxArticle = document.getElementById('maxProductArticle');
        const maxQty = document.getElementById('maxProductQty');
        const maxPrice = document.getElementById('maxProductPrice');
        
        if (maxProducts.length > 0) {
            const maxProd = maxProducts[0];
            if (maxName) maxName.textContent = maxProd.name || '-';
            if (maxArticle) maxArticle.textContent = maxProd.article || '-';
            if (maxQty) maxQty.textContent = maxProd.quantity || 0;
            if (maxPrice) maxPrice.textContent = formatPrice(maxProd.price || 0);
        }
    } catch (error) {
        console.error('[LoadMinMaxProducts] Error:', error);
        showNotification('❌ Помилка завантаження мін/макс: ' + error.message, 'danger');
    }
}

// ========== SUPPLIERS TAB ==========
async function loadSuppliers() {
    try {
        const response = await API.dbQueries.suppliers();
        console.log('[LoadSuppliers] Response:', response);
        
        // Handle different response formats
        let suppliersData = [];
        if (Array.isArray(response)) {
            suppliersData = response;
        } else if (response.suppliers && Array.isArray(response.suppliers)) {
            suppliersData = response.suppliers;
        } else if (response.data && Array.isArray(response.data)) {
            suppliersData = response.data;
        }
        
        const table = document.getElementById('suppliersTable');
        if (!table) return;
        
        table.innerHTML = '';
        
        if (!suppliersData || suppliersData.length === 0) {
            table.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 2rem;">Немає постачальників</td></tr>';
            return;
        }
        
        suppliersData.forEach(supplier => {
            const row = `
                <tr>
                    <td>${supplier.name || '-'}</td>
                    <td>${supplier.city || '-'}</td>
                    <td>${supplier.country || '-'}</td>
                    <td>${supplier.contact || supplier.email || '-'}</td>
                    <td>${supplier.products_supplied || 0}</td>
                </tr>
            `;
            table.innerHTML += row;
        });
    } catch (error) {
        console.error('[LoadSuppliers] Error:', error);
        const table = document.getElementById('suppliersTable');
        if (table) {
            table.innerHTML = '<tr><td colspan="5" style="text-align: center; color: red;">Помилка завантаження: ' + error.message + '</td></tr>';
        }
    }
}

// ========== ORDERS TAB ==========
async function populateOrdersDropdown() {
    try {
        const response = await API.dbQueries.assortment();
        console.log('[PopulateOrdersDropdown] Response:', response);
        
        // Handle different response formats
        let products = [];
        if (Array.isArray(response)) {
            products = response;
        } else if (response.assortment && Array.isArray(response.assortment)) {
            products = response.assortment;
        } else if (response.items && Array.isArray(response.items)) {
            products = response.items;
        }
        
        const select = document.getElementById('orderProductName');
        if (!select) return;
        
        // Clear existing options except placeholder
        select.innerHTML = '<option value="">-- Виберіть товар --</option>';
        
        if (!products || products.length === 0) {
            select.innerHTML += '<option disabled>Немає товарів</option>';
            return;
        }
        
        // Add products to dropdown
        products.forEach(product => {
            const option = document.createElement('option');
            option.value = product.article || '';
            option.textContent = `${product.name} (${product.article}) - ${formatPrice(product.price_uah || 0)}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('[PopulateOrdersDropdown] Error:', error);
        const select = document.getElementById('orderProductName');
        if (select) {
            select.innerHTML = '<option disabled>Помилка завантаження</option>';
        }
    }
}

function switchQueryTab(tabName) {
    // Hide all query tabs
    document.querySelectorAll('[id^="query"]').forEach(el => {
        el.style.display = 'none';
    });
    
    // Reset all tab button styles
    document.querySelectorAll('.query-tab').forEach(btn => {
        btn.style.color = '#7f8c8d';
        btn.style.borderBottom = 'none';
    });
    
    // Load data when switching to dynamic tabs
    if (tabName === 'productImage') {
        loadProductImages();
    } else if (tabName === 'assortment') {
        loadAssortmentData();
    } else if (tabName === 'priceQty') {
        loadPriceQty();
    } else if (tabName === 'minMax') {
        loadMinMaxProducts();
    } else if (tabName === 'suppliers') {
        loadSuppliers();
    } else if (tabName === 'inventory') {
        loadInventoryStatus();
    } else if (tabName === 'orders') {
        populateOrdersDropdown();
    }
    
    // Map tab names to correct IDs (handling special cases like suppliers typo in HTML)
    const tabIdMap = {
        'productImage': 'queryProductImage',
        'assortment': 'queryAssortment',
        'priceQty': 'queryPriceQty',
        'minMax': 'queryMinMax',
        'suppliers': 'querySupplers',  // HTML has typo 'Supplers' instead of 'Suppliers'
        'inventory': 'queryInventory',
        'orders': 'queryOrders'
    };
    
    // Show selected query tab
    let queryId = tabIdMap[tabName] || 'query' + tabName.charAt(0).toUpperCase() + tabName.slice(1);
    const selectedQuery = document.getElementById(queryId);
    if (selectedQuery) {
        selectedQuery.style.display = 'block';
    } else {
        console.warn(`Query tab not found: ${queryId}`);
    }
    
    // Highlight active tab
    if (event && event.target) {
        event.target.style.color = 'var(--primary-color)';
        event.target.style.borderBottom = '3px solid var(--primary-color)';
    }
}

async function generateOrder() {
    const productArticle = document.getElementById('orderProductName').value;
    const quantity = parseInt(document.getElementById('orderQuantity').value);
    
    if (!productArticle || !quantity || quantity < 1) {
        showNotification('⚠️ Заповніть усі поля', 'warning');
        return;
    }
    
    try {
        // Fetch assortment data to get product details
        const response = await API.dbQueries.assortment();
        let products = [];
        if (Array.isArray(response)) {
            products = response;
        } else if (response.assortment && Array.isArray(response.assortment)) {
            products = response.assortment;
        } else if (response.items && Array.isArray(response.items)) {
            products = response.items;
        }
        
        // Find selected product
        const productInfo = products.find(p => p.article === productArticle);
        
        if (!productInfo) {
            showNotification('❌ Товар не знайдено', 'danger');
            return;
        }
        
        // Set minimum required based on product minimum stock or default to 5
        const minRequired = productInfo.minimum || productInfo.min_stock || 5;
        
        // Check if quantity meets minimum requirement
        if (quantity < minRequired) {
            showNotification(`⚠️ Мінімальний обсяг замовлення: ${minRequired} шт`, 'warning');
            return;
        }
    
        // Call API to generate order with validation
        const orderPayload = {
            product_id: productArticle,
            quantity: quantity
        };
        
        const orderResponse = await API.dbQueries.generateOrder(orderPayload);
        
        if (!orderResponse || !orderResponse.order) {
            showNotification('❌ Помилка генерування замовлення', 'danger');
            return;
        }
        
        const order = orderResponse.order;
        const validation = orderResponse.validation || {};
        const businessLetter = orderResponse.business_letter || '';
        
        // Display validation info and order
        const container = document.getElementById('generatedOrdersContainer');
        const ordersContent = document.getElementById('ordersContent');
        
        let validationHTML = '';
        if (validation.validation_passed) {
            validationHTML = `
            <div style="background: #d5f4e6; border-left: 4px solid #27ae60; padding: 1rem; margin-bottom: 1rem; border-radius: 5px;">
                <strong style="color: #27ae60;">✓ Замовлення відповідає вимогам</strong>
                <p style="margin: 0.5rem 0 0; color: #16a085;">
                    Замовлена кількість (${validation.quantity_ordered} шт) >= Мінімально вимагається (${validation.min_stock_required} шт)
                </p>
            </div>`;
        } else {
            validationHTML = `
            <div style="background: #fadbd8; border-left: 4px solid #e74c3c; padding: 1rem; margin-bottom: 1rem; border-radius: 5px;">
                <strong style="color: #e74c3c;">✗ Замовлення не відповідає вимогам</strong>
                <p style="margin: 0.5rem 0 0; color: #c0392b;">${validation.message || 'Перевірте кількість'}</p>
            </div>`;
        }
        
        const orderDetailsHTML = `
        <div style="background: #ecf0f1; padding: 1rem; border-radius: 5px; margin-bottom: 1rem;">
            <h4 style="margin-top: 0;">Деталі замовлення:</h4>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 0.5rem; border-bottom: 1px solid #bdc3c7;">Товар:</td>
                    <td style="padding: 0.5rem; border-bottom: 1px solid #bdc3c7;"><strong>${order.name}</strong></td>
                </tr>
                <tr>
                    <td style="padding: 0.5rem; border-bottom: 1px solid #bdc3c7;">Артикул:</td>
                    <td style="padding: 0.5rem; border-bottom: 1px solid #bdc3c7;"><strong>${order.article}</strong></td>
                </tr>
                <tr>
                    <td style="padding: 0.5rem; border-bottom: 1px solid #bdc3c7;">Кількість:</td>
                    <td style="padding: 0.5rem; border-bottom: 1px solid #bdc3c7;"><strong>${order.quantity} шт</strong></td>
                </tr>
                <tr>
                    <td style="padding: 0.5rem; border-bottom: 1px solid #bdc3c7;">Ціна за одиницю:</td>
                    <td style="padding: 0.5rem; border-bottom: 1px solid #bdc3c7;"><strong>${formatPrice(order.unit_price)}</strong></td>
                </tr>
                <tr>
                    <td style="padding: 0.5rem; border-bottom: 1px solid #bdc3c7;">Сумарна вартість:</td>
                    <td style="padding: 0.5rem; border-bottom: 1px solid #bdc3c7;"><strong style="color: var(--primary-color);">${formatPrice(order.total_price)}</strong></td>
                </tr>
                <tr>
                    <td style="padding: 0.5rem; border-bottom: 1px solid #bdc3c7;">Постачальник:</td>
                    <td style="padding: 0.5rem; border-bottom: 1px solid #bdc3c7;"><strong>${order.supplier}</strong></td>
                </tr>
                <tr>
                    <td style="padding: 0.5rem;">Очікувана доставка:</td>
                    <td style="padding: 0.5rem;"><strong>${order.expected_delivery}</strong></td>
                </tr>
            </table>
        </div>`;
        
        const businessLetterHTML = `
        <div style="margin-bottom: 1rem;">
            <h4>Ділове замовлення:</h4>
            <pre style="background: white; padding: 1.5rem; font-family: 'Courier New', monospace; font-size: 0.85rem; line-height: 1.5; border-radius: 5px; overflow-x: auto; border: 1px solid #ddd;">${businessLetter}</pre>
        </div>`;
        
        ordersContent.innerHTML = validationHTML + orderDetailsHTML + businessLetterHTML + `
        <div style="margin-top: 1rem; display: flex; gap: 1rem; flex-wrap: wrap;">
            <button class="btn-primary" onclick="printOrder()">🖨️ Друкувати</button>
            <button class="btn-success" onclick="sendOrder('${order.supplier}', '${quantity} x ${order.name}')">📧 Надіслати</button>
            <button class="btn-warning" onclick="downloadOrderPDF()">📥 Завантажити PDF</button>
            <button class="btn-secondary" onclick="clearOrder()">✖️ Очистити</button>
        </div>`;
        
        container.style.display = 'block';
        showNotification('✅ Замовлення сформовано успішно!', 'success');
    } catch (error) {
        console.error('[GenerateOrder] Error:', error);
        showNotification('❌ Помилка формування замовлення: ' + error.message, 'danger');
    }
}

function printOrder() {
    window.print();
    showNotification('🖨️ Відправлено на друк', 'info');
}

function sendOrder(supplier, product) {
    showNotification(`📧 Замовлення надіслано ${supplier}\n${product}`, 'success');
}

function downloadOrderPDF() {
    showNotification('📥 Функція завантаження PDF буде доступна в наступному оновленні', 'info');
}

function clearOrder() {
    document.getElementById('generatedOrdersContainer').style.display = 'none';
    document.getElementById('orderProductName').value = '';
    document.getElementById('orderQuantity').value = '';
    showNotification('🗑️ Замовлення очищено', 'info');
}

// ==========================================
// TRAINER EDIT/DELETE
// ==========================================
async function editTrainer(trainerId) {
    try {
        const trainers = await API.trainers.list();
        const trainer = trainers.find(t => t.trainer_id === trainerId);

        if (!trainer) {
            showNotification('Тренера не знайдено', 'danger');
            return;
        }

        const fullName = prompt('ПІБ тренера', trainer.full_name || '');
        if (fullName === null || !fullName.trim()) {
            showNotification('Редагування скасовано', 'info');
            return;
        }

        const specialization = prompt('Спеціалізація', trainer.specialization || '');
        if (specialization === null || !specialization.trim()) {
            showNotification('Спеціалізація обов\'язкова', 'warning');
            return;
        }

        const phone = prompt('Телефон', trainer.contact_info?.phone || '') || '';
        const email = prompt('Email', trainer.contact_info?.email || '') || '';

        const contact_info = {};
        if (phone.trim()) contact_info.phone = phone.trim();
        if (email.trim()) contact_info.email = email.trim();

        const payload = {
            full_name: fullName.trim(),
            specialization: specialization.trim(),
            birth_date: trainer.birth_date || '1990-01-01',
            gender: trainer.gender || 'MALE',
            contact_info: Object.keys(contact_info).length ? contact_info : null
        };

        await API.trainers.update(trainerId, payload);
        showNotification('✓ Тренера оновлено', 'success');
        loadTrainers();
    } catch (error) {
        console.error('[EditTrainer] Error:', error);
        showNotification('Помилка редагування: ' + error.message, 'danger');
    }
}

async function deleteTrainer(trainerId) {
    if (!confirm('Видалити цього тренера?')) return;
    try {
        await apiFetch(`/sport/trainers/${trainerId}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        showNotification('✓ Тренер видалений успішно', 'success');
        loadTrainers();
    } catch (error) {
        showNotification('Помилка видалення: ' + error.message, 'danger');
    }
}

// ==========================================
// SERVICE EDIT/DELETE
// ==========================================
async function editService(serviceId) {
    try {
        const services = await API.services.list();
        const service = services.find(s => s.service_id === serviceId);

        if (!service) {
            showNotification('Послугу не знайдено', 'danger');
            return;
        }

        const name = prompt('Назва послуги', service.service_name || '');
        if (name === null || !name.trim()) {
            showNotification('Редагування скасовано', 'info');
            return;
        }

        const priceInput = prompt('Ціна (₴)', service.price ?? '');
        if (priceInput === null) {
            showNotification('Редагування скасовано', 'info');
            return;
        }

        const price = parseFloat(priceInput);
        if (Number.isNaN(price) || price <= 0) {
            showNotification('Ціна повинна бути додатним числом', 'warning');
            return;
        }

        const requiresMedical = confirm(`Потрібна медична довідка? Поточне значення: ${service.requires_medical_certificate ? 'так' : 'ні'}`);

        const payload = {
            service_name: name.trim(),
            price: price,
            requires_medical_certificate: requiresMedical
        };

        await API.services.update(serviceId, payload);
        showNotification('✓ Послугу оновлено', 'success');
        loadAdminServices();
    } catch (error) {
        console.error('[EditService] Error:', error);
        showNotification('Помилка редагування: ' + error.message, 'danger');
    }
}

async function deleteService(serviceId) {
    if (!confirm('Видалити цю послугу?')) return;
    try {
        await apiFetch(`/sport/services/${serviceId}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        showNotification('✓ Послуга видалена успішно', 'success');
        loadAdminServices();
    } catch (error) {
        showNotification('Помилка видалення: ' + error.message, 'danger');
    }
}

// ==========================================
// MEMBERSHIPS (АБОНЕМЕНТИ)
// ==========================================

let currentEditMembershipId = null;

async function loadMemberships() {
    try {
        const memberships = await API.memberships.list();
        const clientsResponse = await API.clients.list();
        
        // Handle both paginated and legacy response formats
        const clients = Array.isArray(clientsResponse) ? clientsResponse : (clientsResponse.items || []);
        
        const clientMap = {};
        clients.forEach(c => clientMap[c.client_id] = c.full_name);

        // Populate client dropdown
        const clientSelect = document.getElementById('membershipClientId');
        if (clientSelect && clientSelect.options.length <= 1) {
            clients.forEach(client => {
                const option = document.createElement('option');
                option.value = client.client_id;
                option.textContent = client.full_name;
                clientSelect.appendChild(option);
            });
        }

        const tbody = document.getElementById('membershipsTable');
        if (!tbody) return;

        if (!memberships || memberships.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem;">Нема абонементів</td></tr>';
            return;
        }

        tbody.innerHTML = memberships.map(m => `
            <tr>
                <td>${clientMap[m.client_id] || 'Unknown'}</td>
                <td>${m.subscription_type || '-'}</td>
                <td><span class="status-badge ${m.status === 'active' ? 'active' : 'inactive'}">${m.status || 'inactive'}</span></td>
                <td>${formatDate(m.end_date)}</td>
                <td>${m.price ? formatPrice(m.price) : '-'}</td>
                <td>
                    <button class="btn-sm btn-info" onclick="editMembership(${m.membership_id})">✏️ Редагувати</button>
                    <button class="btn-sm btn-danger" onclick="deleteMembership(${m.membership_id})">🗑️ Видалити</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('[LoadMemberships] Error:', error);
        showNotification('Помилка завантаження абонементів: ' + error.message, 'danger');
    }
}

async function addMembership() {
    const clientId = document.getElementById('membershipClientId').value;
    const type = document.getElementById('membershipType').value;
    const startDate = document.getElementById('membershipStartDate').value;
    const endDate = document.getElementById('membershipEndDate').value;
    const price = document.getElementById('membershipPrice').value || null;

    if (!clientId || !type || !startDate || !endDate) {
        showNotification('⚠️ Заповніть обов\'язкові поля', 'warning');
        return;
    }

    if (new Date(startDate) >= new Date(endDate)) {
        showNotification('⚠️ Дата закінчення повинна бути після дати початку', 'warning');
        return;
    }

    try {
        const payload = {
            client_id: parseInt(clientId),
            start_date: startDate,
            end_date: endDate,
            status: 'active',
            subscription_type: type,
            price: price ? parseFloat(price) : null
        };

        await API.memberships.create(payload);
        showNotification('✓ Абонемент додано успішно', 'success');
        
        // Reset form
        document.getElementById('addMembershipForm').reset();
        document.getElementById('addMembershipForm').style.display = 'none';
        loadMemberships();
    } catch (error) {
        console.error('[AddMembership] Error:', error);
        showNotification('Помилка додавання абонемента: ' + error.message, 'danger');
    }
}

async function editMembership(membershipId) {
    try {
        const memberships = await API.memberships.list();
        const membership = memberships.find(m => m.membership_id === membershipId);
        
        if (!membership) {
            showNotification('Абонемент не знайдено', 'danger');
            return;
        }

        currentEditMembershipId = membershipId;

        // Create modal for editing
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close" onclick="this.parentElement.parentElement.remove()">&times;</span>
                <h3>Редагування абонемента</h3>
                <form onsubmit="event.preventDefault(); updateMembership();">
                    <div class="form-group">
                        <label>Клієнт</label>
                        <input type="text" value="${membership.client_name || 'Unknown'}" readonly>
                    </div>
                    <div class="form-group">
                        <label for="editMembershipType">Тип абонемента</label>
                        <select id="editMembershipType" required>
                            <option value="UNLIMITED" ${membership.subscription_type === 'UNLIMITED' ? 'selected' : ''}>Безлімітний</option>
                            <option value="MONTHLY" ${membership.subscription_type === 'MONTHLY' ? 'selected' : ''}>Місячний</option>
                            <option value="SINGLE" ${membership.subscription_type === 'SINGLE' ? 'selected' : ''}>Одноразовий</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="editMembershipStartDate">Дата початку</label>
                        <input type="date" id="editMembershipStartDate" value="${membership.start_date || ''}" required>
                    </div>
                    <div class="form-group">
                        <label for="editMembershipEndDate">Дата закінчення</label>
                        <input type="date" id="editMembershipEndDate" value="${membership.end_date || ''}" required>
                    </div>
                    <div class="form-group">
                        <label for="editMembershipStatus">Статус</label>
                        <select id="editMembershipStatus" required>
                            <option value="active" ${membership.status === 'active' ? 'selected' : ''}>Активний</option>
                            <option value="inactive" ${membership.status === 'inactive' ? 'selected' : ''}>Неактивний</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="editMembershipPrice">Ціна (₴)</label>
                        <input type="number" id="editMembershipPrice" value="${membership.price || ''}" step="0.01" min="0">
                    </div>
                    <div style="display: flex; gap: 0.75rem; margin-top: 1rem;">
                        <button type="submit" class="btn-success">Зберегти</button>
                        <button type="button" class="btn-secondary" onclick="this.closest('.modal').remove()">Скасувати</button>
                    </div>
                </form>
            </div>
        `;
        
        document.body.appendChild(modal);
        modal.style.display = 'block';
    } catch (error) {
        console.error('[EditMembership] Error:', error);
        showNotification('Помилка редагування абонемента: ' + error.message, 'danger');
    }
}

async function updateMembership() {
    if (!currentEditMembershipId) return;

    try {
        const type = document.getElementById('editMembershipType').value;
        const startDate = document.getElementById('editMembershipStartDate').value;
        const endDate = document.getElementById('editMembershipEndDate').value;
        const status = document.getElementById('editMembershipStatus').value;
        const price = document.getElementById('editMembershipPrice').value || null;

        if (new Date(startDate) >= new Date(endDate)) {
            showNotification('⚠️ Дата закінчення повинна бути після дати початку', 'warning');
            return;
        }

        const payload = {
            start_date: startDate,
            end_date: endDate,
            status: status,
            subscription_type: type,
            price: price ? parseFloat(price) : null
        };

        await API.memberships.update(currentEditMembershipId, payload);
        showNotification('✓ Абонемент оновлено успішно', 'success');
        
        // Close modal
        document.querySelector('.modal').remove();
        currentEditMembershipId = null;
        loadMemberships();
    } catch (error) {
        console.error('[UpdateMembership] Error:', error);
        showNotification('Помилка оновлення абонемента: ' + error.message, 'danger');
    }
}

async function deleteMembership(membershipId) {
    if (!confirm('Видалити цей абонемент?')) return;
    
    try {
        await API.memberships.delete(membershipId);
        showNotification('✓ Абонемент видалено успішно', 'success');
        loadMemberships();
    } catch (error) {
        console.error('[DeleteMembership] Error:', error);
        showNotification('Помилка видалення абонемента: ' + error.message, 'danger');
    }
}

// ========== PRODUCTS SYNC FUNCTION ==========

async function syncProductsWithDB() {
    try {
        showNotification('🔄 Синхронізація з базою даних...', 'info');
        const syncData = await API.dbQueries.syncProducts();
        
        if (!syncData || !syncData.db_products) {
            showNotification('⚠️ Помилка синхронізації: невалідні дані', 'warning');
            return;
        }

        // Display sync results in a modal
        const modal = document.createElement('div');
        modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1001; display: flex; align-items: center; justify-content: center; padding: 1rem;';
        modal.innerHTML = `
            <div style="background: white; padding: 1.5rem; border-radius: 8px; max-width: 800px; width: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-height: 90vh; overflow-y: auto;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h2 style="margin: 0;">✓ Результати синхронізації</h2>
                    <button style="background: none; border: none; font-size: 1.35rem; cursor: pointer; color: #999;" onclick="this.closest('div').parentElement.remove()">×</button>
                </div>
                
                <div style="background: #f9f9f9; padding: 1rem; border-radius: 5px; margin-bottom: 1rem;">
                    <p><strong>Статус:</strong> ${syncData.summary ? syncData.summary.sync_recommendation : 'Синхронізовано'}</p>
                    <p><strong>Товарів у БД:</strong> ${syncData.db_products.length}</p>
                </div>

                <h3>Товари у базі даних асортименту:</h3>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 1rem;">
                    <thead>
                        <tr style="background: #f0f0f0;">
                            <th style="padding: 0.5rem; text-align: left; border-bottom: 1px solid #ddd;">Артикул</th>
                            <th style="padding: 0.5rem; text-align: left; border-bottom: 1px solid #ddd;">Назва</th>
                            <th style="padding: 0.5rem; text-align: center; border-bottom: 1px solid #ddd;">Ціна (₴)</th>
                            <th style="padding: 0.5rem; text-align: center; border-bottom: 1px solid #ddd;">Кількість</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${syncData.db_products.map(p => `
                            <tr style="border-bottom: 1px solid #eee;">
                                <td style="padding: 0.5rem;">${p.article || '-'}</td>
                                <td style="padding: 0.5rem;">${p.name || '-'}</td>
                                <td style="padding: 0.5rem; text-align: center;">₴${(p.price_uah || 0).toFixed(0)}</td>
                                <td style="padding: 0.5rem; text-align: center;">${p.quantity || 0}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>

                <div style="display: flex; gap: 0.5rem;">
                    <button class="btn-primary" onclick="this.closest('div').parentElement.remove()">Закрити</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        showNotification('✓ Синхронізація завершена успішно', 'success');
    } catch (error) {
        console.error('[SyncProducts] Error:', error);
        showNotification('❌ Помилка синхронізації: ' + error.message, 'danger');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Check if user has token, only then verify auth status
    const token = localStorage.getItem('authToken');
    if (token) {
        updateAuthStatus();
    } else {
        // User is not authenticated, show login button
        document.getElementById('authStatus').textContent = '❌ Не авторизовано';
        document.getElementById('loginBtn').style.display = 'inline-block';
        document.getElementById('logoutBtn').style.display = 'none';
    }
    switchPage('home');
});
