from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # データベース設定
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./meeting_summary.db")
    
    # PostgreSQLの場合、URLを調整
    @property
    def database_url(self) -> str:
        if self.DATABASE_URL.startswith("postgres://"):
            return self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return self.DATABASE_URL
    
    # セキュリティ設定
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24時間（本番用）
    
    # OpenAI API設定
    OPENAI_API_KEY: Optional[str] = None
    
    # 暗号化設定
    ENCRYPTION_KEY: Optional[str] = None
    
    # レート制限設定
    RATE_LIMIT_MAX_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    
    # セキュリティレベル設定
    SECURITY_LEVEL: str = "medium"  # low, medium, high
    
    # ログ設定
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    SECURITY_LOG_FILE: str = "logs/security.log"
    PERFORMANCE_LOG_FILE: str = "logs/performance.log"
    
    # ファイル設定
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_AUDIO_TYPES: list = ["audio/wav", "audio/mp3", "audio/ogg", "audio/webm"]
    
    # Stripe設定
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # 課金設定
    FREE_TRIAL_DAYS: int = 31
    FREE_USAGE_LIMIT: int = 10
    MONTHLY_PRICE: int = 980  # 円
    
    # ダミーログイン設定
    DUMMY_LOGIN_ENABLED: bool = True  # 開発・テスト用
    
    class Config:
        env_file = ".env"

settings = Settings()

# デバッグ用：環境変数の確認
print(f"DEBUG: OPENAI_API_KEY設定確認 - Key exists: {bool(settings.OPENAI_API_KEY)}")
print(f"DEBUG: OPENAI_API_KEY長さ: {len(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else 0}") 