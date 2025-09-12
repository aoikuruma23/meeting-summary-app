import os
from typing import Optional

# 環境変数を直接読み込むシンプルな設定
class Config:
    """シンプルな設定クラス"""
    
    # データベース設定
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./meeting_summary.db")
    DB_HOST = os.getenv("DB_HOST", "")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "postgres")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    
    # JWT設定
    SECRET_KEY = os.getenv("SECRET_KEY", "meeting-summary-app-secret-key-2025-super-secure-jwt-token-key")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # OpenAI設定
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Stripe設定
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "")
    STRIPE_PORTAL_CONFIGURATION_ID = os.getenv("STRIPE_PORTAL_CONFIGURATION_ID", "")
    
    # 暗号化設定
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "your-encryption-key-here")
    
    # Google OAuth設定
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your-google-client-id.apps.googleusercontent.com")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "your-google-client-secret")
    
    # LINE OAuth設定
    LINE_CHANNEL_ID = os.getenv("LINE_CHANNEL_ID", "2007873513")
    LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
    LINE_REDIRECT_URI = os.getenv("LINE_REDIRECT_URI", "https://meeting-summary-app.jibunkaikaku-lab.com")
    
    # ファイル設定
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    UPLOAD_DIR = "uploads"
    AUDIO_CHUNKS_DIR = "audio_chunks"
    SUMMARIES_DIR = "summaries"
    
    # 録音設定
    FREE_RECORDING_LIMIT = 30  # 分
    PREMIUM_RECORDING_LIMIT = 120  # 分
    
    # レート制限設定
    RATE_LIMIT_MAX_REQUESTS = 100
    RATE_LIMIT_WINDOW_SECONDS = 60
    RATE_LIMIT_PER_MINUTE = 60
    
    # ログ設定
    SECURITY_LEVEL = "standard"
    LOG_LEVEL = "INFO"
    LOG_FILE = "logs/app.log"
    SECURITY_LOG_FILE = "logs/security.log"
    PERFORMANCE_LOG_FILE = "logs/performance.log"
    
    # 音声ファイル設定
    ALLOWED_AUDIO_TYPES = '["audio/wav","audio/mp3","audio/m4a","audio/aac","audio/flac","audio/ogg","audio/webm"]'
    
    # 課金設定
    FREE_TRIAL_DAYS = "31"
    FREE_USAGE_LIMIT = "10"
    MONTHLY_PRICE = "999"
    
    # 機能設定
    DUMMY_LOGIN_ENABLED = "true"
    
    # フロントエンド設定
    VITE_API_URL = os.getenv("VITE_API_URL", "")
    
    # Whisper設定
    WHISPER_MODEL = "base"
    
    @property
    def database_url(self):
        """データベースURLを取得"""
        # 完全な接続文字列が設定されている場合は優先
        if self.DATABASE_URL and self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL
        
        # 個別設定がある場合は組み立て
        if self.DB_HOST and self.DB_USER and self.DB_PASSWORD:
            import urllib.parse
            password = urllib.parse.quote_plus(self.DB_PASSWORD)
            return f"postgresql://{self.DB_USER}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        
        # 従来のDATABASE_URLを使用
        if self.DATABASE_URL.startswith("postgres://"):
            return self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return self.DATABASE_URL

# 設定インスタンスを作成
settings = Config()

print("✅ 設定初期化成功")

# デバッグ用：環境変数の確認
try:
    print(f"DEBUG: OPENAI_API_KEY設定確認 - Key exists: {bool(settings.OPENAI_API_KEY)}")
    print(f"DEBUG: OPENAI_API_KEY長さ: {len(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else 0}")
    print(f"DEBUG: GOOGLE_CLIENT_ID設定確認 - Key exists: {bool(settings.GOOGLE_CLIENT_ID)}")
    print(f"DEBUG: GOOGLE_CLIENT_ID設定済み: {settings.GOOGLE_CLIENT_ID != 'your-google-client-id.apps.googleusercontent.com'}")
except Exception as e:
    print(f"⚠️ デバッグ出力エラー: {e}")