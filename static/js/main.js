// Main JavaScript for the Lunch Ordering System

document.addEventListener('DOMContentLoaded', function() {
    // Handle lunch submission
    const lunchForm = document.getElementById('lunch-form');
    if (lunchForm) {
        lunchForm.addEventListener('submit', handleLunchSubmission);
    }

    // Handle logout button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            window.location.href = "{{ url_for('logout') }}";
        });
    }

    // Handle flash messages auto-dismiss
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.transition = 'opacity 0.5s';
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 500);
        }, 5000);
    });

    // Initialize tooltips
    const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
    tooltipTriggers.forEach(trigger => {
        new bootstrap.Tooltip(trigger);
    });
});

// Handle lunch form submission
async function handleLunchSubmission(e) {
    e.preventDefault();
    
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.innerHTML;
    
    try {
        // Disable button and show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
        
        const formData = new FormData(form);
        const response = await fetch(form.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                has_lunch: formData.get('has_lunch') === 'true',
                reason: formData.get('reason') || ''
            })
        });

        const data = await response.json();
        
        if (response.ok) {
            showNotification('Lunch preference updated successfully!', 'success');
            // Update UI to reflect the change
            updateLunchUI(formData.get('has_lunch') === 'true', formData.get('reason'));
        } else {
            throw new Error(data.message || 'Failed to update lunch preference');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification(error.message || 'An error occurred. Please try again.', 'error');
    } finally {
        // Re-enable button and restore original text
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-md shadow-lg text-white ${
        type === 'success' ? 'bg-green-500' : 
        type === 'error' ? 'bg-red-500' : 'bg-blue-500'
    }`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Auto-remove notification after 5 seconds
    setTimeout(() => {
        notification.style.transition = 'opacity 0.5s';
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 500);
    }, 5000);
}

// Update UI after successful lunch submission
function updateLunchUI(hasLunch, reason = '') {
    const statusElement = document.getElementById('lunch-status');
    const reasonElement = document.getElementById('lunch-reason');
    const form = document.getElementById('lunch-form');
    
    if (statusElement) {
        statusElement.textContent = hasLunch ? 'Yes' : 'No';
        statusElement.className = `px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
            hasLunch ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`;
    }
    
    if (reasonElement) {
        reasonElement.textContent = hasLunch ? 'N/A' : (reason || 'No reason provided');
    }
    
    // Update form state
    if (form) {
        const yesBtn = form.querySelector('input[value="true"]');
        const noBtn = form.querySelector('input[value="false"]');
        const reasonField = form.querySelector('select[name="reason"]');
        
        if (hasLunch) {
            yesBtn.checked = true;
            if (reasonField) reasonField.disabled = true;
        } else {
            noBtn.checked = true;
            if (reasonField) {
                reasonField.disabled = false;
                reasonField.value = reason || '';
            }
        }
    }
}
