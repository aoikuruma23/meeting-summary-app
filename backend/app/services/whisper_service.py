import openai
from typing import Optional
from app.core.config import settings

class WhisperService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def transcribe(self, audio_file_path: str) -> str:
        """音声ファイルを文字起こし"""
        try:
            with open(audio_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ja",  # 日本語
                    response_format="text"
                )
            
            return response
        
        except Exception as e:
            raise Exception(f"文字起こしに失敗しました: {str(e)}")
    
    async def transcribe_with_timestamps(self, audio_file_path: str) -> dict:
        """タイムスタンプ付きで文字起こし"""
        try:
            with open(audio_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ja",
                    response_format="verbose_json"
                )
            
            return response
        
        except Exception as e:
            raise Exception(f"タイムスタンプ付き文字起こしに失敗しました: {str(e)}")
    
    def estimate_tokens(self, audio_duration_seconds: float) -> int:
        """音声の長さからトークン数を推定"""
        # Whisperの概算: 1分あたり約150トークン
        estimated_tokens = int(audio_duration_seconds / 60 * 150)
        return estimated_tokens 