const API_URL = 'http://localhost:8000';

const state = {
    identity: null,
    status: null,
    history: [],
    isThinking: false,
    visionCount: 0,
};

// DOM Elements
const terminalOutput = document.getElementById('terminal-output');
const userInput = document.getElementById('user-input');
const uptimeEl = document.getElementById('uptime');
const memoryCountEl = document.getElementById('memory-count');
const visionCountEl = document.getElementById('vision-count');
const actionLogEl = document.getElementById('action-log');
const stateBadgeEl = document.getElementById('soul-state');
const lastActionEl = document.getElementById('last-action');
const currentToolEl = document.getElementById('current-tool');
const visionSummary = document.getElementById('vision-summary');

function addMessage(text, role) {
    const msg = document.createElement('div');
    msg.className = `msg ${role}`;
    msg.textContent = text;
    terminalOutput.appendChild(msg);
    terminalOutput.scrollTop = terminalOutput.scrollHeight;
}

function setAvatar(stateName) {
    if (typeof setAvatarState === 'function') {
        setAvatarState(stateName);
    }
}

async function fetchIdentity() {
    try {
        const res = await fetch(`${API_URL}/identity`);
        const data = await res.json();
        state.identity = data;
        updateProfileUI();
    } catch (err) {
        console.error('Failed to fetch identity', err);
    }
}

function updateProfileUI() {
    if (!state.identity) return;
    document.getElementById('profile-name').textContent = state.identity.full_name;
    document.getElementById('profile-moniker').textContent = state.identity.moniker;
    document.getElementById('profile-focus').textContent = state.identity.focus;
}

async function fetchStatus() {
    try {
        const res = await fetch(`${API_URL}/status`);
        const data = await res.json();
        state.status = data;
        updateStatusUI();
    } catch (err) {
        console.error('Failed to fetch status', err);
    }
}

function updateStatusUI() {
    if (!state.status) return;
    uptimeEl.textContent = state.status.uptime || '00:00:00';
    memoryCountEl.textContent = state.status.memories || '0';
    visionCountEl.textContent = state.visionCount;
}

async function handleSendMessage() {
    const text = userInput.value.trim();
    if (!text || state.isThinking) return;

    userInput.value = '';
    addMessage(text, 'user');

    state.isThinking = true;
    setAvatar('thinking');
    const thinkingMsg = document.createElement('div');
    thinkingMsg.className = 'msg bot thinking';
    thinkingMsg.textContent = '...THINKING';
    terminalOutput.appendChild(thinkingMsg);
    terminalOutput.scrollTop = terminalOutput.scrollHeight;

    try {
        const res = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        const data = await res.json();

        terminalOutput.removeChild(thinkingMsg);
        addMessage(data.response, 'bot');
        setAvatar('speaking');
        setTimeout(() => setAvatar('idle'), 2000);
        fetchStatus();
    } catch (err) {
        terminalOutput.removeChild(thinkingMsg);
        addMessage('ERROR: CONNECTION TO SOUL INTERRUPTED.', 'bot');
        setAvatar('error');
        setTimeout(() => setAvatar('idle'), 3000);
    } finally {
        state.isThinking = false;
    }
}

async function captureScreen() {
    addMessage('SYSTEM: Capturing screen...', 'user');
    setAvatar('thinking');

    try {
        const res = await fetch(`${API_URL}/vision/capture`);
        const data = await res.json();

        if (data.text) {
            state.visionCount++;
            visionSummary.textContent = data.summary || data.text.substring(0, 200);
            addMessage(`SCREEN CAPTURED: ${data.text.substring(0, 100)}...`, 'bot');
        } else {
            addMessage('SCREEN: No text detected or capture failed.', 'bot');
        }
        setAvatar('idle');
    } catch (err) {
        addMessage('SCREEN CAPTURE FAILED: ' + err.message, 'bot');
        setAvatar('error');
        setTimeout(() => setAvatar('idle'), 2000);
    }
}

// Event Listeners
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSendMessage();
});

async function triggerScrub() {
    addMessage('SYSTEM: EXECUTING MEMORY SCRUB...', 'user');
    try {
        const res = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: '/tool shell python soul/memory_scrubber.py' })
        });
        addMessage('MEMORY SCRUB COMPLETE. HALLUCINATIONS PURGED.', 'bot');
    } catch (err) {
        addMessage('ERROR EXECUTING SCRUB.', 'bot');
    }
}

async function triggerAction(action) {
    userInput.value = action;
    handleSendMessage();
}

async function fetchState() {
    try {
        const res = await fetch(`${API_URL}/state`);
        const data = await res.json();

        stateBadgeEl.textContent = data.current_state;
        stateBadgeEl.className = `state-badge ${data.current_state}`;
        lastActionEl.textContent = data.last_action;
        currentToolEl.textContent = data.active_tool || 'IDLE';

        if (data.current_state !== 'IDLE' && !state.isThinking) {
            setAvatar('thinking');
        } else if (data.current_state === 'IDLE' && !state.isThinking) {
            setAvatar('idle');
        }
    } catch (err) {
        console.error('Failed to fetch state', err);
    }
}

async function fetchActions() {
    try {
        const res = await fetch(`${API_URL}/actions`);
        const actions = await res.json();

        actionLogEl.innerHTML = '';
        actions.forEach(action => {
            const div = document.createElement('div');
            div.className = 'action-item';
            div.textContent = action;
            actionLogEl.appendChild(div);
        });
    } catch (err) {
        console.error('Failed to fetch actions', err);
    }
}

// Start
fetchIdentity();
fetchStatus();
fetchState();
fetchActions();
setInterval(fetchStatus, 5000);
setInterval(fetchState, 2000);
setInterval(fetchActions, 5000);

setTimeout(() => {
    addMessage('ANDILE SIZOPHILA DIGITAL TWIN ONLINE. I SEE, I THINK, I ACT.', 'bot');
}, 1000);
