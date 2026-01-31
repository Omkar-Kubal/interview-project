/**
 * Session API Module
 * Handles start/stop session calls
 */

/**
 * Start a new capture session
 * @param {string} candidateId - The candidate identifier
 * @param {number} [applicationId] - Optional job application ID
 * @returns {Promise<Object>} Session start result
 */
async function startSession(candidateId, applicationId = null) {
    const response = await fetch('/api/session/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            candidate_id: candidateId,
            application_id: applicationId
        })
    });

    if (!response.ok) {
        let errorMessage = 'Failed to start session';
        try {
            const data = await response.json();
            errorMessage = data.detail || errorMessage;
        } catch (e) {
            // Not a JSON response
            errorMessage = await response.text() || errorMessage;
        }
        throw new Error(errorMessage);
    }

    return response.json();
}

/**
 * Stop the current capture session
 * @returns {Promise<Object>} Session stop result
 */
async function stopSession(candidateId) {
    const response = await fetch(`/api/session/stop?candidate_id=${candidateId}`, {
        method: 'POST'
    });

    if (!response.ok) {
        let errorMessage = 'Failed to stop session';
        try {
            const data = await response.json();
            errorMessage = data.detail || errorMessage;
        } catch (e) {
            errorMessage = await response.text() || errorMessage;
        }
        throw new Error(errorMessage);
    }

    return response.json();
}

/**
 * Get session summary
 * @returns {Promise<Object>} Session summary data
 */
async function getSessionSummary(candidateId) {
    const response = await fetch(`/api/session/summary?candidate_id=${candidateId}`);

    if (!response.ok) {
        let errorMessage = 'Failed to get summary';
        try {
            const data = await response.json();
            errorMessage = data.detail || errorMessage;
        } catch (e) {
            errorMessage = await response.text() || errorMessage;
        }
        throw new Error(errorMessage);
    }

    return response.json();
}
/**
 * Send a heartbeat to keep the session alive
 * @param {string} candidateId 
 */
async function sendHeartbeat(candidateId) {
    try {
        await fetch(`/api/session/heartbeat?candidate_id=${candidateId}`, { method: 'POST' });
    } catch (e) {
        console.error('Heartbeat failed', e);
    }
}

let heartbeatInterval = null;

function startHeartbeat(candidateId) {
    stopHeartbeat();
    heartbeatInterval = setInterval(() => sendHeartbeat(candidateId), 20000); // Pulse every 20s
}

function stopHeartbeat() {
    if (heartbeatInterval) {
        clearInterval(heartbeatInterval);
        heartbeatInterval = null;
    }
}
