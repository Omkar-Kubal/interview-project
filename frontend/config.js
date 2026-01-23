/**
 * Signal Capture Frontend Configuration
 */
const CONFIG = {
    // API Base URL - adjust for production
    API_BASE: window.location.origin,

    // WebSocket protocol
    WS_PROTOCOL: window.location.protocol === 'https:' ? 'wss:' : 'ws:',

    // Signal refresh interval (ms)
    SIGNAL_INTERVAL: 200,

    // Pages
    PAGES: {
        LANDING: '/pages/index.html',
        CAPTURE: '/capture',
        SUMMARY: '/summary'
    }
};

// Freeze config to prevent accidental modification
Object.freeze(CONFIG);
Object.freeze(CONFIG.PAGES);
