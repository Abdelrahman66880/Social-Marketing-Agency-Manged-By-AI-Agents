/**
 * Facebook Connect Script
 * Handles initialization of FB SDK, authentication, and page selection.
 */

const loginBtn = document.getElementById('fbLoginBtn');
const connectStep = document.getElementById('connectStep');
const pageSelectionStep = document.getElementById('pageSelectionStep');
const pageList = document.getElementById('pageList');
const confirmBtn = document.getElementById('confirmPageBtn');

let selectedPageId = null;
let selectedPageToken = null; // We might need to store this if we exchange the User Token for a Page Token here, 
// OR we send the User Token and Page ID to backend to do the exchange.
// Based on my backend analysis `exchange_token` takes a short_lived_token.
// Usually, we get a User Token, then query /me/accounts to get Page Tokens.
// The backend `exchange_token` seems designed to upgrade a token. 
// Let's see: `exchange_token` calls oauth/access_token with fb_exchange_token.
// This upgrades a User Token to Long-Lived User Token, OR a Page Token to Long-Lived Page Token.

// STRATEGY: 
// 1. Get User Token via FB.login
// 2. Use User Token to fetch pages (client side)
// 3. Select Page -> Get that Page's Access Token (which is short lived)
// 4. Send Page ID and Page's Short Lived Token to backend
// 5. Backend upgrades it to Long Lived Page Token and stores it.

// ============================================
// INITIALIZATION
// ============================================

async function initFacebook() {
    try {
        // Fetch config from backend
        const response = await fetch('/auth/config');
        if (!response.ok) throw new Error('Failed to load configuration');
        const config = await response.json();

        // Initialize FB SDK
        window.fbAsyncInit = function () {
            FB.init({
                appId: config.facebook_app_id,
                cookie: true,
                xfbml: true,
                version: config.api_version || 'v20.0'
            });

            // Check login status on load (optional, maybe auto-trigger?)
            // FB.getLoginStatus(function(response) {
            //     statusChangeCallback(response);
            // });
        };

        // Load SDK asynchronously
        (function (d, s, id) {
            var js, fjs = d.getElementsByTagName(s)[0];
            if (d.getElementById(id)) { return; }
            js = d.createElement(s); js.id = id;
            js.src = "https://connect.facebook.net/en_US/sdk.js";
            fjs.parentNode.insertBefore(js, fjs);
        }(document, 'script', 'facebook-jssdk'));

    } catch (error) {
        console.error("Setup Error:", error);
        alert("Failed to initialize Facebook connection. Please refresh.");
    }
}

initFacebook();

// ============================================
// HANDLERS
// ============================================

loginBtn.addEventListener('click', () => {
    // Determine info needed: 
    // pages_show_list, pages_read_engagement, pages_manage_posts, pages_manage_metadata
    // These permissions are needed to manage the page.
    // 'public_profile' and 'email' are default.

    FB.login(function (response) {
        if (response.authResponse) {
            console.log('Welcome!  Fetching your information.... ');
            const userAccessToken = response.authResponse.accessToken;
            fetchPages(userAccessToken);
        } else {
            console.log('User cancelled login or did not fully authorize.');
        }
    }, { scope: 'public_profile,pages_show_list,pages_read_engagement,pages_manage_posts,pages_manage_metadata' });
});

function fetchPages(userAccessToken) {
    FB.api('/me/accounts', function (response) {
        if (response && !response.error) {
            renderPageList(response.data);

            // Switch UI
            connectStep.style.display = 'none';
            pageSelectionStep.classList.add('active');
        } else {
            console.error('Error fetching pages:', response.error);
            alert('Failed to fetch your Facebook Pages.');
        }
    });
}

function renderPageList(pages) {
    pageList.innerHTML = '';

    if (pages.length === 0) {
        pageList.innerHTML = '<div style="padding:20px; text-align:center; color:#6B7280;">No Pages found for this account.</div>';
        return;
    }

    pages.forEach(page => {
        const item = document.createElement('div');
        item.className = 'page-item';
        item.innerHTML = `
            <div class="page-avatar"></div>
            <div class="page-name">${page.name}</div>
            <div style="font-size:12px; color:#9CA3AF; margin-left:auto;">${page.category || 'Page'}</div>
        `;

        item.addEventListener('click', () => {
            // Deselect others
            document.querySelectorAll('.page-item').forEach(el => el.classList.remove('selected'));
            item.classList.add('selected');

            selectedPageId = page.id;
            selectedPageToken = page.access_token; // This is the Page Access Token

            confirmBtn.style.display = 'inline-flex';
        });

        pageList.appendChild(item);
    });
}

confirmBtn.addEventListener('click', async () => {
    if (!selectedPageId || !selectedPageToken) return;

    confirmBtn.disabled = true;
    confirmBtn.innerHTML = 'Setting up...';

    try {
        const token = localStorage.getItem('accessToken'); // App JWT
        if (!token) throw new Error("Not authenticated with App. Please login again.");

        // Match backend expectation:
        // /facebook/auth/exchange expects: { short_lived_token, page_id }
        const payload = {
            short_lived_token: selectedPageToken,
            page_id: selectedPageId
        };

        const response = await fetch('/facebook/auth/exchange', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'Failed to exchange token');
        }

        // Success
        window.location.href = 'dashboard.html';

    } catch (error) {
        console.error("Token Exchange Error:", error);
        alert(error.message);
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = 'Confirm Selection';
    }
});
