/**
 * Media Capture Module
 * Handles camera and microphone lifecycle
 */

let mediaStream = null;

/**
 * Start media capture (using MJPEG stream from backend)
 * @param {HTMLImageElement} imgElement - Image element to attach stream to
 */
async function startMediaCapture(imgElement) {
    try {
        console.log('Attaching to backend MJPEG stream...');

        // Point the image src to the MJPEG endpoint
        // Adding a timestamp to prevent caching
        if (imgElement) {
            imgElement.src = `/video_feed?t=${Date.now()}`;
        }

        console.log('Media stream attached successfully');
    } catch (error) {
        console.error('Failed to attach media stream:', error);
        throw error;
    }
}

/**
 * Stop media capture
 * @param {HTMLImageElement} imgElement - Image element to clear
 */
function stopMediaCapture(imgElement) {
    if (imgElement) {
        imgElement.src = '';
    }
}

/**
 * Check if media capture is active
 * @param {HTMLImageElement} imgElement
 * @returns {boolean}
 */
function isMediaCaptureActive(imgElement) {
    return imgElement && imgElement.src !== '';
}

/**
 * Show error overlay on video container
 * @param {HTMLElement} container - Container element
 */
function showMediaError(container) {
    const errorOverlay = document.createElement('div');
    errorOverlay.className = 'absolute inset-0 flex items-center justify-center bg-black/80';
    errorOverlay.id = 'media-error-overlay';
    errorOverlay.innerHTML = `
        <div class="text-center text-white p-6">
            <span class="material-symbols-outlined text-4xl mb-2">videocam_off</span>
            <p class="text-sm font-mono">Stream Connection Failed</p>
            <p class="text-xs text-white/60 mt-1">Make sure the backend is running and the session is started.</p>
        </div>
    `;
    container.appendChild(errorOverlay);
}

/**
 * Clear error overlay
 * @param {HTMLElement} container - Container element
 */
function clearMediaError(container) {
    const overlay = container.querySelector('#media-error-overlay');
    if (overlay) {
        overlay.remove();
    }
}
