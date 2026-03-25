/**
 * Dynamic SVG Avatar for Andile Sizophila Mchunu.
 * Changes expression based on soul state.
 */

const AVATAR_STATES = {
    idle: {
        eyeSvg: `
            <circle cx="35" cy="45" r="5" fill="#222"/>
            <circle cx="65" cy="45" r="5" fill="#222"/>
            <circle cx="36" cy="43" r="2" fill="white"/>
            <circle cx="66" cy="43" r="2" fill="white"/>`,
        mouthSvg: '<line x1="40" y1="65" x2="60" y2="65" stroke="#333" stroke-width="2"/>',
        accent: '#7c3aed',
    },
    thinking: {
        eyeSvg: `
            <ellipse cx="35" cy="45" rx="5" ry="3" fill="#7c3aed"/>
            <ellipse cx="65" cy="45" rx="5" ry="3" fill="#7c3aed"/>
            <line x1="30" y1="38" x2="40" y2="40" stroke="#7c3aed" stroke-width="2"/>
            <line x1="60" y1="40" x2="70" y2="38" stroke="#7c3aed" stroke-width="2"/>`,
        mouthSvg: '<ellipse cx="50" cy="65" rx="6" ry="3" fill="#333"/>',
        accent: '#f59e0b',
    },
    speaking: {
        eyeSvg: `
            <circle cx="35" cy="45" r="5" fill="#222"/>
            <circle cx="65" cy="45" r="5" fill="#222"/>
            <circle cx="36" cy="43" r="2" fill="white"/>
            <circle cx="66" cy="43" r="2" fill="white"/>`,
        mouthSvg: '<ellipse cx="50" cy="65" rx="8" ry="5" fill="#333"><animate attributeName="ry" values="5;8;5" dur="0.3s" repeatCount="indefinite"/></ellipse>',
        accent: '#10b981',
    },
    happy: {
        eyeSvg: `
            <path d="M 30 45 Q 35 40 40 45" stroke="#222" stroke-width="2" fill="none"/>
            <path d="M 60 45 Q 65 40 70 45" stroke="#222" stroke-width="2" fill="none"/>`,
        mouthSvg: '<path d="M 38 62 Q 50 72 62 62" stroke="#333" stroke-width="2" fill="none"/>',
        accent: '#f59e0b',
    },
    error: {
        eyeSvg: `
            <line x1="30" y1="42" x2="40" y2="48" stroke="#ef4444" stroke-width="2"/>
            <line x1="40" y1="42" x2="30" y2="48" stroke="#ef4444" stroke-width="2"/>
            <line x1="60" y1="42" x2="70" y2="48" stroke="#ef4444" stroke-width="2"/>
            <line x1="70" y1="42" x2="60" y2="48" stroke="#ef4444" stroke-width="2"/>`,
        mouthSvg: '<path d="M 38 68 Q 50 60 62 68" stroke="#333" stroke-width="2" fill="none"/>',
        accent: '#ef4444',
    },
};

function generateAvatarSVG(state = 'idle') {
    const s = AVATAR_STATES[state] || AVATAR_STATES.idle;
    const skin = '#8B6914';
    const bg = '#1a1a2e';
    
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="200" height="200">
    <defs>
        <radialGradient id="glow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" style="stop-color:${s.accent};stop-opacity:0.3"/>
            <stop offset="100%" style="stop-color:${s.accent};stop-opacity:0"/>
        </radialGradient>
        <filter id="shadow">
            <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="${s.accent}" flood-opacity="0.5"/>
        </filter>
    </defs>
    <circle cx="50" cy="50" r="48" fill="url(#glow)"/>
    <ellipse cx="50" cy="50" rx="38" ry="42" fill="${bg}" stroke="${s.accent}" stroke-width="2" filter="url(#shadow)"/>
    <path d="M 15 35 Q 20 10 50 8 Q 80 10 85 35" fill="#1a1a1a"/>
    <path d="M 18 38 Q 22 25 50 20 Q 78 25 82 38" fill="#1a1a1a"/>
    <ellipse cx="50" cy="52" rx="32" ry="35" fill="${skin}"/>
    ${s.eyeSvg}
    <path d="M 50 50 L 47 58 L 53 58" stroke="${skin}" stroke-width="2" fill="none" opacity="0.5"/>
    ${s.mouthSvg}
    <ellipse cx="18" cy="50" rx="5" ry="8" fill="${skin}"/>
    <ellipse cx="82" cy="50" rx="5" ry="8" fill="${skin}"/>
    <circle cx="50" cy="50" r="46" fill="none" stroke="${s.accent}" stroke-width="1" stroke-dasharray="4 4" opacity="0.5">
        <animateTransform attributeName="transform" type="rotate" from="0 50 50" to="360 50 50" dur="10s" repeatCount="indefinite"/>
    </circle>
    <circle cx="50" cy="95" r="3" fill="${s.accent}">
        <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/>
    </circle>
</svg>`;
}

function setAvatarState(state) {
    const svg = generateAvatarSVG(state);
    const avatarContainer = document.getElementById('avatar-svg');
    if (avatarContainer) {
        avatarContainer.innerHTML = svg;
    }
    // Also update the class
    const avatar = document.querySelector('.avatar');
    if (avatar) {
        avatar.className = `avatar state-${state}`;
    }
}

// Initialize with idle state
document.addEventListener('DOMContentLoaded', () => {
    setAvatarState('idle');
});
