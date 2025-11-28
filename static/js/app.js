// ==================== 실시간 녹음 기능 ====================

let mediaRecorder = null;
let audioChunks = [];
let recordingStartTime = null;
let recordingInterval = null;
let audioContext = null;
let analyser = null;
let visualizerAnimationId = null;

// 탭 전환
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const tabName = e.target.dataset.tab;
        
        // 탭 버튼 활성화
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        
        // 탭 콘텐츠 표시
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName + 'Tab').classList.add('active');
        
        // ✅ 수정 1: 탭 전환 시 상태 메시지 초기화
        document.getElementById('uploadStatus').style.display = 'none';
        document.getElementById('uploadStatus').textContent = '';
        document.getElementById('uploadStatus').className = 'status';
    });
});

// 녹음 시작
document.getElementById('startRecordBtn').addEventListener('click', async () => {
    try {
        // ✅ 수정 1: 녹음 시작 전 상태 메시지 초기화
        document.getElementById('uploadStatus').style.display = 'none';
        
        // 마이크 권한 요청
        const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true,
                sampleRate: 16000
            } 
        });
        
        // MIME 타입 확인
        let mimeType = 'audio/webm;codecs=opus';
        if (!MediaRecorder.isTypeSupported(mimeType)) {
            mimeType = 'audio/webm';
        }
        
        // MediaRecorder 초기화
        mediaRecorder = new MediaRecorder(stream, { mimeType });
        
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };
        
        mediaRecorder.onstop = () => {
            // 녹음된 오디오 Blob 생성
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            const audioUrl = URL.createObjectURL(audioBlob);
            
            // 오디오 플레이어 표시
            const recordedAudio = document.getElementById('recordedAudio');
            recordedAudio.src = audioUrl;
            document.getElementById('recordedAudioContainer').style.display = 'block';
            
            // 녹음된 Blob을 전역 변수로 저장
            window.recordedAudioBlob = audioBlob;
            
            // 스트림 정지
            stream.getTracks().forEach(track => track.stop());
            
            // 비주얼라이저 정리
            stopVisualizer();
        };
        
        // 녹음 시작
        mediaRecorder.start(100);
        
        // UI 업데이트
        document.getElementById('startRecordBtn').disabled = true;
        document.getElementById('stopRecordBtn').disabled = false;
        
        // 타이머 시작
        recordingStartTime = Date.now();
        updateRecordingTime();
        recordingInterval = setInterval(updateRecordingTime, 1000);
        
        // 비주얼라이저 시작
        startVisualizer(stream);
        
        showStatus('uploadStatus', '🎤 녹음 중...', 'loading');
        
    } catch (error) {
        console.error('녹음 시작 실패:', error);
        
        // ✅ 수정 3: 권한 거부 시 더 명확한 메시지
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
            showStatus('uploadStatus', '⚠️ 마이크 권한이 필요합니다. 브라우저 설정에서 마이크 권한을 허용해주세요.', 'error');
        } else {
            showStatus('uploadStatus', `❌ 녹음 시작 실패: ${error.message}`, 'error');
        }
    }
});

// 녹음 종료
document.getElementById('stopRecordBtn').addEventListener('click', () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        
        // UI 업데이트
        document.getElementById('startRecordBtn').disabled = false;
        document.getElementById('stopRecordBtn').disabled = true;
        
        // 타이머 정지
        clearInterval(recordingInterval);
        document.getElementById('recordingTime').textContent = '00:00';
        
        // ✅ 수정 1: 녹음 완료 시 상태를 성공으로만 표시 (에러 메시지 숨김)
        showStatus('uploadStatus', '✅ 녹음 완료!', 'success');
    }
});

// 녹음 시간 표시
function updateRecordingTime() {
    const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    document.getElementById('recordingTime').textContent = 
        `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

// 오디오 비주얼라이저
function startVisualizer(stream) {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaStreamSource(stream);
    
    source.connect(analyser);
    analyser.fftSize = 256;
    
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    
    const canvas = document.getElementById('visualizer');
    const canvasCtx = canvas.getContext('2d');
    
    function draw() {
        visualizerAnimationId = requestAnimationFrame(draw);
        
        analyser.getByteFrequencyData(dataArray);
        
        canvasCtx.fillStyle = '#f8f9fa';
        canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
        
        const barWidth = (canvas.width / bufferLength) * 2.5;
        let barHeight;
        let x = 0;
        
        for (let i = 0; i < bufferLength; i++) {
            barHeight = (dataArray[i] / 255) * canvas.height;
            
            const gradient = canvasCtx.createLinearGradient(0, canvas.height, 0, 0);
            gradient.addColorStop(0, '#667eea');
            gradient.addColorStop(1, '#764ba2');
            
            canvasCtx.fillStyle = gradient;
            canvasCtx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
            
            x += barWidth + 1;
        }
    }
    
    draw();
}

function stopVisualizer() {
    if (visualizerAnimationId) {
        cancelAnimationFrame(visualizerAnimationId);
    }
    if (audioContext) {
        audioContext.close();
    }
    
    const canvas = document.getElementById('visualizer');
    const canvasCtx = canvas.getContext('2d');
    canvasCtx.fillStyle = '#f8f9fa';
    canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
}

// 녹음된 오디오 처리
document.getElementById('processRecordedBtn').addEventListener('click', async () => {
    if (!window.recordedAudioBlob) {
        showStatus('uploadStatus', '❌ 녹음된 오디오가 없습니다.', 'error');
        return;
    }
    
    showStatus('uploadStatus', '업로드 중...', 'loading');
    
    const formData = new FormData();
    formData.append('audio', window.recordedAudioBlob, 'recording.webm');
    
    try {
        const uploadResponse = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!uploadResponse.ok) {
            const errorText = await uploadResponse.text();
            throw new Error(`업로드 실패 (${uploadResponse.status}): ${errorText}`);
        }
        
        const uploadData = await uploadResponse.json();
        
        if (!uploadData.success) {
            throw new Error(uploadData.error || '업로드 실패');
        }
        
        currentFilepath = uploadData.filepath;
        showStatus('uploadStatus', '음성 인식 중... (1-2분 소요)', 'loading');
        
        const transcribeResponse = await fetch('/api/transcribe', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({filepath: currentFilepath})
        });
        
        if (!transcribeResponse.ok) {
            const errorText = await transcribeResponse.text();
            throw new Error(`STT 실패 (${transcribeResponse.status}): ${errorText}`);
        }
        
        const transcribeData = await transcribeResponse.json();
        
        if (!transcribeData.success) {
            throw new Error(transcribeData.error || 'STT 처리 실패');
        }
        
        document.getElementById('transcript').value = transcribeData.transcript;
        document.getElementById('transcriptSection').style.display = 'block';
        showStatus('uploadStatus', '✅ 음성 인식 완료!', 'success');
        
        document.getElementById('transcriptSection').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        console.error('전체 오류:', error);
        showStatus('uploadStatus', `❌ 오류: ${error.message}`, 'error');
    }
});

// ==================== 파일 업로드 ====================
let currentFilepath = null;

document.getElementById('uploadBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById('audioFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showStatus('uploadStatus', '❌ 파일을 선택해주세요', 'error');
        return;
    }
    
    showStatus('uploadStatus', '업로드 중...', 'loading');
    
    const formData = new FormData();
    formData.append('audio', file);
    
    try {
        const uploadResponse = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!uploadResponse.ok) {
            throw new Error(`업로드 실패 (${uploadResponse.status})`);
        }
        
        const uploadData = await uploadResponse.json();
        
        if (!uploadData.success) {
            throw new Error(uploadData.error);
        }
        
        currentFilepath = uploadData.filepath;
        showStatus('uploadStatus', '음성 인식 중... (1-2분 소요)', 'loading');
        
        const transcribeResponse = await fetch('/api/transcribe', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({filepath: currentFilepath})
        });
        
        if (!transcribeResponse.ok) {
            throw new Error(`STT 실패 (${transcribeResponse.status})`);
        }
        
        const transcribeData = await transcribeResponse.json();
        
        if (!transcribeData.success) {
            throw new Error(transcribeData.error);
        }
        
        document.getElementById('transcript').value = transcribeData.transcript;
        document.getElementById('transcriptSection').style.display = 'block';
        showStatus('uploadStatus', '✅ 음성 인식 완료!', 'success');
        
    } catch (error) {
        console.error('전체 오류:', error);
        showStatus('uploadStatus', `❌ 오류: ${error.message}`, 'error');
    }
});

// ==================== SOAP 생성 ====================
document.getElementById('generateSoapBtn').addEventListener('click', async () => {
    const transcript = document.getElementById('transcript').value;
    const department = document.getElementById('department').value;
    
    if (!transcript) {
        alert('전사 텍스트가 없습니다');
        return;
    }
    
    // ✅ 수정 2: SOAP 생성 상태를 별도 영역에 표시
    showStatus('soapStatus', 'SOAP 노트 생성 중...', 'loading');
    
    try {
        const response = await fetch('/api/generate-soap', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({transcript, department})
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error);
        }
        
        document.getElementById('soapNote').value = data.soap_note;
        document.getElementById('soapSection').style.display = 'block';
        showStatus('soapStatus', '✅ SOAP 노트 생성 완료!', 'success');
        
    } catch (error) {
        showStatus('soapStatus', `❌ 오류: ${error.message}`, 'error');
    }
});

// 복사 기능
document.getElementById('copyBtn').addEventListener('click', () => {
    const soapNote = document.getElementById('soapNote');
    soapNote.select();
    document.execCommand('copy');
    alert('✅ 클립보드에 복사되었습니다!');
});

// 다운로드 기능
document.getElementById('downloadBtn').addEventListener('click', () => {
    const soapNote = document.getElementById('soapNote').value;
    const blob = new Blob([soapNote], {type: 'text/plain'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `SOAP_${new Date().toISOString().slice(0,10)}.txt`;
    a.click();
});

// 약물 검색 모달
document.getElementById('searchMedBtn').addEventListener('click', () => {
    document.getElementById('medModal').style.display = 'block';
});

document.querySelector('.close').addEventListener('click', () => {
    document.getElementById('medModal').style.display = 'none';
});

document.getElementById('searchBtn').addEventListener('click', async () => {
    const keyword = document.getElementById('medSearchInput').value;
    
    try {
        const response = await fetch('/api/medications/search', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({keyword})
        });
        
        const data = await response.json();
        
        const resultsDiv = document.getElementById('searchResults');
        resultsDiv.innerHTML = '';
        
        if (data.results.length === 0) {
            resultsDiv.innerHTML = '<p>검색 결과가 없습니다</p>';
            return;
        }
        
        data.results.forEach(med => {
            const div = document.createElement('div');
            div.className = 'med-item';
            div.textContent = med;
            div.onclick = () => {
                const soapNote = document.getElementById('soapNote');
                soapNote.value += `\n${med}`;
                alert('추가되었습니다!');
            };
            resultsDiv.appendChild(div);
        });
        
    } catch (error) {
        alert(`오류: ${error.message}`);
    }
});

// 상태 표시 함수
function showStatus(elementId, message, type) {
    const statusEl = document.getElementById(elementId);
    statusEl.textContent = message;
    statusEl.className = `status ${type}`;
    statusEl.style.display = 'block';
}
