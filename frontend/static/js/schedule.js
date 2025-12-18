// schedule.js — manage schedule (posts, competitor analysis, interaction analysis)

(function () {
    const API_BASE_URL = window.API_BASE_URL || 'http://localhost:8000';

    function getUserIdFromCookie(name) {
        const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
        return v ? v.pop() : null;
    }

    let USER_ID = window.CURRENT_USER_ID || localStorage.getItem('userId') || getUserIdFromCookie('user_id') || null;

    // State
    let currentSchedule = null;
    let editingItemId = null;
    let editingItemType = null; // 'post', 'competitor', 'interaction'

    // DOM elements
    const postsList = document.getElementById('postsList');
    const competitorList = document.getElementById('competitorList');
    const interactionList = document.getElementById('interactionList');
    const itemModal = document.getElementById('itemModal');
    const currentUserBadge = document.getElementById('currentUserBadge');
    const saveMessage = document.getElementById('saveMessage');

    function setCurrentUserBadge() {
        if (USER_ID) {
            currentUserBadge.innerHTML = `User: <strong style="color:var(--primary)">${USER_ID}</strong>`;
        } else {
            currentUserBadge.innerHTML = `No current user. Set <code>window.CURRENT_USER_ID</code> and reload.`;
        }
    }

    setCurrentUserBadge();

    function dateToLocalString(iso) {
        try { return new Date(iso).toLocaleString(); }
        catch (e) { return iso; }
    }

    function dateToLocalDatetimeInput(iso) {
        try {
            const d = new Date(iso);
            return d.toISOString().slice(0, 16);
        } catch (e) { return ''; }
    }

    // API calls
    async function fetchSchedule() {
        if (!USER_ID) {
            console.warn('No user id');
            return null;
        }
        const url = `${API_BASE_URL}/schedule/users/${USER_ID}`;
        try {
            const r = await fetch(url);
            if (!r.ok) {
                if (r.status === 404) return {
                    user_id: USER_ID,
                    posts: [],
                    competitor_analysis: [],
                    interaction_analysis_dates: []
                };
                throw new Error(`${r.status}: ${await r.text()}`);
            }
            return await r.json();
        } catch (e) {
            console.error('fetchSchedule failed:', e);
            alert('Failed to fetch schedule: ' + e.message);
            return null;
        }
    }

    async function saveSchedule(schedule) {
        if (!USER_ID) {
            alert('No user id set');
            return false;
        }
        const url = `${API_BASE_URL}/schedule/users/${USER_ID}`;
        try {
            const r = await fetch(url, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(schedule)
            });
            if (!r.ok) {
                throw new Error(`${r.status}: ${await r.text()}`);
            }
            currentSchedule = await r.json();
            saveMessage.innerText = 'Schedule saved successfully!';
            setTimeout(() => { saveMessage.innerText = ''; }, 3000);
            return true;
        } catch (e) {
            console.error('saveSchedule failed:', e);
            alert('Failed to save schedule: ' + e.message);
            return false;
        }
    }

    // Render sections
    function renderSections() {
        const lists = {
            post: postsList,
            competitor: competitorList,
            interaction: interactionList
        };

        // Clear all lists
        Object.values(lists).forEach(list => {
            if (list) list.innerHTML = '';
        });

        if (!currentSchedule) {
            Object.values(lists).forEach(list => {
                if (list) list.innerHTML = '<div class="empty-state"><p>Error loading content.</p></div>';
            });
            return;
        }

        const items = {
            post: currentSchedule.posts || [],
            competitor: currentSchedule.competitor_analysis || [],
            interaction: currentSchedule.interaction_analysis_dates || []
        };

        Object.keys(items).forEach(type => {
            const listEl = lists[type];
            const data = items[type];

            if (!listEl) return;

            if (data.length === 0) {
                listEl.innerHTML = `<div class="empty-state" style="padding: 20px 0;"><p>No ${type}s scheduled.</p></div>`;
                return;
            }

            // Sort by date
            const sortedData = [...data].sort((a, b) => new Date(a.date) - new Date(b.date));

            sortedData.forEach(item => {
                const card = document.createElement('div');
                card.className = 'timeline-item';
                card.style.margin = '0 0 12px 0';
                card.style.padding = '12px';

                const header = document.createElement('div');
                header.className = 'timeline-item-header';

                const dateSpan = document.createElement('span');
                dateSpan.className = 'timeline-item-date';
                dateSpan.innerText = dateToLocalString(item.date);

                header.appendChild(dateSpan);

                const content = document.createElement('div');
                content.className = 'timeline-item-content';

                if (type === 'post') {
                    content.innerHTML = `<div><strong>Prompt:</strong> ${item.content}</div>`;
                    if (item.media_urls && item.media_urls.length > 0) {
                        content.innerHTML += `<div style="font-size:12px; color:var(--gray-500); margin-top:4px;">${item.media_urls.length} media attached</div>`;
                    }
                } else if (type === 'competitor') {
                    content.innerHTML = `<div><strong>Focus:</strong> ${item.analysis_focus}</div>`;
                } else {
                    content.innerHTML = `<div style="font-size:14px; color:var(--gray-600);">Interaction Analysis</div>`;
                }

                const actions = document.createElement('div');
                actions.className = 'timeline-item-actions';
                actions.style.marginTop = '8px';

                const editBtn = document.createElement('button');
                editBtn.className = 'btn-edit';
                editBtn.innerText = 'Edit';
                editBtn.addEventListener('click', () => openEditModal(type, item.id));

                const deleteBtn = document.createElement('button');
                deleteBtn.className = 'btn-delete';
                deleteBtn.innerText = 'Delete';
                deleteBtn.addEventListener('click', () => deleteItem(type, item.id));

                actions.appendChild(editBtn);
                actions.appendChild(deleteBtn);

                card.appendChild(header);
                card.appendChild(content);
                card.appendChild(actions);

                listEl.appendChild(card);
            });
        });
    }

    // Modal management
    function openModal(type) {
        editingItemType = type;
        editingItemId = null;

        // Hide all tabs, show selected
        document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
        document.getElementById(type + 'Tab').style.display = 'block';

        // Reset forms
        document.getElementById('postForm').reset();
        document.getElementById('competitorForm').reset();
        document.getElementById('interactionForm').reset();

        itemModal.classList.add('active');
    }

    function openEditModal(type, itemId) {
        editingItemType = type;
        editingItemId = itemId;

        const item = findItemById(type, itemId);
        if (!item) return;

        // Show modal and tab
        document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
        document.getElementById(type + 'Tab').style.display = 'block';

        // Populate form
        if (type === 'post') {
            document.getElementById('postDate').value = dateToLocalDatetimeInput(item.date);
            document.getElementById('postContent').value = item.content || '';
            document.getElementById('postMedia').value = (item.media_urls || []).join(', ');
        } else if (type === 'competitor') {
            document.getElementById('competitorDate').value = dateToLocalDatetimeInput(item.date);
            document.getElementById('competitorFocus').value = item.analysis_focus || '';
            document.getElementById('competitorKeywords').value = (item.keywords || []).join(', ');
        } else if (type === 'interaction') {
            document.getElementById('interactionDate').value = dateToLocalDatetimeInput(item.date);
        }

        itemModal.classList.add('active');
    }

    function closeModal() {
        itemModal.classList.remove('active');
        editingItemId = null;
        editingItemType = null;
    }

    function findItemById(type, id) {
        if (type === 'post') return currentSchedule.posts.find(p => p.id === id);
        if (type === 'competitor') return currentSchedule.competitor_analysis.find(c => c.id === id);
        if (type === 'interaction') return currentSchedule.interaction_analysis_dates.find(i => i.id === id);
    }

    function deleteItem(type, id) {
        if (!confirm('Delete this item?')) return;

        if (type === 'post') {
            currentSchedule.posts = currentSchedule.posts.filter(p => p.id !== id);
        } else if (type === 'competitor') {
            currentSchedule.competitor_analysis = currentSchedule.competitor_analysis.filter(c => c.id !== id);
        } else if (type === 'interaction') {
            currentSchedule.interaction_analysis_dates = currentSchedule.interaction_analysis_dates.filter(i => i.id !== id);
        }

        renderSections();
    }

    // Form submissions
    document.getElementById('postForm').addEventListener('submit', (e) => {
        e.preventDefault();
        const date = document.getElementById('postDate').value;
        const content = document.getElementById('postContent').value;
        const media = document.getElementById('postMedia').value.split(',').map(s => s.trim()).filter(s => s);

        if (!date || !content) {
            alert('Please fill in date and content');
            return;
        }

        const newPost = {
            id: editingItemId || `post_${Date.now()}`,
            date: new Date(date).toISOString(),
            content,
            media_urls: media
        };

        if (editingItemId) {
            const idx = currentSchedule.posts.findIndex(p => p.id === editingItemId);
            if (idx >= 0) currentSchedule.posts[idx] = newPost;
        } else {
            currentSchedule.posts.push(newPost);
        }

        renderSections();
        closeModal();
    });

    document.getElementById('competitorForm').addEventListener('submit', (e) => {
        e.preventDefault();
        const date = document.getElementById('competitorDate').value;
        const focus = document.getElementById('competitorFocus').value;
        const keywords = document.getElementById('competitorKeywords').value.split(',').map(s => s.trim()).filter(s => s);

        if (!date || !focus) {
            alert('Please fill in date and analysis focus');
            return;
        }

        const newCompetitor = {
            id: editingItemId || `comp_${Date.now()}`,
            date: new Date(date).toISOString(),
            analysis_focus: focus,
            keywords
        };

        if (editingItemId) {
            const idx = currentSchedule.competitor_analysis.findIndex(c => c.id === editingItemId);
            if (idx >= 0) currentSchedule.competitor_analysis[idx] = newCompetitor;
        } else {
            currentSchedule.competitor_analysis.push(newCompetitor);
        }

        renderSections();
        closeModal();
    });

    document.getElementById('interactionForm').addEventListener('submit', (e) => {
        e.preventDefault();
        const date = document.getElementById('interactionDate').value;

        if (!date) {
            alert('Please fill in date');
            return;
        }

        const newInteraction = {
            id: editingItemId || `int_${Date.now()}`,
            date: new Date(date).toISOString()
        };

        if (editingItemId) {
            const idx = currentSchedule.interaction_analysis_dates.findIndex(i => i.id === editingItemId);
            if (idx >= 0) currentSchedule.interaction_analysis_dates[idx] = newInteraction;
        } else {
            currentSchedule.interaction_analysis_dates.push(newInteraction);
        }

        renderSections();
        closeModal();
    });

    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const type = e.target.dataset.tab;
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
            e.target.classList.add('active');
            document.getElementById(type + 'Tab').style.display = 'block';
        });
    });

    // Modal controls
    document.getElementById('closeModal').addEventListener('click', closeModal);
    document.getElementById('cancelPostForm').addEventListener('click', closeModal);
    document.getElementById('cancelCompetitorForm').addEventListener('click', closeModal);
    document.getElementById('cancelInteractionForm').addEventListener('click', closeModal);

    // Quick add buttons
    document.getElementById('addPostBtn').addEventListener('click', () => openModal('post'));
    document.getElementById('addCompetitorBtn').addEventListener('click', () => openModal('competitor'));
    document.getElementById('addInteractionBtn').addEventListener('click', () => openModal('interaction'));

    // Save schedule
    document.getElementById('saveScheduleBtn').addEventListener('click', async () => {
        if (!currentSchedule) return;
        await saveSchedule(currentSchedule);
    });

    // Close modal on background click
    itemModal.addEventListener('click', (e) => {
        if (e.target === itemModal) closeModal();
    });

    // Initial load
    async function init() {
        if (!USER_ID) {
            const msg = '<div class="empty-state"><p>No user set. Set window.CURRENT_USER_ID and reload.</p></div>';
            if (postsList) postsList.innerHTML = msg;
            if (competitorList) competitorList.innerHTML = msg;
            if (interactionList) interactionList.innerHTML = msg;
            return;
        }
        const schedule = await fetchSchedule();
        if (schedule) {
            currentSchedule = schedule;
            renderSections();
        }
    }

    init();

    // Helper
    window.__schedule_set_user = function (id) {
        USER_ID = id;
        localStorage.setItem('userId', id);
        setCurrentUserBadge();
        init();
    };
})();