// analytics.js — separate sections for competitor and interaction analyses

(function () {
    const API_BASE_URL = window.API_BASE_URL || (window.location.origin.indexOf('http') === 0 ? window.location.origin : 'http://localhost:8000');

    function getUserIdFromCookie(name) {
        const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
        return v ? v.pop() : null;
    }

    let USER_ID = window.CURRENT_USER_ID || localStorage.getItem('CURRENT_USER_ID') || getUserIdFromCookie('user_id') || null;

    const PAGE_LIMIT = 10;
    let skipCompetitor = 0;
    let skipInteraction = 0;

    const competitorListEl = document.getElementById('competitorList');
    const interactionListEl = document.getElementById('interactionList');
    const insightsEl = document.getElementById('insightsContent');
    const currentUserBadge = document.getElementById('currentUserBadge');

    function setCurrentUserBadge() {
        if (USER_ID) {
            currentUserBadge.innerHTML = `User: <strong style="color:var(--primary)">${USER_ID}</strong>`;
        } else {
            currentUserBadge.innerHTML = `No current user found. Set <code>window.CURRENT_USER_ID</code> or store it in <code>localStorage.CURRENT_USER_ID</code>.`;
        }
    }

    setCurrentUserBadge();

    function isoToLocalString(iso) {
        try { return new Date(iso).toLocaleString(); }
        catch (e) { return iso; }
    }

    async function fetchCompetitor(limit = PAGE_LIMIT, skip = 0) {
        if (!USER_ID) return [];
        const url = `${API_BASE_URL}/analytics/users/${USER_ID}/analysis/competitor/${limit}/${skip}`;
        try {
            const r = await fetch(url);
            if (!r.ok) return [];
            return await r.json();
        } catch (e) {
            console.error('fetchCompetitor failed', e);
            return [];
        }
    }

    async function fetchInteraction(limit = PAGE_LIMIT, skip = 0) {
        if (!USER_ID) return [];
        const url = `${API_BASE_URL}/analytics/users/${USER_ID}/analysis/interaction/${limit}/${skip}`;
        try {
            const r = await fetch(url);
            if (!r.ok) return [];
            return await r.json();
        } catch (e) {
            console.error('fetchInteraction failed', e);
            return [];
        }
    }

    function renderList(container, items, emptyMessage) {
        container.innerHTML = '';
        if (!items || items.length === 0) {
            container.innerHTML = `<p style="color:var(--gray-600)">${emptyMessage}</p>`;
            return;
        }
        const frag = document.createDocumentFragment();
        items.forEach(item => {
            const card = document.createElement('div');
            card.className = 'analysis-card';
            card.style = 'border-left:3px solid var(--primary);padding:12px;margin-bottom:10px;border-radius:8px;background:var(--white);';
            const header = document.createElement('div');
            header.style = 'display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;';
            header.innerHTML = `<strong>${item.analysisType || 'analysis'}</strong><span style="color:var(--gray-600);font-size:13px">${isoToLocalString(item.createdAt)}</span>`;
            const content = document.createElement('div');
            content.innerText = item.content || '(no content)';
            content.style = 'margin-bottom:8px;color:var(--gray-800)';
            card.appendChild(header);
            card.appendChild(content);
            frag.appendChild(card);
        });
        container.appendChild(frag);
    }

    function renderInsights(competitorItems, interactionItems) {
        const totalCompetitor = competitorItems ? competitorItems.length : 0;
        const totalInteraction = interactionItems ? interactionItems.length : 0;
        const total = totalCompetitor + totalInteraction;
        const latestCompetitor = (competitorItems && competitorItems[0]) ? competitorItems[0] : null;
        const latestInteraction = (interactionItems && interactionItems[0]) ? interactionItems[0] : null;

        if (!total) {
            insightsEl.innerHTML = '<p style="color:var(--gray-600)">No data to show insights.</p>';
            return;
        }

        insightsEl.innerHTML = `
            <div style="display:flex;gap:16px;flex-wrap:wrap;">
                <div style="min-width:160px;">
                    <div class="stat-label">Total analyses (page)</div>
                    <div class="stat-value">${total}</div>
                </div>
                <div style="min-width:160px;">
                    <div class="stat-label">Competitor (page)</div>
                    <div class="stat-value">${totalCompetitor}</div>
                </div>
                <div style="min-width:160px;">
                    <div class="stat-label">Interaction (page)</div>
                    <div class="stat-value">${totalInteraction}</div>
                </div>
            </div>
            <div style="margin-top:12px;display:flex;gap:12px;flex-wrap:wrap;">
                ${latestCompetitor ? `<div style="min-width:280px;"><div class="card-title">Latest competitor</div><div style="padding:10px;border-radius:8px;border:1px solid var(--gray-100);background:var(--white)"><div style="display:flex;justify-content:space-between"><strong>${latestCompetitor.analysisType}</strong><span style="color:var(--gray-600)">${isoToLocalString(latestCompetitor.createdAt)}</span></div><div style="margin-top:8px;color:var(--gray-800)">${latestCompetitor.content || '(no content)'}</div></div></div>` : ''}
                ${latestInteraction ? `<div style="min-width:280px;"><div class="card-title">Latest interaction</div><div style="padding:10px;border-radius:8px;border:1px solid var(--gray-100);background:var(--white)"><div style="display:flex;justify-content:space-between"><strong>${latestInteraction.analysisType}</strong><span style="color:var(--gray-600)">${isoToLocalString(latestInteraction.createdAt)}</span></div><div style="margin-top:8px;color:var(--gray-800)">${latestInteraction.content || '(no content)'}</div></div></div>` : ''}
            </div>
        `;
    }

    async function loadInitial() {
        if (!USER_ID) {
            currentUserBadge.innerHTML = `No current user found. Set <code>window.CURRENT_USER_ID</code> and reload.`;
            return;
        }
        skipCompetitor = 0;
        skipInteraction = 0;

        const [competitorItems, interactionItems] = await Promise.all([
            fetchCompetitor(PAGE_LIMIT, skipCompetitor),
            fetchInteraction(PAGE_LIMIT, skipInteraction)
        ]);

        renderList(competitorListEl, competitorItems, 'No competitor analyses found.');
        renderList(interactionListEl, interactionItems, 'No interaction analyses found.');
        renderInsights(competitorItems, interactionItems);
    }

    async function loadMoreCompetitor() {
        skipCompetitor += PAGE_LIMIT;
        const items = await fetchCompetitor(PAGE_LIMIT, skipCompetitor);
        // append new items to existing list
        if (!items || items.length === 0) return;
        const existing = Array.from(competitorListEl.querySelectorAll('.analysis-card'));
        // if no existing items, render directly:
        if (existing.length === 0) {
            renderList(competitorListEl, items, 'No competitor analyses found.');
        } else {
            // append
            const frag = document.createDocumentFragment();
            items.forEach(item => {
                const card = document.createElement('div');
                card.className = 'analysis-card';
                card.style = 'border-left:3px solid var(--primary);padding:12px;margin-bottom:10px;border-radius:8px;background:var(--white);';
                const header = document.createElement('div');
                header.style = 'display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;';
                header.innerHTML = `<strong>${item.analysisType || 'analysis'}</strong><span style="color:var(--gray-600);font-size:13px">${isoToLocalString(item.createdAt)}</span>`;
                const content = document.createElement('div');
                content.innerText = item.content || '(no content)';
                content.style = 'margin-bottom:8px;color:var(--gray-800)';
                card.appendChild(header);
                card.appendChild(content);
                frag.appendChild(card);
            });
            competitorListEl.appendChild(frag);
        }
    }

    async function loadMoreInteraction() {
        skipInteraction += PAGE_LIMIT;
        const items = await fetchInteraction(PAGE_LIMIT, skipInteraction);
        if (!items || items.length === 0) return;
        const existing = Array.from(interactionListEl.querySelectorAll('.analysis-card'));
        if (existing.length === 0) {
            renderList(interactionListEl, items, 'No interaction analyses found.');
        } else {
            const frag = document.createDocumentFragment();
            items.forEach(item => {
                const card = document.createElement('div');
                card.className = 'analysis-card';
                card.style = 'border-left:3px solid var(--primary);padding:12px;margin-bottom:10px;border-radius:8px;background:var(--white);';
                const header = document.createElement('div');
                header.style = 'display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;';
                header.innerHTML = `<strong>${item.analysisType || 'analysis'}</strong><span style="color:var(--gray-600);font-size:13px">${isoToLocalString(item.createdAt)}</span>`;
                const content = document.createElement('div');
                content.innerText = item.content || '(no content)';
                content.style = 'margin-bottom:8px;color:var(--gray-800)';
                card.appendChild(header);
                card.appendChild(content);
                frag.appendChild(card);
            });
            interactionListEl.appendChild(frag);
        }
    }

    async function createAnalysis(type, content) {
        if (!USER_ID) throw new Error('No current user id');
        const payload = {
            analysisType: type,
            content: content || 'AI prompt to generate analysis',
            user_id: USER_ID
        };
        const url = `${API_BASE_URL}/analytics/analysis`;
        const resp = await fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        if (!resp.ok) throw new Error(await resp.text());
        return await resp.json();
    }

    // DOM wiring
    document.getElementById('createAnalysisForm').addEventListener('submit', async (ev) => {
        ev.preventDefault();
        const typeVal = document.getElementById('analysisType').value;
        const contentVal = document.getElementById('analysisContent').value.trim();
        const formMessage = document.getElementById('formMessage');

        if (!typeVal) {
            formMessage.innerText = 'Please select analysis type.';
            return;
        }
        if (!USER_ID) {
            formMessage.innerText = 'No current user set. Set window.CURRENT_USER_ID or store in localStorage.';
            return;
        }
        formMessage.innerText = 'Creating analysis...';
        try {
            await createAnalysis(typeVal, contentVal);
            formMessage.innerText = 'Created successfully.';
            // reload both lists from start to show new item
            await loadInitial();
        } catch (e) {
            console.error(e);
            formMessage.innerText = 'Create failed: ' + (e.message || e);
        }
    });

    document.getElementById('clearForm').addEventListener('click', () => {
        document.getElementById('analysisType').value = '';
        document.getElementById('analysisContent').value = '';
    });

    document.getElementById('loadMoreCompetitor').addEventListener('click', loadMoreCompetitor);
    document.getElementById('loadMoreInteraction').addEventListener('click', loadMoreInteraction);

    // Auto-load if user id known
    if (USER_ID) {
        loadInitial();
    } else {
        setCurrentUserBadge();
    }

    // helper to set user from console
    window.__analytics_set_current_user = function (id, persist = false) {
        USER_ID = id;
        if (persist) localStorage.setItem('CURRENT_USER_ID', id);
        setCurrentUserBadge();
        loadInitial();
    };
})();