// Business Setup Script

// Data store for tags
const formDataStore = {
    longTermGoals: [],
    shortTermGoals: [],
    targetAudience: [],
    differentiators: [],
    theme: [],
    businessKeyWords: []
};

// Initialize Tag Inputs
document.querySelectorAll('.tag-input').forEach(input => {
    const target = input.dataset.target;

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ',') {
            e.preventDefault();
            addTag(input, target);
        }
        if (e.key === 'Backspace' && input.value === '') {
            removeLastTag(target);
        }
    });

    input.addEventListener('blur', () => {
        if (input.value.trim()) {
            addTag(input, target);
        }
    });
});

function addTag(inputElement, targetKey) {
    const text = inputElement.value.trim();
    if (!text) return;

    // Prevent duplicates
    if (formDataStore[targetKey].includes(text)) {
        inputElement.value = '';
        return;
    }

    formDataStore[targetKey].push(text);
    renderTags(targetKey);
    inputElement.value = '';
}

function removeTag(targetKey, index) {
    formDataStore[targetKey].splice(index, 1);
    renderTags(targetKey);
}

function removeLastTag(targetKey) {
    if (formDataStore[targetKey].length > 0) {
        formDataStore[targetKey].pop();
        renderTags(targetKey);
    }
}

function renderTags(targetKey) {
    const container = document.getElementById(`${targetKey}Container`);
    // Keep the input, remove existing tags
    const existingTags = container.querySelectorAll('.tag');
    existingTags.forEach(t => t.remove());

    const input = container.querySelector('.tag-input');

    formDataStore[targetKey].forEach((text, index) => {
        const tag = document.createElement('div');
        tag.className = 'tag';
        tag.innerHTML = `
            ${text}
            <i onclick="removeTag('${targetKey}', ${index})">&times;</i>
        `;
        container.insertBefore(tag, input);
    });
}

// Global scope for onclick handler
window.removeTag = removeTag;


document.getElementById('businessSetupForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const form = e.target;
    const businessName = form.querySelector('input[name="businessName"]').value;
    const field = form.querySelector('input[name="field"]').value;
    const description = form.querySelector('textarea[name="description"]').value;

    const submitBtn = form.querySelector('.btn-signin');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>Saving...</span>';

    try {
        const token = localStorage.getItem('accessToken');
        const userId = localStorage.getItem('userId');

        if (!token || !userId) {
            throw new Error("Authentication failed. Please login again.");
        }

        const payload = {
            user_id: userId,
            businessName: businessName,
            field: field,
            description: description,
            // Include list data
            longTermGoals: formDataStore.longTermGoals,
            shortTermGoals: formDataStore.shortTermGoals,
            targetAudience: formDataStore.targetAudience,
            differentiators: formDataStore.differentiators,
            theme: formDataStore.theme,
            businessKeyWords: formDataStore.businessKeyWords
        };

        const response = await fetch('/business-info/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || data.signal || 'Failed to save business info');
        }

        // Success -> Redirect to Facebook Connect
        window.location.href = 'facebook_connect.html';

    } catch (error) {
        alert(error.message);
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
});
