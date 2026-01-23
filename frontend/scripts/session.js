/**
 * Session API Module
 * Handles start/stop session calls
 */

/**
 * Start a new capture session
 * @param {string} candidateId - The candidate identifier
 * @returns {Promise<Object>} Session start result
 */
async function startSession(candidateId) {
    const response = await fetch('/api/session/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ candidate_id: candidateId })
    });

    if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to start session');
    }

    return response.json();
}

/**
 * Stop the current capture session
 * @returns {Promise<Object>} Session stop result
 */
async function stopSession() {
    const response = await fetch('/api/session/stop', {
        method: 'POST'
    });

    if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to stop session');
    }

    return response.json();
}

/**
 * Get session summary
 * @returns {Promise<Object>} Session summary data
 */
async function getSessionSummary() {
    const response = await fetch('/api/session/summary');

    if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to get summary');
    }

    return response.json();
}
