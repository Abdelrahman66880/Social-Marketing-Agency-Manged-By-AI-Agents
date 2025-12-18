/**
 * Common Header - Shared functionality for all dashboard pages
 * Handles the current user badge and logout.
 */

(function () {
    // Single source of truth for userId
    function getUserId() {
        return localStorage.getItem('userId');
    }

    function setCurrentUserBadge() {
        const currentUserBadge = document.getElementById('currentUserBadge');
        if (!currentUserBadge) return;

        const userId = getUserId();
        if (userId) {
            currentUserBadge.innerHTML = `User: <strong style="color:var(--primary)">${userId}</strong>`;
        } else {
            currentUserBadge.innerHTML = `No current user found. Please <a href="login">Login</a>.`;
        }
    }

    function initLogout() {
        const logoutBtn = document.querySelector('.btn-logout');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                localStorage.removeItem('accessToken');
                localStorage.removeItem('userId');
                window.location.href = 'login';
            });
        }
    }

    // Initialize on DOM load
    document.addEventListener('DOMContentLoaded', () => {
        setCurrentUserBadge();
        initLogout();
    });

    // Handle manual updates if needed
    window.updateSharedHeader = setCurrentUserBadge;
})();
