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

function handleLoginSubmit(e) {
    e.preventDefault();

    const email = loginForm.querySelector('input[type="email"]').value;
    const password = loginForm.querySelector('input[type="password"]').value;
    const rememberMe = loginForm.querySelector('.checkbox-input').checked;

    if (!email || !password) {
        showNotification('Please fill in all fields', 'error');
        return;
    }

    if (!isValidEmail(email)) {
        showNotification('Please enter a valid email address', 'error');
        return;
    }

    const submitBtn = loginForm.querySelector('.btn-signin');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>Signing in...</span>';

    setTimeout(() => {
        if (rememberMe) {
            localStorage.setItem('rememberedEmail', email);
        }

        showNotification('Login successful! Redirecting...', 'success');
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;

        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1500);
    }, 1500);
}

function handleSignupSubmit(e) {
    e.preventDefault();

    const form = e.target;
    const inputs = form.querySelectorAll('.form-input');
    const name = inputs[0].value;
    const email = inputs[1].value;
    const password = inputs[2].value;
    const confirmPassword = inputs[3].value;
    const agreeTerms = form.querySelector('.checkbox-input').checked;

    if (!name || !email || !password || !confirmPassword) {
        showNotification('Please fill in all fields', 'error');
        return;
    }

    if (!isValidEmail(email)) {
        showNotification('Please enter a valid email address', 'error');
        return;
    }

    if (!isValidPassword(password)) {
        showNotification(
            'Password must be at least 8 characters',
            'error'
        );
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

    setTimeout(() => {
        showNotification('Account created successfully! Logging in...', 'success');
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;

        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1500);
    }, 1500);
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
