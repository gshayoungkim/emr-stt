import whisper
import os

class Transcriber:
    def __init__(self, model_name="base"):
        """
        Whisper 모델 초기화
        model_name 옵션: tiny, base, small, medium, large
        - tiny/base: 빠르지만 정확도 낮음
        - small: 균형잡힌 선택 (추천)
        - medium/large: 느리지만 정확도 높음
        """
        print(f"🔄 Whisper 모델 로딩 중... ({model_name})")
        self.model = whisper.load_model(model_name)
        print("✅ 모델 로딩 완료\n")
    
    def transcribe(self, audio_file, language="ko"):
        """
        음성 파일을 텍스트로 변환
        language: ko (한국어), en (영어), None (자동감지)
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"오디오 파일을 찾을 수 없습니다: {audio_file}")
        
        print(f"🎯 음성 인식 시작: {audio_file}")
        
        # Whisper 실행
        result = self.model.transcribe(
            audio_file,
            language=language,
            fp16=False  # CPU 사용 시 False
        )
        
        text = result["text"]
        print(f"✅ 인식 완료!\n")
        print(f"📄 변환된 텍스트:\n{text}\n")
        
        return text
    
    def transcribe_with_timestamps(self, audio_file, language="ko"):
        """
        타임스탬프 포함 변환 (향후 화자 분리에 유용)
        """
        result = self.model.transcribe(
            audio_file,
            language=language,
            fp16=False,
            verbose=True  # 진행상황 표시
        )
        
        return {
            "text": result["text"],
            "segments": result["segments"]  # 각 문장별 시간 정보
        }
