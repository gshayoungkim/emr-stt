import pyaudio
import wave
import os

class AudioRecorder:
    def __init__(self):
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1  # 모노
        self.RATE = 16000  # Whisper 권장 샘플레이트
        self.CHUNK = 1024
        self.audio = pyaudio.PyAudio()
        
    def record(self, filename="temp/recording.wav", duration=None):
        """
        음성 녹음 (Enter 키로 종료 또는 duration 초 후 자동 종료)
        """
        stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        print("🎤 녹음 시작! (Enter 키를 눌러 종료)")
        frames = []
        
        if duration:
            # 지정 시간만 녹음
            for i in range(0, int(self.RATE / self.CHUNK * duration)):
                data = stream.read(self.CHUNK)
                frames.append(data)
        else:
            # 수동 종료
            import threading
            stop_flag = threading.Event()
            
            def wait_for_enter():
                input()
                stop_flag.set()
            
            threading.Thread(target=wait_for_enter, daemon=True).start()
            
            while not stop_flag.is_set():
                data = stream.read(self.CHUNK)
                frames.append(data)
        
        print("⏹️  녹음 종료")
        stream.stop_stream()
        stream.close()
        
        # WAV 파일로 저장
        os.makedirs("temp", exist_ok=True)
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        return filename
    
    def cleanup(self):
        self.audio.terminate()
