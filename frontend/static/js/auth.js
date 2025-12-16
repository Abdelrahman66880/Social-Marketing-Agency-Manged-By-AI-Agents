/**
 * Authentication Page - JavaScript
 * Handles tab switching, form interactions, and authentication logic
 */

const tabButtons = document.querySelectorAll('.tab-btn');
const authForms = document.querySelectorAll('.auth-form');
const formInputs = document.querySelectorAll('.form-input');
const loginForm = document.getElementById('loginForm');
const signupForm = document.getElementById('signupForm');
const signupLink = document.querySelector('.signup-link');
const loginLink = document.querySelector('.login-link');
const btnSignin = document.querySelectorAll('.btn-signin');
const checkboxes = document.querySelectorAll('.checkbox-input');

// ============================================
// TAB SWITCHING
// ============================================

function initTabSwitching() {
    tabButtons.forEach((btn) => {
        btn.addEventListener('click', (e) => {
            const tabName = btn.dataset.tab;
            switchTab(tabName);
        });
    });

    if (signupLink) {
        signupLink.addEventListener('click', (e) => {
            e.preventDefault();
            switchTab('signup');
        });
    }

    if (loginLink) {
        loginLink.addEventListener('click', (e) => {
            e.preventDefault();
            switchTab('login');
        });
    }
}

function switchTab(tabName) {
    tabButtons.forEach((btn) => {
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    authForms.forEach((form) => {
        if (form.id === `${tabName}Form`) {
            form.classList.add('active');
        } else {
            form.classList.remove('active');
        }
    });

    clearFormInputs();
}

function clearFormInputs() {
    formInputs.forEach((input) => {
        input.value = '';
    });
    checkboxes.forEach((checkbox) => {
        checkbox.checked = false;
    });
}

// ============================================
// FORM HANDLING
// ============================================

function initFormHandlers() {
    if (loginForm) {
        loginForm.addEventListener('submit', handleLoginSubmit);
    }

    if (signupForm) {
        signupForm.addEventListener('submit', handleSignupSubmit);
    }
}

async function handleLoginSubmit(e) {
    e.preventDefault();

    const email = loginForm.querySelector('input[name="username"]').value.trim();
    const password = loginForm.querySelector('input[name="password"]').value;
    const rememberMe = loginForm.querySelector('.checkbox-input').checked;

    if (!email || !password) {
        showNotification('Please fill in all fields', 'error');
        return;
    }

    const submitBtn = loginForm.querySelector('.btn-signin');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>Signing in...</span>';

    try {
        const formData = new URLSearchParams();
        formData.append('username', email); // OAuth2PasswordRequestForm uses 'username' for email
        formData.append('password', password);

        const response = await fetch('/auth/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            try {
                const errorData = JSON.parse(errorText);
                throw new Error(errorData.detail || 'Login failed');
            } catch (e) {
                if (e instanceof SyntaxError) {
                    // Response was not JSON (likely 500 HTML)
                    console.error("Login Error (Non-JSON):", errorText);
                    throw new Error(`Server Error (${response.status}). Please try again later.`);
                }
                throw e; // rethrow parsed error
            }
        }

        const data = await response.json();

        // Store auth data
        localStorage.setItem('accessToken', data.access_token);
        // We might want to fetch user details to get the ID, but for now token is key

        if (rememberMe) {
            localStorage.setItem('rememberedEmail', email);
        }

        showNotification('Login successful! Redirecting...', 'success');

        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1000);

    } catch (error) {
        showNotification(error.message, 'error');
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

async function handleSignupSubmit(e) {
    e.preventDefault();

    const form = e.target;
    console.log('Signup form submitted');

    // Select inputs by name attribute for robustness
    const nameInput = form.querySelector('input[name="username"]');
    const emailInput = form.querySelector('input[name="email"]');
    const passwordInput = form.querySelector('input[name="password"]');
    const confirmPasswordInput = form.querySelector('input[name="confirmPassword"]');

    if (!nameInput || !emailInput || !passwordInput || !confirmPasswordInput) {
        alert('Error: Could not find one or more form fields. Please refresh the page.');
        console.error('Missing inputs:', { nameInput, emailInput, passwordInput, confirmPasswordInput });
        return;
    }

    const name = nameInput.value.trim();
    const email = emailInput.value.trim();
    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;

    const agreeTerms = form.querySelector('.checkbox-input').checked;

    if (!name || !email || !password || !confirmPassword) {
        showNotification('Please fill in all fields', 'error');
        return;
    }

    // Validate username (letters, numbers, spaces)
    const nameRegex = /^[a-zA-Z0-9 ]+$/;
    if (!nameRegex.test(name)) {
        showNotification('Username must only contain letters, numbers, and spaces', 'error');
        return;
    }

    if (name.length > 30) {
        showNotification('Username must be 30 characters or less', 'error');
        return;
    }

    if (password.length < 8) {
        showNotification('Password must be at least 8 characters long', 'error');
        return;
    }

    if (password !== confirmPassword) {
        showNotification('Passwords do not match', 'error');
        return;
    }

    if (!agreeTerms) {
        showNotification('Please agree to the Terms of Service', 'error');
        return;
    }

    const submitBtn = form.querySelector('.btn-signin');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>Creating account...</span>';

    try {
        // UserRegisterRequest: username, email, password
        const payload = {
            username: name,
            email: email,
            password: password
        };

        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            let errorMessage = 'Registration failed';
            // Try to extract specific error message
            if (data.detail) {
                if (typeof data.detail === 'string') {
                    errorMessage = data.detail;
                } else if (Array.isArray(data.detail)) {
                    // Extract first Pydantic error
                    errorMessage = data.detail[0]?.msg || JSON.stringify(data.detail);
                } else if (data.detail.message) {
                    errorMessage = data.detail.message;
                }
            } else if (data.message) {
                errorMessage = data.message;
            }

            throw new Error(errorMessage);
        }

        // Check for specific signal
        // Check for specific signal
        if (data.signal === 'User registered successfully' || data.user_id) {
            showNotification('Account created! Configuring setup...', 'success');

            // Wait a moment for DB propagation then auto-login
            setTimeout(async () => {
                const loginFormData = new URLSearchParams();
                loginFormData.append('username', email); // OAuth2 form uses username for email
                loginFormData.append('password', password);

                const loginResponse = await fetch('/auth/token', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: loginFormData
                });

                if (loginResponse.ok) {
                    const loginData = await loginResponse.json();
                    localStorage.setItem('accessToken', loginData.access_token);
                    localStorage.setItem('userId', data.user_id);

                    // SUCCESS -> Setup Page
                    window.location.href = 'business_setup.html';
                } else {
                    const loginErrorText = await loginResponse.text();
                    console.error("Auto-login failed:", loginResponse.status, loginErrorText);

                    // Try to parse error
                    try {
                        const loginErrorJson = JSON.parse(loginErrorText);
                        showNotification(`Account created, but auto-login failed: ${loginErrorJson.detail || 'Unknown error'}`, 'error');
                    } catch (e) {
                        showNotification(`Account created, but auto-login failed: ${loginResponse.status}`, 'error');
                    }

                    switchTab('login');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }
            }, 500); // 500ms delay to ensure user is queryable
        } else if (data.signal === 'error user is already exist') {
            showNotification('This email is already registered. Please log in.', 'error');
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        } else {
            console.error('Unexpected response:', data);
            throw new Error(`Unexpected response: ${data.signal} (Check console for details)`);
        }

    } catch (error) {
        console.error('Signup error:', error);
        alert('Signup Error: ' + error.message);
        showNotification(error.message, 'error');
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

// ============================================
// VALIDATION HELPERS
// ============================================

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPassword(password) {
    return password.length >= 8;
}

// ============================================
// NOTIFICATIONS
// ============================================

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification {
                position: fixed;
                bottom: 20px;
                right: 20px;
                padding: 16px 20px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 500;
                z-index: 10000;
                animation: slideInRight 0.3s ease-out;
                max-width: 400px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
            }

            .notification-success {
                background: #10B981;
                color: white;
            }

            .notification-error {
                background: #EF4444;
                color: white;
            }

            .notification-info {
                background: #3B82F6;
                color: white;
            }

            @keyframes slideInRight {
                from {
                    opacity: 0;
                    transform: translateX(100px);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }

            @media (max-width: 480px) {
                .notification {
                    bottom: 10px;
                    right: 10px;
                    left: 10px;
                    max-width: none;
                }
            }
        `;
        document.head.appendChild(style);
    }

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out forwards';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initTabSwitching();
    initFormHandlers();

    const rememberedEmail = localStorage.getItem('rememberedEmail');
    if (rememberedEmail) {
        const emailInput = loginForm.querySelector('input[type="email"]');
        if (emailInput) {
            emailInput.value = rememberedEmail;
            const checkbox = loginForm.querySelector('.checkbox-input');
            if (checkbox) {
                checkbox.checked = true;
            }
        }
    }

    console.log('Auth page initialized');
});

// ============================================
// KEYBOARD SHORTCUTS
// ============================================

document.addEventListener('keydown', (e) => {
    if (e.altKey && e.key === 'l') {
        switchTab('login');
    }

    if (e.altKey && e.key === 's') {
        switchTab('signup');
    }

    if (e.key === 'Escape') {
        clearFormInputs();
    }
});
