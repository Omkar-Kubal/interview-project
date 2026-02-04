/**
 * WebSocket Signals Module
 * Handles live signal streaming from backend
 */

let ws = null;
let signalCallbacks = [];

/**
 * Connect to live signal WebSocket
 * @param {Function} onSignal - Callback for signal updates
 */
function connectSignals(onSignal, candidateId = null) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    let url = `${protocol}//${window.location.host}/api/session/live`;
    if (candidateId) {
        url += `?candidate_id=${candidateId}`;
    }
    ws = new WebSocket(url);

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (onSignal) {
            onSignal(data);
        }
        signalCallbacks.forEach(cb => cb(data));
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
        console.log('WebSocket closed');
    };
}

/**
 * Add signal callback
 * @param {Function} callback 
 */
function addSignalCallback(callback) {
    signalCallbacks.push(callback);
}

/**
 * Disconnect WebSocket
 */
function disconnectSignals() {
    if (ws) {
        ws.close();
        ws = null;
    }
    signalCallbacks = [];
}

/**
 * Check if WebSocket is connected
 * @returns {boolean}
 */
function isConnected() {
    return ws !== null && ws.readyState === WebSocket.OPEN;
}
