import os
from typing import Optional, List

# 設定を直接作成（クラスを使わない）
def create_settings():
    """設定オブジェクトを作成"""
    settings = type('Settings', (), {})()
    
    # データベース設定
    settings.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./meeting_summary.db")
    settings.DB_HOST = os.getenv("DB_HOST", "")
    settings.DB_PORT = os.getenv("DB_PORT", "5432")
    settings.DB_NAME = os.getenv("DB_NAME", "postgres")
    settings.DB_USER = os.getenv("DB_USER", "postgres")
    settings.DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    
    # JWT設定
    settings.SECRET_KEY = os.getenv("SECRET_KEY", "meeting-summary-app-secret-key-2025-super-secure-jwt-token-key")
    settings.ALGORITHM = "HS256"
    settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # OpenAI設定
    settings.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Stripe設定
    settings.STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    settings.STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    settings.STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    settings.STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "")
    settings.STRIPE_PORTAL_CONFIGURATION_ID = os.getenv("STRIPE_PORTAL_CONFIGURATION_ID", "")
    
    # 暗号化設定
    settings.ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "your-encryption-key-here")
    
    # Google OAuth設定
    settings.GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your-google-client-id.apps.googleusercontent.com")
    settings.GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "your-google-client-secret")
    
    # LINE OAuth設定
    settings.LINE_CHANNEL_ID = os.getenv("LINE_CHANNEL_ID", "2007873513")
    settings.LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
    settings.LINE_REDIRECT_URI = os.getenv("LINE_REDIRECT_URI", "https://meeting-summary-app.jibunkaikaku-lab.com")
    
    # ファイル設定
    settings.MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    settings.UPLOAD_DIR = "uploads"
    settings.AUDIO_CHUNKS_DIR = "audio_chunks"
    settings.SUMMARIES_DIR = "summaries"
    
    # 録音設定
    settings.FREE_RECORDING_LIMIT = 30  # 分
    settings.PREMIUM_RECORDING_LIMIT = 120  # 分
    
    # レート制限設定
    settings.RATE_LIMIT_MAX_REQUESTS = 100
    settings.RATE_LIMIT_WINDOW_SECONDS = 60
    settings.RATE_LIMIT_PER_MINUTE = 60
    
    # ログ設定
    settings.SECURITY_LEVEL = "standard"
    settings.LOG_LEVEL = "INFO"
    settings.LOG_FILE = "logs/app.log"
    settings.SECURITY_LOG_FILE = "logs/security.log"
    settings.PERFORMANCE_LOG_FILE = "logs/performance.log"
    
    # 音声ファイル設定
    settings.ALLOWED_AUDIO_TYPES = '["audio/wav","audio/mp3","audio/m4a","audio/aac","audio/flac","audio/ogg","audio/webm"]'
    
    # 課金設定
    settings.FREE_TRIAL_DAYS = "31"
    settings.FREE_USAGE_LIMIT = "10"
    settings.MONTHLY_PRICE = "999"
    
    # 機能設定
    settings.DUMMY_LOGIN_ENABLED = "true"
    
    # フロントエンド設定
    settings.VITE_API_URL = os.getenv("VITE_API_URL", "")
    
    # Whisper設定
    settings.WHISPER_MODEL = "base"
    
    return settings

def get_database_url(settings):
    """データベースURLを取得"""
    # 完全な接続文字列が設定されている場合は優先
    if settings.DATABASE_URL and settings.DATABASE_URL.startswith("postgresql://"):
        return settings.DATABASE_URL
    
    # 個別設定がある場合は組み立て
    if settings.DB_HOST and settings.DB_USER and settings.DB_PASSWORD:
        import urllib.parse
        password = urllib.parse.quote_plus(settings.DB_PASSWORD)
        # 課金プランなので直接接続（ポート5432）を使用
        return f"postgresql://{settings.DB_USER}:{password}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    
    # 従来のDATABASE_URLを使用
    if settings.DATABASE_URL.startswith("postgres://"):
        return settings.DATABASE_URL.replace("postgres://", "postgresql://", 1)
    return settings.DATABASE_URL

# 設定を初期化
settings = create_settings()
settings.database_url = get_database_url(settings)
print("✅ 設定初期化成功")

# デバッグ用：環境変数の確認
try:
    print(f"DEBUG: OPENAI_API_KEY設定確認 - Key exists: {bool(settings.OPENAI_API_KEY)}")
    print(f"DEBUG: OPENAI_API_KEY長さ: {len(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else 0}")
    print(f"DEBUG: GOOGLE_CLIENT_ID設定確認 - Key exists: {bool(settings.GOOGLE_CLIENT_ID)}")
    print(f"DEBUG: GOOGLE_CLIENT_ID設定済み: {settings.GOOGLE_CLIENT_ID != 'your-google-client-id.apps.googleusercontent.com'}")
except Exception as e:
    print(f"⚠️ デバッグ出力エラー: {e}") 