from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    # データベース設定
    DATABASE_URL: str = "sqlite:///./meeting_summary.db"
    
    # PostgreSQLの場合、URLを調整
    @property
    def database_url(self) -> str:
        if self.DATABASE_URL.startswith("postgres://"):
            return self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return self.DATABASE_URL
    
    # JWT設定
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24時間
    
    # OpenAI設定
    OPENAI_API_KEY: str = ""
    
    # Stripe設定
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # 暗号化設定
    ENCRYPTION_KEY: str = "your-encryption-key-here"
    
    # Google OAuth設定
    # Google Cloud Consoleで取得したクライアントIDに置き換えてください
    # 1. https://console.cloud.google.com/ にアクセス
    # 2. プロジェクトを作成または選択
    # 3. 「APIとサービス」→「認証情報」でOAuth 2.0クライアントIDを作成
    # 4. 承認済みリダイレクトURI: http://localhost:3000/auth/callback, https://meeting-summary-app.onrender.com/auth/callback
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "666039610454-j9rujj1aqaotuidr8dt182blna6prugm.apps.googleusercontent.com")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "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")
    
    # LINE OAuth設定
    LINE_CHANNEL_ID: str = ""
    LINE_CHANNEL_SECRET: str = ""
    LINE_REDIRECT_URI: str = ""
    
    # ファイル設定
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    UPLOAD_DIR: str = "uploads"
    AUDIO_CHUNKS_DIR: str = "audio_chunks"
    SUMMARIES_DIR: str = "summaries"
    
    # 録音設定
    FREE_RECORDING_LIMIT: int = 30  # 分
    PREMIUM_RECORDING_LIMIT: int = 120  # 分
    
    # レート制限設定
    RATE_LIMIT_MAX_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    
    # ログ設定
    SECURITY_LEVEL: str = "standard"
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    SECURITY_LOG_FILE: str = "logs/security.log"
    PERFORMANCE_LOG_FILE: str = "logs/performance.log"
    
    # 音声ファイル設定
    ALLOWED_AUDIO_TYPES: str = '["audio/wav","audio/mp3","audio/m4a","audio/aac","audio/flac","audio/ogg","audio/webm"]'
    
    # 課金設定
    FREE_TRIAL_DAYS: str = "31"
    FREE_USAGE_LIMIT: str = "10"
    MONTHLY_PRICE: str = "980"
    
    # 機能設定
    DUMMY_LOGIN_ENABLED: str = "true"
    
    class Config:
        env_file = ".env"

settings = Settings()

# デバッグ用：環境変数の確認
print(f"DEBUG: OPENAI_API_KEY設定確認 - Key exists: {bool(settings.OPENAI_API_KEY)}")
print(f"DEBUG: OPENAI_API_KEY長さ: {len(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else 0}")
print(f"DEBUG: GOOGLE_CLIENT_ID設定確認 - Key exists: {bool(settings.GOOGLE_CLIENT_ID)}")
print(f"DEBUG: GOOGLE_CLIENT_ID値: {settings.GOOGLE_CLIENT_ID}") 