/**
 * Media Capture Module
 * Handles camera and microphone lifecycle
 */

let mediaStream = null;

/**
 * Start media capture (camera + microphone)
 * @param {HTMLVideoElement} videoElement - Video element to attach stream to
 * @returns {Promise<MediaStream>} The media stream
 */
async function startMediaCapture(videoElement) {
    try {
        console.log('Requesting camera and microphone access...');
        mediaStream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: true
        });

        if (videoElement) {
            videoElement.srcObject = mediaStream;
        }

        console.log('Media capture started successfully');
        return mediaStream;
    } catch (error) {
        console.error('Media access denied:', error);
        throw error;
    }
}

/**
 * Stop media capture
 * @param {HTMLVideoElement} videoElement - Video element to clear
 */
function stopMediaCapture(videoElement) {
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
        mediaStream = null;
    }

    if (videoElement) {
        videoElement.srcObject = null;
    }
}

/**
 * Check if media capture is active
 * @returns {boolean}
 */
function isMediaCaptureActive() {
    return mediaStream !== null && mediaStream.active;
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
            <p class="text-sm font-mono">Camera/Microphone access denied</p>
            <p class="text-xs text-white/60 mt-1">Please allow access and refresh the page</p>
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
