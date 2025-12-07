// ==========================================
// Authentication Management
// ==========================================

// Check authentication status
async function updateAuthStatus() {
    try {
        const user = await API.me();
        const authStatus = document.getElementById('authStatus');
        
        if (authStatus) {
            authStatus.textContent = `✅ ${user.username} (${user.role})`;
            authStatus.className = 'auth-status authenticated';
        }
        
        localStorage.setItem('authRole', user.role);
        return true;
    } catch (error) {
        localStorage.removeItem('authToken');
        localStorage.removeItem('authRole');
        return false;
    }
}

// ==========================================
// Login
// ==========================================

async function login() {
    const usernameInput = document.getElementById('loginUsername');
    const passwordInput = document.getElementById('loginPassword');
    const loginError = document.getElementById('loginError');
    
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();
    
    console.log(`[LOGIN] Username: "${username}", Password length: ${password.length}`);

    if (!username || !password) {
        if (loginError) {
            loginError.textContent = 'Будь ласка, заповніть всі поля';
            loginError.style.display = 'block';
        }
        return;
    }

    try {
        const response = await API.login(username, password);
        console.log('[LOGIN] Success:', response);
        
        localStorage.setItem('authToken', response.access_token);
        localStorage.setItem('authRole', response.role);
        localStorage.setItem('authUsername', username);
        
        usernameInput.value = '';
        passwordInput.value = '';
        
        if (loginError) {
            loginError.style.display = 'none';
        }
        
        // Оновити UI та перейти в додаток
        await updateAuthStatus();
        showAuthenticatedUI();
        showNotification(`Ласкаво просимо, ${username}!`, 'success');
        
        // Call updateNavigationForRole to show correct nav
        if (window.updateNavigationForRole) {
            updateNavigationForRole();
        }
        
        // Show role-specific home page
        showRoleSpecificHome(response.role);
        
    } catch (error) {
        console.error('[LOGIN] Error:', error);
        if (loginError) {
            loginError.textContent = 'Помилка входу: ' + error.message;
            loginError.style.display = 'block';
        }
        showNotification('Помилка входу: ' + error.message, 'danger');
    }
}

// ==========================================
// Register
// ==========================================

async function register() {
    const usernameInput = document.getElementById('registerUsername');
    const passwordInput = document.getElementById('registerPassword');
    const passwordConfirmInput = document.getElementById('registerPasswordConfirm');
    const emailInput = document.getElementById('registerEmail');
    const registerError = document.getElementById('registerError');
    const registerSuccess = document.getElementById('registerSuccess');
    
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();
    const passwordConfirm = passwordConfirmInput.value.trim();
    const email = emailInput.value.trim();
    
    // Clear previous messages
    if (registerError) registerError.style.display = 'none';
    if (registerSuccess) registerSuccess.style.display = 'none';
    
    // Валідація
    if (!username || !password || !passwordConfirm) {
        if (registerError) {
            registerError.textContent = 'Будь ласка, заповніть обов\'язкові поля';
            registerError.style.display = 'block';
        }
        return;
    }
    
    if (username.length < 3) {
        if (registerError) {
            registerError.textContent = 'Ім\'я користувача повинно мати мінімум 3 символи';
            registerError.style.display = 'block';
        }
        return;
    }
    
    if (password.length < 6) {
        if (registerError) {
            registerError.textContent = 'Пароль повинен мати мінімум 6 символів';
            registerError.style.display = 'block';
        }
        return;
    }
    
    if (password !== passwordConfirm) {
        if (registerError) {
            registerError.textContent = 'Паролі не збігаються';
            registerError.style.display = 'block';
        }
        return;
    }

    try {
        const response = await API.register(username, password, email);
        console.log('[REGISTER] Success:', response);
        
        // Показати повідомлення про успіх
        if (registerSuccess) {
            registerSuccess.textContent = '✅ Реєстрація успішна! Тепер увійдіть з вашими даними.';
            registerSuccess.style.display = 'block';
        }
        showNotification('Реєстрація успішна! Тепер увійдіть.', 'success');
        
        // Очистити форму
        usernameInput.value = '';
        passwordInput.value = '';
        passwordConfirmInput.value = '';
        emailInput.value = '';
        
        // Через 2 секунди переключитися на вкладку входу
        setTimeout(() => {
            switchAuthTab('login');
            if (registerSuccess) registerSuccess.style.display = 'none';
            document.getElementById('loginUsername').focus();
        }, 2000);
        
    } catch (error) {
        console.error('[REGISTER] Error:', error);
        if (registerError) {
            registerError.textContent = 'Помилка реєстрації: ' + error.message;
            registerError.style.display = 'block';
        }
        showNotification('Помилка реєстрації: ' + error.message, 'danger');
    }
}

// ==========================================
// Logout
// ==========================================

async function logout() {
    // Clear token from storage immediately
    localStorage.removeItem('authToken');
    localStorage.removeItem('authRole');
    
    // Try to notify backend, but don't fail if it errors
    try {
        await API.logout();
    } catch (error) {
        console.error('Logout error:', error);
    }
    
    showNotification('Ви вийшли з системи', 'info');
    showLoginUI();
}

// ==========================================
// UI Management
// ==========================================

function showAuthenticatedUI() {
    // Показати основний інтерфейс після авторизації
    const loginScreen = document.getElementById('loginScreen');
    const header = document.getElementById('header');
    const mainContainer = document.getElementById('mainContainer');
    
    if (loginScreen) loginScreen.classList.add('hidden');
    if (header) header.style.display = 'block';
    if (mainContainer) mainContainer.style.display = 'block';
}

function showLoginUI() {
    // Показати екран входу (перед авторизацією)
    const loginScreen = document.getElementById('loginScreen');
    const header = document.getElementById('header');
    const mainContainer = document.getElementById('mainContainer');
    
    if (loginScreen) loginScreen.classList.remove('hidden');
    if (header) header.style.display = 'none';
    if (mainContainer) mainContainer.style.display = 'none';
}

// ==========================================
// Initialization
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    // Перевірити, чи користувач уже авторизований
    const token = localStorage.getItem('authToken');
    
    if (token) {
        // Користувач має токен, перевіримо його дійсність
        updateAuthStatus().then(isValid => {
            if (isValid) {
                showAuthenticatedUI();
                // Show role-specific home page
                const role = localStorage.getItem('authRole') || 'user';
                if (window.updateNavigationForRole) {
                    updateNavigationForRole();
                }
                showRoleSpecificHome(role);
            } else {
                showLoginUI();
            }
        });
    } else {
        // Користувач не авторизований, показати екран входу
        showLoginUI();
    }
    
    // Auto-focus on login username field
    setTimeout(() => {
        const loginUsernameInput = document.getElementById('loginUsername');
        if (loginUsernameInput) loginUsernameInput.focus();
    }, 100);
});

// ==========================================
// Role-Specific Home Page
// ==========================================

function showRoleSpecificHome(role) {
    // Hide all home pages
    const homePageUser = document.getElementById('homePageUser');
    const homePageAdmin = document.getElementById('homePageAdmin');
    
    if (homePageUser) homePageUser.style.display = 'none';
    if (homePageAdmin) homePageAdmin.style.display = 'none';
    
    // Show role-specific home
    if (role === 'admin') {
        if (homePageAdmin) homePageAdmin.style.display = 'block';
    } else {
        if (homePageUser) homePageUser.style.display = 'block';
    }
    
    // Trigger switch to home page with role-specific content
    if (window.switchPage) {
        switchPage('home');
    }
}
