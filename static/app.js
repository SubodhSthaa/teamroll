/**
 * TeamRoll Frontend JavaScript
 * Handles client-side interactions and API calls
 */

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// API helper functions
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Authentication functions
function logout() {
    // Clear client storage
    localStorage.clear();
    sessionStorage.clear();

    // Fire-and-forget logout API call so navigation is not blocked/canceled.
    fetch('/api/auth/logout', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
        keepalive: true
    }).catch((error) => {
        console.error('Logout API error:', error);
    });

    // Force hard redirect with cache busting
    window.location.href = '/login?logout=true&nocache=' + Date.now();
    return false;
}

async function checkAuth() {
    try {
        const response = await fetch('/api/auth/me');
        const data = await response.json();
        return data.success ? data.user : null;
    } catch (error) {
        return null;
    }
}

// Employee management functions
async function loadEmployees() {
    try {
        const data = await apiCall('/api/employees');
        return data;
    } catch (error) {
        console.error('Error loading employees:', error);
        return { success: false, message: error.message };
    }
}

async function addEmployee(employeeData) {
    try {
        const data = await apiCall('/api/employees', {
            method: 'POST',
            body: JSON.stringify(employeeData)
        });
        return data;
    } catch (error) {
        console.error('Error adding employee:', error);
        return { success: false, message: error.message };
    }
}

// Payroll management functions
async function loadPayrollData() {
    try {
        const data = await apiCall('/api/payroll');
        return data;
    } catch (error) {
        console.error('Error loading payroll data:', error);
        return { success: false, message: error.message };
    }
}

async function processPayroll(payrollData) {
    try {
        const data = await apiCall('/api/payroll/process', {
            method: 'POST',
            body: JSON.stringify(payrollData)
        });
        return data;
    } catch (error) {
        console.error('Error processing payroll:', error);
        return { success: false, message: error.message };
    }
}

// Form validation
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validateForm(formData) {
    const errors = [];
    
    if (!formData.first_name || formData.first_name.trim().length < 2) {
        errors.push('First name must be at least 2 characters');
    }
    
    if (!formData.last_name || formData.last_name.trim().length < 2) {
        errors.push('Last name must be at least 2 characters');
    }
    
    if (!validateEmail(formData.email)) {
        errors.push('Please enter a valid email address');
    }
    
    if (!formData.position || formData.position.trim().length < 2) {
        errors.push('Position must be specified');
    }
    
    if (!formData.base_salary || parseFloat(formData.base_salary) <= 0) {
        errors.push('Base salary must be greater than 0');
    }
    
    return errors;
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    // Set background color based on type
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Add CSS for notifications
const notificationStyles = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;

const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    console.log('TeamRoll application initialized');
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});