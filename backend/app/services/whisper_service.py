import openai
import os
from typing import Optional
from app.core.config import settings

class WhisperService:
    def __init__(self):
        print(f"DEBUG: OpenAI API Key設定確認 - Key exists: {bool(settings.OPENAI_API_KEY)}")
        print(f"DEBUG: OpenAI API Key長さ: {len(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else 0}")
        # APIキーから改行文字を除去
        api_key = settings.OPENAI_API_KEY.strip() if settings.OPENAI_API_KEY else None
        print(f"DEBUG: 修正後のAPI Key長さ: {len(api_key) if api_key else 0}")
        self.client = openai.OpenAI(api_key=api_key)
    
    async def transcribe(self, audio_file_path: str) -> str:
        """音声ファイルを文字起こし"""
        try:
            print(f"DEBUG: 文字起こし開始 - ファイル: {audio_file_path}")
            print(f"DEBUG: ファイル存在確認: {os.path.exists(audio_file_path)}")
            
            with open(audio_file_path, "rb") as audio_file:
                print(f"DEBUG: OpenAI API呼び出し開始")
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ja",  # 日本語
                    response_format="text"
                )
                print(f"DEBUG: OpenAI API呼び出し成功")
            
            return response
        
        except Exception as e:
            print(f"DEBUG: 文字起こしエラー詳細: {str(e)}")
            print(f"DEBUG: エラータイプ: {type(e).__name__}")
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