import os
from typing import Optional, List

class Settings:
    """設定クラス（pydanticを使わない簡易版）"""
    def __init__(self):
        # データベース設定
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./meeting_summary.db")
        
        # 個別データベース設定（Render用）
        self.DB_HOST = os.getenv("DB_HOST", "")
        self.DB_PORT = os.getenv("DB_PORT", "5432")
        self.DB_NAME = os.getenv("DB_NAME", "postgres")
        self.DB_USER = os.getenv("DB_USER", "postgres")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD", "")
        # JWT設定
        self.SECRET_KEY = os.getenv("SECRET_KEY", "meeting-summary-app-secret-key-2025-super-secure-jwt-token-key")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        
        # OpenAI設定
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        
        # Stripe設定
        self.STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
        self.STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
        self.STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
        self.STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "")
        self.STRIPE_PORTAL_CONFIGURATION_ID = os.getenv("STRIPE_PORTAL_CONFIGURATION_ID", "")
        
        # 暗号化設定
        self.ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "your-encryption-key-here")
        
        # Google OAuth設定
        self.GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your-google-client-id.apps.googleusercontent.com")
        self.GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "your-google-client-secret")
        
        # LINE OAuth設定
        self.LINE_CHANNEL_ID = os.getenv("LINE_CHANNEL_ID", "2007873513")
        self.LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
        self.LINE_REDIRECT_URI = os.getenv("LINE_REDIRECT_URI", "https://meeting-summary-app.jibunkaikaku-lab.com")
        
        # ファイル設定
        self.MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
        self.UPLOAD_DIR = "uploads"
        self.AUDIO_CHUNKS_DIR = "audio_chunks"
        self.SUMMARIES_DIR = "summaries"
        
        # 録音設定
        self.FREE_RECORDING_LIMIT = 30  # 分
        self.PREMIUM_RECORDING_LIMIT = 120  # 分
        
        # レート制限設定
        self.RATE_LIMIT_MAX_REQUESTS = 100
        self.RATE_LIMIT_WINDOW_SECONDS = 60
        self.RATE_LIMIT_PER_MINUTE = 60
        
        # ログ設定
        self.SECURITY_LEVEL = "standard"
        self.LOG_LEVEL = "INFO"
        self.LOG_FILE = "logs/app.log"
        self.SECURITY_LOG_FILE = "logs/security.log"
        self.PERFORMANCE_LOG_FILE = "logs/performance.log"
        
        # 音声ファイル設定
        self.ALLOWED_AUDIO_TYPES = '["audio/wav","audio/mp3","audio/m4a","audio/aac","audio/flac","audio/ogg","audio/webm"]'
        
        # 課金設定
        self.FREE_TRIAL_DAYS = "31"
        self.FREE_USAGE_LIMIT = "10"
        self.MONTHLY_PRICE = "999"
        
        # 機能設定
        self.DUMMY_LOGIN_ENABLED = "true"
        
        # フロントエンド設定
        self.VITE_API_URL = os.getenv("VITE_API_URL", "")
        
        # Whisper設定
        self.WHISPER_MODEL = "base"
    
    # PostgreSQLの場合、URLを調整
    @property
    def database_url(self) -> str:
        # 完全な接続文字列が設定されている場合は優先
        if self.DATABASE_URL and self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL
        
        # 個別設定がある場合は組み立て
        if self.DB_HOST and self.DB_USER and self.DB_PASSWORD:
            import urllib.parse
            password = urllib.parse.quote_plus(self.DB_PASSWORD)
            # 課金プランなので直接接続（ポート5432）を使用
            return f"postgresql://{self.DB_USER}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        
        # 従来のDATABASE_URLを使用
        if self.DATABASE_URL.startswith("postgres://"):
            return self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return self.DATABASE_URL

# 設定を初期化
try:
    settings = Settings()
    print("✅ 設定クラス初期化成功")
except Exception as e:
    print(f"❌ 設定クラス初期化エラー: {e}")
    # フォールバック設定
    settings = type('Settings', (), {
        'DATABASE_URL': os.getenv("DATABASE_URL", "sqlite:///./meeting_summary.db"),
        'DB_HOST': os.getenv("DB_HOST", ""),
        'DB_PORT': os.getenv("DB_PORT", "5432"),
        'DB_NAME': os.getenv("DB_NAME", "postgres"),
        'DB_USER': os.getenv("DB_USER", "postgres"),
        'DB_PASSWORD': os.getenv("DB_PASSWORD", ""),
        'OPENAI_API_KEY': os.getenv("OPENAI_API_KEY", ""),
        'GOOGLE_CLIENT_ID': os.getenv("GOOGLE_CLIENT_ID", ""),
        'SECRET_KEY': os.getenv("SECRET_KEY", "meeting-summary-app-secret-key-2025-super-secure-jwt-token-key"),
        'ALGORITHM': "HS256",
        'ACCESS_TOKEN_EXPIRE_MINUTES': 30,
        'STRIPE_SECRET_KEY': os.getenv("STRIPE_SECRET_KEY", ""),
        'STRIPE_PUBLISHABLE_KEY': os.getenv("STRIPE_PUBLISHABLE_KEY", ""),
        'STRIPE_WEBHOOK_SECRET': os.getenv("STRIPE_WEBHOOK_SECRET", ""),
        'STRIPE_PRICE_ID': os.getenv("STRIPE_PRICE_ID", ""),
        'STRIPE_PORTAL_CONFIGURATION_ID': os.getenv("STRIPE_PORTAL_CONFIGURATION_ID", ""),
        'ENCRYPTION_KEY': os.getenv("ENCRYPTION_KEY", "your-encryption-key-here"),
        'GOOGLE_CLIENT_SECRET': os.getenv("GOOGLE_CLIENT_SECRET", ""),
        'LINE_CHANNEL_ID': os.getenv("LINE_CHANNEL_ID", "2007873513"),
        'LINE_CHANNEL_SECRET': os.getenv("LINE_CHANNEL_SECRET", ""),
        'LINE_REDIRECT_URI': os.getenv("LINE_REDIRECT_URI", "https://meeting-summary-app.jibunkaikaku-lab.com"),
        'MAX_FILE_SIZE': 100 * 1024 * 1024,
        'UPLOAD_DIR': "uploads",
        'AUDIO_CHUNKS_DIR': "audio_chunks",
        'SUMMARIES_DIR': "summaries",
        'FREE_RECORDING_LIMIT': 30,
        'PREMIUM_RECORDING_LIMIT': 120,
        'RATE_LIMIT_MAX_REQUESTS': 100,
        'RATE_LIMIT_WINDOW_SECONDS': 60,
        'RATE_LIMIT_PER_MINUTE': 60,
        'SECURITY_LEVEL': "standard",
        'LOG_LEVEL': "INFO",
        'LOG_FILE': "logs/app.log",
        'SECURITY_LOG_FILE': "logs/security.log",
        'PERFORMANCE_LOG_FILE': "logs/performance.log",
        'ALLOWED_AUDIO_TYPES': '["audio/wav","audio/mp3","audio/m4a","audio/aac","audio/flac","audio/ogg","audio/webm"]',
        'FREE_TRIAL_DAYS': "31",
        'FREE_USAGE_LIMIT': "10",
        'MONTHLY_PRICE': "999",
        'DUMMY_LOGIN_ENABLED': "true",
        'VITE_API_URL': os.getenv("VITE_API_URL", ""),
        'WHISPER_MODEL': "base"
    })()
    
    # database_urlプロパティを追加
    def database_url(self):
        if self.DATABASE_URL and self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL
        if self.DB_HOST and self.DB_USER and self.DB_PASSWORD:
            import urllib.parse
            password = urllib.parse.quote_plus(self.DB_PASSWORD)
            return f"postgresql://{self.DB_USER}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        if self.DATABASE_URL.startswith("postgres://"):
            return self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return self.DATABASE_URL
    
    settings.database_url = database_url.__get__(settings, type(settings))
    print("⚠️ フォールバック設定を使用")

# デバッグ用：環境変数の確認
try:
    print(f"DEBUG: OPENAI_API_KEY設定確認 - Key exists: {bool(settings.OPENAI_API_KEY)}")
    print(f"DEBUG: OPENAI_API_KEY長さ: {len(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else 0}")
    print(f"DEBUG: GOOGLE_CLIENT_ID設定確認 - Key exists: {bool(settings.GOOGLE_CLIENT_ID)}")
    print(f"DEBUG: GOOGLE_CLIENT_ID設定済み: {settings.GOOGLE_CLIENT_ID != 'your-google-client-id.apps.googleusercontent.com'}")
except Exception as e:
    print(f"⚠️ デバッグ出力エラー: {e}") 