import os
from openai import OpenAI

class Transcriber:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    
    def transcribe(self, audio_path, language="ko"):
        with open(audio_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language
            )
        return transcript.text
