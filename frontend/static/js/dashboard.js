/**
 * Dashboard Page - JavaScript
 * Handles dashboard interactions and navigation
 */

// ============================================
// SIDEBAR NAVIGATION
// ============================================

function initSidebarNavigation() {
    const navItems = document.querySelectorAll('.nav-item');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            // Remove active class from all items
            navItems.forEach(i => i.classList.remove('active'));
            // Add active class to clicked item
            item.classList.add('active');

            // Prevent default navigation for demo
            if (item.getAttribute('href') === '#') {
                e.preventDefault();
            }
        });
    });
}

// ============================================
// LOGOUT
// ============================================

function initLogout() {
    const logoutBtn = document.querySelector('.btn-logout');
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to logout?')) {
                showNotification('Logging out...', 'info');
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 1000);
            }
        });
    }
}

// ============================================
// SEARCH FUNCTIONALITY
// ============================================

function initSearch() {
    const searchInput = document.querySelector('.search-input');

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            // Implement search functionality
            console.log('Searching for:', query);
        });
    }
}

// ============================================
// NOTIFICATION BUTTON
// ============================================

function initNotifications() {
    const notifBtn = document.querySelector('.btn-notification');

    if (notifBtn) {
        notifBtn.addEventListener('click', () => {
            showNotification('You have 3 new notifications', 'info');
        });
    }
}

// ============================================
// STATS CARDS
// ============================================

function initStatsCards() {
    const statCards = document.querySelectorAll('.stat-card');

    statCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-4px)';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
        });
    });
}

// ============================================
// CHART INTERACTION
// ============================================

function initChart() {
    const chartBars = document.querySelectorAll('.chart-bar');

    chartBars.forEach(bar => {
        bar.addEventListener('mouseenter', () => {
            bar.style.opacity = '0.8';
        });

        bar.addEventListener('mouseleave', () => {
            bar.style.opacity = '1';
        });

        // Show tooltip on hover (optional)
        bar.addEventListener('mouseover', (e) => {
            const height = bar.style.height;
            const value = parseInt(height) / 100 * 1000; // Sample calculation
            bar.title = `Value: ${Math.round(value)}`;
        });
    });
}

// ============================================
// POST ACTIONS
// ============================================

function initPostActions() {
    const postItems = document.querySelectorAll('.post-item');

    postItems.forEach(item => {
        const statsDiv = item.querySelector('.post-stats');
        if (statsDiv) {
            statsDiv.style.cursor = 'pointer';
            statsDiv.addEventListener('click', () => {
                showNotification('Post details not yet implemented', 'info');
            });
        }
    });
}

// ============================================
// SELECT FILTER
// ============================================

function initSelectFilter() {
    const selectFilter = document.querySelector('.select-filter');

    if (selectFilter) {
        selectFilter.addEventListener('change', (e) => {
            const value = e.target.value;
            console.log('Filter changed to:', value);
            showNotification(`Showing data for ${value}`, 'info');
        });
    }
}

// ============================================
// SCHEDULE NEW BUTTON
// ============================================

function initScheduleNewButton() {
    const btns = document.querySelectorAll('.card-header .btn-secondary');

    btns.forEach(btn => {
        if (btn.textContent.includes('Schedule New')) {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                showScheduleModal();
            });
        }

        if (btn.textContent.includes('View All')) {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                showNotification('View all posts feature coming soon', 'info');
            });
        }
    });
}

// ============================================
// MODALS
// ============================================

function showScheduleModal() {
    const modal = document.createElement('div');
    modal.className = 'schedule-modal';
    modal.innerHTML = `
        <div class="modal-overlay">
            <div class="modal">
                <div class="modal-header">
                    <h3>Schedule New Post</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>Post Content</label>
                        <textarea placeholder="What's on your mind?" rows="4" style="width: 100%; padding: 12px; border: 1px solid #E5E7EB; border-radius: 8px; font-family: inherit; font-size: 14px;"></textarea>
                    </div>
                    <div class="form-group">
                        <label>Schedule Date & Time</label>
                        <input type="datetime-local" style="width: 100%; padding: 12px; border: 1px solid #E5E7EB; border-radius: 8px; font-family: inherit; font-size: 14px;">
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-cancel">Cancel</button>
                    <button class="btn-schedule">Schedule Post</button>
                </div>
            </div>
        </div>
    `;

    if (!document.getElementById('modal-styles')) {
        const style = document.createElement('style');
        style.id = 'modal-styles';
        style.textContent = `
            .schedule-modal {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                z-index: 1000;
            }

            .modal-overlay {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .modal {
                background: white;
                border-radius: 12px;
                width: 90%;
                max-width: 500px;
                box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.15);
            }

            .modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 24px;
                border-bottom: 1px solid #E5E7EB;
            }

            .modal-header h3 {
                font-size: 18px;
                font-weight: 600;
                color: #111827;
                margin: 0;
            }

            .modal-close {
                width: 32px;
                height: 32px;
                border: none;
                background: transparent;
                font-size: 24px;
                cursor: pointer;
                color: #6B7280;
            }

            .modal-close:hover {
                color: #111827;
            }

            .modal-body {
                padding: 24px;
            }

            .form-group {
                margin-bottom: 16px;
            }

            .form-group:last-child {
                margin-bottom: 0;
            }

            .form-group label {
                display: block;
                font-size: 14px;
                font-weight: 600;
                color: #374151;
                margin-bottom: 8px;
            }

            .modal-footer {
                display: flex;
                gap: 12px;
                padding: 24px;
                border-top: 1px solid #E5E7EB;
                justify-content: flex-end;
            }

            .btn-cancel,
            .btn-schedule {
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                border: none;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .btn-cancel {
                background: #F3F4F6;
                color: #374151;
            }

            .btn-cancel:hover {
                background: #E5E7EB;
            }

            .btn-schedule {
                background: #2563EB;
                color: white;
            }

            .btn-schedule:hover {
                background: #1e40af;
            }
        `;
        document.head.appendChild(style);
    }

    document.body.appendChild(modal);

    const closeBtn = modal.querySelector('.modal-close');
    const cancelBtn = modal.querySelector('.btn-cancel');
    const scheduleBtn = modal.querySelector('.btn-schedule');
    const overlay = modal.querySelector('.modal-overlay');

    const closeModal = () => {
        modal.remove();
    };

    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            closeModal();
        }
    });

    scheduleBtn.addEventListener('click', () => {
        showNotification('Post scheduled successfully!', 'success');
        closeModal();
    });
}

// ============================================
// NOTIFICATIONS
// ============================================

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    if (!document.getElementById('notification-styles-dashboard')) {
        const style = document.createElement('style');
        style.id = 'notification-styles-dashboard';
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
    initSidebarNavigation();
    initLogout();
    initSearch();
    initNotifications();
    initStatsCards();
    initChart();
    initPostActions();
    initSelectFilter();
    initScheduleNewButton();

    console.log('Dashboard initialized');
});
