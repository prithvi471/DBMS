// script.js

function showToast(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.style.background = type === 'success' ? '#22c55e' : '#ef4444';
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function openModal(modalId) {
    document.getElementById(modalId).style.display = 'flex';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

async function apiRequest(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: { 'Content-Type': 'application/json' }
    };
    if (body) {
        options.body = JSON.stringify(body);
    }
    try {
        const response = await fetch(endpoint, options);
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'API Error');
        if (method !== 'GET') showToast(data.message || 'Success', 'success');
        return data;
    } catch (err) {
        showToast(err.message, 'error');
        throw err;
    }
}

// Global modal closer
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}

// Utility to gather form data into a JSON object
function getFormData(formId) {
    const form = document.getElementById(formId);
    const fd = new FormData(form);
    const obj = {};
    fd.forEach((value, key) => { obj[key] = value });
    return obj;
}

// Re-usable form submitter
async function submitForm(endpoint, method, formId, callback) {
    const data = getFormData(formId);
    try {
        await apiRequest(endpoint, method, data);
        closeModal(document.getElementById(formId).closest('.modal').id);
        if (callback) callback();
    } catch(e) {}
}

const statusColors = {
    'PENDING': 'pending',
    'SHIPPED': 'shipped',
    'DELIVERED': 'delivered',
    'CANCELLED': 'cancelled',
    'IN_TRANSIT': 'in_transit',
    'DELAYED': 'delayed'
};

function getBadgeHTML(status) {
    const cls = statusColors[status?.toUpperCase()] || 'pending';
    return `<span class="badge ${cls}">${status}</span>`;
}
