//// Main JavaScript file for Solar CRM
//
//// Initialize tooltips
//document.addEventListener('DOMContentLoaded', function() {
//    // Enable Bootstrap tooltips
//    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
//    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
//        return new bootstrap.Tooltip(tooltipTriggerEl)
//    });
//
//    // Format currency inputs
//    const currencyInputs = document.querySelectorAll('input[data-type="currency"]');
//    currencyInputs.forEach(input => {
//        input.addEventListener('blur', function(e) {
//            let value = e.target.value.replace(/[^\d]/g, '');
//            if (value) {
//                e.target.value = '₹ ' + parseInt(value).toLocaleString('en-IN');
//            }
//        });
//    });
//});
//
//// AJAX form submission with HTMX
//document.body.addEventListener('htmx:afterRequest', function(evt) {
//    if (evt.detail.successful) {
//        // Show success message
//        showNotification('Success', 'Operation completed successfully', 'success');
//    } else {
//        // Show error message
//        showNotification('Error', 'Something went wrong', 'error');
//    }
//});
//
//// Notification system
//function showNotification(title, message, type = 'info') {
//    // You can implement a toast notification system here
//    console.log(`${type}: ${title} - ${message}`);
//}
//
//// Export functions for use in templates
//window.showNotification = showNotification;
//

// Main JavaScript file for Solar CRM

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Format currency inputs
    const currencyInputs = document.querySelectorAll('input[data-type="currency"]');
    currencyInputs.forEach(input => {
        input.addEventListener('blur', function(e) {
            let value = e.target.value.replace(/[^\d]/g, '');
            if (value) {
                e.target.value = '₹ ' + parseInt(value).toLocaleString('en-IN');
            }
        });
    });
});

// Notification system
function showNotification(title, message, type = 'info') {
    console.log(`${type}: ${title} - ${message}`);
}

// Export functions for use in templates
window.showNotification = showNotification;