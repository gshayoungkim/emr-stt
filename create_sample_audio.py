# create_sample_audio.py
import numpy as np
import wave

def create_test_audio(filename="test_sample.wav", duration=5):
    """테스트용 무음 파일 생성"""
    RATE = 16000
    CHANNELS = 1
    
    # 무음 데이터 생성
    audio_data = np.zeros(RATE * duration, dtype=np.int16)
    
    # WAV 파일로 저장
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(audio_data.tobytes())
    
    print(f"✅ 테스트 파일 생성 완료: {filename}")

if __name__ == "__main__":
    create_test_audio()
