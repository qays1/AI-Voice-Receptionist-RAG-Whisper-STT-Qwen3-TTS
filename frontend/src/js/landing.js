const API_BASE = 'http://localhost:8000/api/v1';

// State
let currentUser = JSON.parse(localStorage.getItem('user')) || null;
let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];
let audioContext = null;
let analyser = null;
let dataArray = null;
let animationId = null;

// DOM Elements
const loginOverlay = document.getElementById('loginOverlay');
const usernameInput = document.getElementById('usernameInput');
const loginBtn = document.getElementById('loginBtn');
const userDisplay = document.getElementById('userDisplay');
const logoutBtn = document.getElementById('logoutBtn');

const speakBtn = document.getElementById('speakBtn');
const conversationArea = document.getElementById('conversationArea');
const messageHistory = document.getElementById('messageHistory');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const audioPlayer = document.getElementById('audioPlayer');
const adminToggle = document.getElementById('adminToggle');
const adminContent = document.getElementById('adminContent');
const knowledgeUpload = document.getElementById('knowledgeUpload');
const uploadBtn = document.getElementById('uploadBtn');
const uploadStatus = document.getElementById('uploadStatus');
const avatarImage = document.getElementById('avatarImage');
const visualizer = document.getElementById('visualizer');
const vBars = document.querySelectorAll('.v-bar');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    setupEventListeners();
    loadAvatarImage();
});

function checkAuth() {
    if (currentUser) {
        loginOverlay.style.display = 'none';
        userDisplay.textContent = `Hello, ${currentUser.username}`;
        logoutBtn.style.display = 'block';
    } else {
        loginOverlay.style.display = 'flex';
        logoutBtn.style.display = 'none';
    }
}

function setupEventListeners() {
    loginBtn.addEventListener('click', handleLogin);
    usernameInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') handleLogin(); });
    logoutBtn.addEventListener('click', handleLogout);

    speakBtn.addEventListener('click', handleSpeakClick);
    adminToggle.addEventListener('click', toggleAdmin);
    uploadBtn.addEventListener('click', handleUpload);
    sendBtn.addEventListener('click', handleChatSubmit);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleChatSubmit();
    });
}

async function handleLogin() {
    const username = usernameInput.value.trim();
    if (!username) return;

    const fd = new FormData();
    fd.append('username', username);

    try {
        const res = await fetch(`${API_BASE}/login`, { method: 'POST', body: fd });
        const data = await res.json();
        currentUser = data;
        localStorage.setItem('user', JSON.stringify(data));
        checkAuth();
    } catch (err) {
        alert('Login failed. Please try again.');
    }
}

function handleLogout() {
    localStorage.removeItem('user');
    currentUser = null;
    checkAuth();
    window.location.reload();
}

function loadAvatarImage() {
    avatarImage.src = 'src/images/receptionist-avatar.png';
}

// --- Voice ---

async function handleSpeakClick() {
    if (!isRecording) await startRecording();
    else await stopRecording();
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const sc = audioContext.createMediaStreamSource(stream);
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 64;
        sc.connect(analyser);
        dataArray = new Uint8Array(analyser.frequencyBinCount);

        visualizer.style.display = 'flex';
        animateV();

        mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
        mediaRecorder.onstop = async () => {
            const blob = new Blob(audioChunks, { type: 'audio/wav' });
            await sendAudio(blob);
            stream.getTracks().forEach(t => t.stop());
            if (audioContext) audioContext.close();
        };

        mediaRecorder.start();
        isRecording = true;
        speakBtn.querySelector('span').textContent = 'LISTENING...';
        avatarImage.classList.add('speaking');
    } catch (err) {
        console.error(err);
    }
}

function animateV() {
    if (!isRecording) return;
    animationId = requestAnimationFrame(animateV);
    analyser.getByteFrequencyData(dataArray);
    vBars.forEach((bar, idx) => {
        const val = dataArray[idx] || 0;
        const h = Math.max(4, (val / 255) * 35);
        bar.style.height = `${h}px`;
    });
}

async function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        visualizer.style.display = 'none';
        speakBtn.querySelector('span').textContent = 'SPEAK TO AN ASSISTANT';
        avatarImage.classList.remove('speaking');
    }
}

async function sendAudio(blob) {
    const fd = new FormData();
    fd.append('audio', blob, 'rec.wav');
    fd.append('user_id', currentUser.user_id);

    try {
        const res = await fetch(`${API_BASE}/interaction`, { method: 'POST', body: fd });
        const data = await res.json();
        addMessageToUI('user', data.transcript);
        addMessageToUI('assistant', data.response_text, data.sources, true);
        if (data.audio_url) playAudio(data.audio_url);
    } catch (err) {
        console.error(err);
    }
}

// --- Chat ---

async function handleChatSubmit() {
    const txt = chatInput.value.trim();
    if (!txt) return;
    chatInput.value = '';
    addMessageToUI('user', txt);

    try {
        const fd = new FormData();
        fd.append('text', txt);
        fd.append('user_id', currentUser.user_id);
        const res = await fetch(`${API_BASE}/chat`, { method: 'POST', body: fd });
        const data = await res.json();
        addMessageToUI('assistant', data.response_text, data.sources, true);
    } catch (err) {
        console.error(err);
    }
}

function addMessageToUI(role, text, sources = [], type = false) {
    const hint = document.getElementById('startHint');
    if (hint) hint.style.display = 'none';

    const row = document.createElement('div');
    row.className = `msg-row ${role}`;
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    row.appendChild(bubble);
    messageHistory.appendChild(row);

    if (type && role === 'assistant') {
        typeWriter(bubble, text, () => {
            if (sources && sources.length > 0) attachSources(row, sources);
            messageHistory.scrollTop = messageHistory.scrollHeight;
        });
    } else {
        bubble.textContent = text;
        if (sources && sources.length > 0) attachSources(row, sources);
    }
    messageHistory.scrollTop = messageHistory.scrollHeight;
}

function typeWriter(el, txt, cb) {
    let i = 0;
    const int = setInterval(() => {
        if (i < txt.length) {
            el.textContent += txt.charAt(i++);
            messageHistory.scrollTop = messageHistory.scrollHeight;
        } else {
            clearInterval(int);
            if (cb) cb();
        }
    }, 15);
}

function attachSources(parent, src) {
    const list = document.createElement('div');
    list.style.cssText = 'font-size: 0.75rem; color: #8b949e; margin-top: 8px; padding-top: 8px; border-top: 1px solid #30363d;';
    list.innerHTML = '<strong>Sources:</strong>' + src.map(s => `<div>• ${s.substring(0, 100)}...</div>`).join('');
    parent.querySelector('.bubble').appendChild(list);
}

function playAudio(url) {
    const fn = url.split('/').pop();
    audioPlayer.src = `http://localhost:8000/audio/${fn}`;
    audioPlayer.play();
    avatarImage.classList.add('speaking');
    audioPlayer.onended = () => avatarImage.classList.remove('speaking');
}

// --- Admin ---

async function toggleAdmin() {
    const isH = adminContent.style.display === 'none' || !adminContent.style.display;
    adminContent.style.display = isH ? 'block' : 'none';
}

async function handleUpload() {
    const f = knowledgeUpload.files[0];
    if (!f) return;
    const fd = new FormData();
    fd.append('file', f);
    fd.append('user_id', currentUser.user_id);
    uploadStatus.textContent = '⏳ Uploading...';
    try {
        const res = await fetch(`${API_BASE}/knowledge/upload`, { method: 'POST', body: fd });
        const d = await res.json();
        uploadStatus.textContent = `✅ Processed ${d.chunks_processed} chunks`;
    } catch (err) {
        uploadStatus.textContent = '❌ Upload failed';
    }
}
