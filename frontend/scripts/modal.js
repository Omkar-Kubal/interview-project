/**
 * Confirmation Modal Component
 * Enhancement #8: Confirmation dialogs for destructive actions
 */

// Modal state
let modalResolver = null;

/**
 * Create and show a confirmation modal
 * @param {Object} options - Modal options
 * @param {string} options.title - Modal title
 * @param {string} options.message - Modal message
 * @param {string} options.confirmText - Confirm button text
 * @param {string} options.cancelText - Cancel button text
 * @param {string} options.type - Modal type: 'warning', 'danger', 'info'
 * @returns {Promise<boolean>} - True if confirmed, false if cancelled
 */
function showConfirmModal(options = {}) {
    const {
        title = 'Confirm Action',
        message = 'Are you sure you want to proceed?',
        confirmText = 'Confirm',
        cancelText = 'Cancel',
        type = 'warning'
    } = options;

    // Remove any existing modal
    const existing = document.getElementById('confirm-modal');
    if (existing) existing.remove();

    // Color scheme based on type
    const colors = {
        warning: { bg: 'bg-yellow-50', border: 'border-yellow-500', btn: 'bg-yellow-500 hover:bg-yellow-600' },
        danger: { bg: 'bg-red-50', border: 'border-red-500', btn: 'bg-red-500 hover:bg-red-600' },
        info: { bg: 'bg-blue-50', border: 'border-blue-500', btn: 'bg-blue-500 hover:bg-blue-600' }
    };
    const scheme = colors[type] || colors.warning;

    // Create modal HTML
    const modal = document.createElement('div');
    modal.id = 'confirm-modal';
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center p-4';
    modal.innerHTML = `
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" onclick="closeConfirmModal(false)"></div>
        <div class="relative bg-white border-2 ${scheme.border} max-w-md w-full p-6 shadow-xl">
            <div class="flex items-start gap-4">
                <div class="flex-shrink-0 w-10 h-10 ${scheme.bg} ${scheme.border} border flex items-center justify-center">
                    <span class="material-symbols-outlined text-xl">warning</span>
                </div>
                <div class="flex-1">
                    <h3 class="text-sm font-mono font-bold uppercase tracking-wider mb-2">${title}</h3>
                    <p class="text-sm text-gray-600">${message}</p>
                </div>
            </div>
            <div class="flex gap-3 mt-6 justify-end">
                <button onclick="closeConfirmModal(false)" 
                    class="px-4 py-2 border border-black text-black text-xs font-mono uppercase hover:bg-gray-100 transition-colors">
                    ${cancelText}
                </button>
                <button onclick="closeConfirmModal(true)" 
                    class="px-4 py-2 ${scheme.btn} text-white text-xs font-mono uppercase transition-colors">
                    ${confirmText}
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Return a promise that resolves when modal closes
    return new Promise(resolve => {
        modalResolver = resolve;
    });
}

/**
 * Close the confirmation modal
 * @param {boolean} confirmed - Whether the user confirmed
 */
function closeConfirmModal(confirmed) {
    const modal = document.getElementById('confirm-modal');
    if (modal) {
        modal.remove();
    }
    if (modalResolver) {
        modalResolver(confirmed);
        modalResolver = null;
    }
}

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeConfirmModal(false);
    }
});
