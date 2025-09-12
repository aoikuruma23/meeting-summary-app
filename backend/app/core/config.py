from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    # データベース設定
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./meeting_summary.db")
    
    # 個別データベース設定（Render用）
    DB_HOST: str = os.getenv("DB_HOST", "")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "postgres")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    
    # PostgreSQLの場合、URLを調整
    @property
    def database_url(self) -> str:
        # 個別設定がある場合は組み立て
        if self.DB_HOST and self.DB_USER and self.DB_PASSWORD:
            import urllib.parse
            password = urllib.parse.quote_plus(self.DB_PASSWORD)
            return f"postgresql://{self.DB_USER}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        
        # 従来のDATABASE_URLを使用
        if self.DATABASE_URL.startswith("postgres://"):
            return self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return self.DATABASE_URL
    
    # JWT設定
    SECRET_KEY: str = os.getenv("SECRET_KEY", "meeting-summary-app-secret-key-2025-super-secure-jwt-token-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OpenAI設定
    OPENAI_API_KEY: str = ""
    
    # Stripe設定
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_PRICE_ID: str = os.getenv("STRIPE_PRICE_ID", "")
    STRIPE_PORTAL_CONFIGURATION_ID: str = os.getenv("STRIPE_PORTAL_CONFIGURATION_ID", "")
    
    # 暗号化設定
    ENCRYPTION_KEY: str = "your-encryption-key-here"
    
    # Google OAuth設定
    # Google Cloud Consoleで取得したクライアントIDに置き換えてください
    # 1. https://console.cloud.google.com/ にアクセス
    # 2. プロジェクトを作成または選択
    # 3. 「APIとサービス」→「認証情報」でOAuth 2.0クライアントIDを作成
    # 4. 承認済みリダイレクトURI: http://localhost:3000/auth/callback, https://meeting-summary-app.onrender.com/auth/callback
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "your-google-client-id.apps.googleusercontent.com")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "your-google-client-secret")
    
    # LINE OAuth設定
    LINE_CHANNEL_ID: str = os.getenv("LINE_CHANNEL_ID", "2007873513")
    LINE_CHANNEL_SECRET: str = os.getenv("LINE_CHANNEL_SECRET", "")
    LINE_REDIRECT_URI: str = os.getenv("LINE_REDIRECT_URI", "https://meeting-summary-app.jibunkaikaku-lab.com")
    
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
    RATE_LIMIT_PER_MINUTE: int = 60
    
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
    MONTHLY_PRICE: str = "999"
    
    # 機能設定
    DUMMY_LOGIN_ENABLED: str = "true"
    
    # フロントエンド設定
    VITE_API_URL: str = os.getenv("VITE_API_URL", "")
    
    # Whisper設定
    WHISPER_MODEL: str = "base"
    
    class Config:
        env_file = ".env"

settings = Settings()

# デバッグ用：環境変数の確認
print(f"DEBUG: OPENAI_API_KEY設定確認 - Key exists: {bool(settings.OPENAI_API_KEY)}")
print(f"DEBUG: OPENAI_API_KEY長さ: {len(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else 0}")
print(f"DEBUG: GOOGLE_CLIENT_ID設定確認 - Key exists: {bool(settings.GOOGLE_CLIENT_ID)}")
# セキュリティのため、実際の値は出力しない
print(f"DEBUG: GOOGLE_CLIENT_ID設定済み: {settings.GOOGLE_CLIENT_ID != 'your-google-client-id.apps.googleusercontent.com'}") 