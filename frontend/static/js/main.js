/**
 * Home Page - JavaScript
 * Handles navigation, animations, and interactions
 */

// ============================================
// NAVIGATION
// ============================================

function initNavigation() {
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');

    if (navToggle) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }

    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            navMenu.classList.remove('active');
        });
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const element = document.querySelector(href);
                if (element) {
                    element.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
}

// ============================================
// SCROLL ANIMATIONS
// ============================================

function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease-out forwards';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const animatedElements = document.querySelectorAll(
        '.feature-card, .step, .stat-item'
    );

    animatedElements.forEach(el => {
        el.style.opacity = '0';
        observer.observe(el);
    });

    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    `;
    document.head.appendChild(style);
}

// ============================================
// BUTTON INTERACTIONS
// ============================================

function initButtonInteractions() {
    const buttons = document.querySelectorAll('.btn');

    buttons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            createRipple(e, this);
        });
    });
}

function createRipple(e, button) {
    if (!button.classList.contains('btn-primary') && 
        !button.classList.contains('btn-secondary') &&
        !button.classList.contains('btn-outline')) {
        return;
    }

    const rect = button.getBoundingClientRect();
    const ripple = document.createElement('span');
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;

    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');

    const existingRipple = button.querySelector('.ripple');
    if (existingRipple) {
        existingRipple.remove();
    }

    button.appendChild(ripple);
}

// ============================================
// STATS COUNTER
// ============================================

function initStatsCounter() {
    const stats = document.querySelectorAll('.stat-number');
    const observed = new Set();

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !observed.has(entry.target)) {
                observed.add(entry.target);
                const target = entry.target;
                const finalValue = target.textContent;
                animateCounter(target, finalValue);
            }
        });
    }, { threshold: 0.5 });

    stats.forEach(stat => observer.observe(stat));
}

function animateCounter(element, finalValue) {
    const isPercentage = finalValue.includes('%');
    const isDecimal = finalValue.includes('.');
    const isCurrency = finalValue.includes('$') || finalValue.includes('B') || finalValue.includes('K');

    let numStr = finalValue.replace(/[^0-9.]/g, '');
    const finalNum = parseFloat(numStr);
    const multiplier = finalValue.includes('K') ? 1000 : finalValue.includes('B') ? 1000000000 : 1;
    const displayMultiplier = finalValue.includes('K') ? 'K' : finalValue.includes('B') ? 'B' : '';

    let current = 0;
    const increment = finalNum / 50;
    const duration = 1500;
    const steps = 50;
    const stepDuration = duration / steps;

    const counter = setInterval(() => {
        current += increment;
        if (current >= finalNum) {
            current = finalNum;
            clearInterval(counter);
        }

        if (isPercentage) {
            element.textContent = current.toFixed(1) + '%';
        } else if (displayMultiplier) {
            element.textContent = '$' + current.toFixed(1) + displayMultiplier + '+';
        } else if (isCurrency) {
            element.textContent = current.toLocaleString();
        } else {
            element.textContent = current.toLocaleString() + displayMultiplier;
        }
    }, stepDuration);
}

// ============================================
// MODAL / DEMO VIDEO
// ============================================

function initDemoVideo() {
    const demoBtn = document.querySelector('button[class*="secondary"]');
    if (!demoBtn || demoBtn.textContent !== 'Watch Demo') return;

    demoBtn.addEventListener('click', () => {
        showDemoModal();
    });
}

function showDemoModal() {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <button class="modal-close">&times;</button>
            <div class="modal-video">
                <iframe width="100%" height="500" src="https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
            </div>
        </div>
    `;

    const style = document.createElement('style');
    style.textContent = `
        .modal {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            animation: fadeIn 0.3s ease-out;
        }

        .modal-content {
            background: white;
            border-radius: 12px;
            max-width: 800px;
            width: 90%;
            position: relative;
            overflow: hidden;
        }

        .modal-close {
            position: absolute;
            top: 16px;
            right: 16px;
            width: 40px;
            height: 40px;
            border: none;
            background: rgba(0, 0, 0, 0.1);
            border-radius: 50%;
            font-size: 24px;
            cursor: pointer;
            z-index: 10;
            transition: all 0.3s ease;
        }

        .modal-close:hover {
            background: rgba(0, 0, 0, 0.2);
        }

        .modal-video {
            position: relative;
            padding-bottom: 56.25%;
            height: 0;
            overflow: hidden;
        }

        .modal-video iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }
    `;

    document.head.appendChild(style);
    document.body.appendChild(modal);

    const closeBtn = modal.querySelector('.modal-close');
    closeBtn.addEventListener('click', () => {
        modal.remove();
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// ============================================
// NAVBAR STICKY
// ============================================

function initStickyNavbar() {
    const navbar = document.querySelector('.navbar');
    let lastScrollTop = 0;

    window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

        if (scrollTop > 50) {
            navbar.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
        } else {
            navbar.style.boxShadow = '0 1px 2px 0 rgba(0, 0, 0, 0.05)';
        }

        lastScrollTop = scrollTop;
    });
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initScrollAnimations();
    initButtonInteractions();
    initStatsCounter();
    initDemoVideo();
    initStickyNavbar();

    console.log('Home page initialized');
});
