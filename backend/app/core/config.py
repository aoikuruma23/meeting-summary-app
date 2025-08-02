from pydantic_settings import BaseSettings
from typing import Optional
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
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    
    # LINE OAuth設定
    LINE_CHANNEL_ID: str = ""
    LINE_CHANNEL_SECRET: str = ""
    LINE_REDIRECT_URI: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()

# デバッグ用：環境変数の確認
print(f"DEBUG: OPENAI_API_KEY設定確認 - Key exists: {bool(settings.OPENAI_API_KEY)}")
print(f"DEBUG: OPENAI_API_KEY長さ: {len(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else 0}") 