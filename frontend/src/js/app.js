const API_BASE = "http://localhost:8000/api/v1";
const AUDIO_BASE = "http://localhost:8000/audio";

let mediaRecorder;
let audioChunks = [];
let isRecording = false;

const recordBtn = document.getElementById('recordBtn');
const statusLabel = document.getElementById('statusLabel');
const transcriptContainer = document.getElementById('transcriptContainer');
const transcriptText = document.getElementById('transcriptText');
const responseContainer = document.getElementById('responseContainer');
const responseText = document.getElementById('responseText');
const audioPlayer = document.getElementById('audioPlayer');
const sourcesToggle = document.getElementById('sourcesToggle');
const sourcesList = document.getElementById('sourcesList');

// Recording Logic
recordBtn.addEventListener('click', async () => {
    if (!isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
});

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            sendAudioToBackend(audioBlob);
        };

        mediaRecorder.start();
        isRecording = true;
        recordBtn.classList.add('recording');
        statusLabel.innerText = "I'm listening...";
        statusLabel.style.color = "#ef4444";
    } catch (err) {
        console.error("Error accessing microphone:", err);
        statusLabel.innerText = "Error: Allow microphone access.";
    }
}

function stopRecording() {
    mediaRecorder.stop();
    isRecording = false;
    recordBtn.classList.remove('recording');
    statusLabel.innerText = "Processing context...";
    statusLabel.style.color = "#94a3b8";
}

async function sendAudioToBackend(blob) {
    const formData = new FormData();
    formData.append('audio', blob, 'recording.wav');
    formData.append('business_id', 1);

    try {
        const response = await fetch(`${API_BASE}/interaction`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        updateUI(data);
    } catch (err) {
        console.error("Error sending audio:", err);
        statusLabel.innerText = "Error: Backend unreachable.";
    }
}

function updateUI(data) {
    if (!data || data.detail) {
        statusLabel.innerText = "Error: " + (data?.detail || "Unknown backend error.");
        statusLabel.style.color = "#ef4444";
        return;
    }

    transcriptContainer.style.display = 'block';
    transcriptText.innerText = data.transcript || "No transcript available";

    responseContainer.style.display = 'block';
    responseText.innerText = data.response_text || "No response generated";

    if (data.audio_url) {
        // Construct clean URL
        const filename = data.audio_url.split('/').pop();
        const fullAudioUrl = `${AUDIO_BASE}/${filename}`;

        console.log("DEBUG: Playing audio from:", fullAudioUrl);
        audioPlayer.src = fullAudioUrl;
        audioPlayer.style.display = 'block'; // Show it for debugging

        audioPlayer.play().catch(e => {
            console.error("DEBUG: Auto-play failed:", e);
            statusLabel.innerText = "Click Play on the player to hear Nova.";
        });
    }

    if (data.sources && data.sources.length > 0) {
        sourcesToggle.style.display = 'block';
        sourcesList.innerHTML = data.sources.map(s => `<p style="margin-bottom: 8px;">"${s}"</p>`).join('');
    } else {
        sourcesToggle.style.display = 'none';
        sourcesList.innerHTML = '';
    }

    statusLabel.innerText = "Click to speak again";
}

// UI Controls
sourcesToggle.addEventListener('click', () => {
    const isHidden = sourcesList.style.display === 'none' || sourcesList.style.display === '';
    sourcesList.style.display = isHidden ? 'block' : 'none';
    sourcesToggle.innerText = isHidden ? 'Hide Sources' : 'Show Sources';
});

// Knowledge Upload
const uploadBtn = document.getElementById('uploadBtn');
const knowledgeUpload = document.getElementById('knowledgeUpload');
const uploadStatus = document.getElementById('uploadStatus');

uploadBtn.addEventListener('click', async () => {
    const file = knowledgeUpload.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('business_id', 1);

    uploadStatus.innerText = "Uploading...";

    try {
        const response = await fetch(`${API_BASE}/knowledge/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            uploadStatus.innerText = `Success: ${data.chunks_processed} chunks indexed.`;
            uploadStatus.style.color = "#10b981";
        } else {
            uploadStatus.innerText = `Upload failed: ${data.detail || 'Unknown error'}`;
            uploadStatus.style.color = "#ef4444";
        }
    } catch (err) {
        uploadStatus.innerText = "Upload failed: Server unreachable.";
        uploadStatus.style.color = "#ef4444";
    }
});
