/**
 * UI Utility Module
 * DOM manipulation and state updates
 */

/**
 * Format seconds to HH:MM:SS
 * @param {number} seconds 
 * @returns {string}
 */
function formatTime(seconds) {
    const h = Math.floor(seconds / 3600).toString().padStart(2, '0');
    const m = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${h}:${m}:${s}`;
}

/**
 * Update signal display elements
 * @param {Object} data - Signal data from WebSocket
 */
function updateSignalDisplay(data) {
    // Face
    const sigFace = document.getElementById('sig-face');
    const sigFaceDot = document.getElementById('sig-face-dot');
    if (sigFace) sigFace.textContent = data.face_detected ? 'Yes' : 'No';
    if (sigFaceDot) sigFaceDot.className = `w-2 h-2 rounded-full ${data.face_detected ? 'bg-green-500' : 'bg-gray-400'}`;

    // Eye
    const sigEye = document.getElementById('sig-eye');
    if (sigEye && data.eye_direction) {
        sigEye.textContent = data.eye_direction.charAt(0).toUpperCase() + data.eye_direction.slice(1);
    }

    // Head
    const sigHead = document.getElementById('sig-head');
    if (sigHead && data.head_movement) {
        sigHead.textContent = data.head_movement.charAt(0).toUpperCase() + data.head_movement.slice(1);
    }

    // Voice
    const sigVoice = document.getElementById('sig-voice');
    const sigVoiceDot = document.getElementById('sig-voice-dot');
    if (sigVoice) sigVoice.textContent = data.voice_activity === 'active' ? 'Active' : 'Silent';
    if (sigVoiceDot) sigVoiceDot.className = `w-2 h-2 rounded-full ${data.voice_activity === 'active' ? 'bg-green-500' : 'border border-gray-400 bg-transparent'}`;

    // Integrity
    if (data.integrity) {
        const intFace = document.getElementById('int-face');
        const intMulti = document.getElementById('int-multi');
        const intAudio = document.getElementById('int-audio');
        if (intFace) intFace.textContent = data.integrity.face_continuous ? 'Yes' : 'No';
        if (intMulti) intMulti.textContent = data.integrity.multiple_faces ? 'Yes' : 'No';
        if (intAudio) intAudio.textContent = data.integrity.audio_interruptions ? 'Yes' : 'No';
    }

    // Timer
    const timer = document.getElementById('timer');
    if (timer && data.elapsed_sec !== undefined) {
        timer.textContent = formatTime(data.elapsed_sec);
    }
}

/**
 * Store data in sessionStorage for cross-page access
 * @param {string} key 
 * @param {*} value 
 */
function storeSessionData(key, value) {
    sessionStorage.setItem(key, JSON.stringify(value));
}

/**
 * Get data from sessionStorage
 * @param {string} key 
 * @returns {*}
 */
function getSessionData(key) {
    const data = sessionStorage.getItem(key);
    return data ? JSON.parse(data) : null;
}

/**
 * Clear session data
 */
function clearSessionData() {
    sessionStorage.clear();
}

/**
 * Navigate to a page
 * @param {string} path 
 */
function navigateTo(path) {
    window.location.href = path;
}
