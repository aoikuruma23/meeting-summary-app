import os

# 環境変数を直接読み込むシンプルな設定
def get_database_url():
    """データベースURLを取得"""
    # 完全な接続文字列が設定されている場合は優先
    database_url = os.getenv("DATABASE_URL", "sqlite:///./meeting_summary.db")
    if database_url and database_url.startswith("postgresql://"):
        return database_url
    
    # 個別設定がある場合は組み立て
    db_host = os.getenv("DB_HOST", "")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "postgres")
    
    if db_host and db_user and db_password:
        import urllib.parse
        password = urllib.parse.quote_plus(db_password)
        return f"postgresql://{db_user}:{password}@{db_host}:{db_port}/{db_name}"
    
    # 従来のDATABASE_URLを使用
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql://", 1)
    return database_url

# 設定値を直接取得する関数
def get_setting(key, default=None):
    """設定値を取得"""
    return os.getenv(key, default)

# 設定クラス（シンプル版）
class Config:
    def __init__(self):
        # データベース設定
        self.DATABASE_URL = get_setting("DATABASE_URL", "sqlite:///./meeting_summary.db")
        self.DB_HOST = get_setting("DB_HOST", "")
        self.DB_PORT = get_setting("DB_PORT", "5432")
        self.DB_NAME = get_setting("DB_NAME", "postgres")
        self.DB_USER = get_setting("DB_USER", "postgres")
        self.DB_PASSWORD = get_setting("DB_PASSWORD", "")
        
        # JWT設定
        self.SECRET_KEY = get_setting("SECRET_KEY", "meeting-summary-app-secret-key-2025-super-secure-jwt-token-key")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        
        # OpenAI設定
        self.OPENAI_API_KEY = get_setting("OPENAI_API_KEY", "")
        
        # Stripe設定
        self.STRIPE_SECRET_KEY = get_setting("STRIPE_SECRET_KEY", "")
        self.STRIPE_PUBLISHABLE_KEY = get_setting("STRIPE_PUBLISHABLE_KEY", "")
        self.STRIPE_WEBHOOK_SECRET = get_setting("STRIPE_WEBHOOK_SECRET", "")
        self.STRIPE_PRICE_ID = get_setting("STRIPE_PRICE_ID", "")
        self.STRIPE_PORTAL_CONFIGURATION_ID = get_setting("STRIPE_PORTAL_CONFIGURATION_ID", "")
        
        # 暗号化設定
        self.ENCRYPTION_KEY = get_setting("ENCRYPTION_KEY", "your-encryption-key-here")
        
        # Google OAuth設定
        self.GOOGLE_CLIENT_ID = get_setting("GOOGLE_CLIENT_ID", "your-google-client-id.apps.googleusercontent.com")
        self.GOOGLE_CLIENT_SECRET = get_setting("GOOGLE_CLIENT_SECRET", "your-google-client-secret")
        
        # LINE OAuth設定
        self.LINE_CHANNEL_ID = get_setting("LINE_CHANNEL_ID", "2007873513")
        self.LINE_CHANNEL_SECRET = get_setting("LINE_CHANNEL_SECRET", "")
        self.LINE_REDIRECT_URI = get_setting("LINE_REDIRECT_URI", "https://meeting-summary-app.jibunkaikaku-lab.com")
        
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
        self.VITE_API_URL = get_setting("VITE_API_URL", "")
        
        # Whisper設定
        self.WHISPER_MODEL = "base"
    
    @property
    def database_url(self):
        """データベースURLを取得"""
        return get_database_url()

# 設定インスタンスを作成
try:
    settings = Config()
    print("✅ 設定初期化成功")
except Exception as e:
    print(f"❌ 設定初期化エラー: {e}")
    # フォールバック用の設定
    settings = type('Settings', (), {
        'DATABASE_URL': get_setting("DATABASE_URL", "sqlite:///./meeting_summary.db"),
        'DB_HOST': get_setting("DB_HOST", ""),
        'DB_PORT': get_setting("DB_PORT", "5432"),
        'DB_NAME': get_setting("DB_NAME", "postgres"),
        'DB_USER': get_setting("DB_USER", "postgres"),
        'DB_PASSWORD': get_setting("DB_PASSWORD", ""),
        'database_url': get_database_url()
    })()

# デバッグ用：環境変数の確認
try:
    print(f"DEBUG: OPENAI_API_KEY設定確認 - Key exists: {bool(settings.OPENAI_API_KEY)}")
    print(f"DEBUG: OPENAI_API_KEY長さ: {len(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else 0}")
    print(f"DEBUG: GOOGLE_CLIENT_ID設定確認 - Key exists: {bool(settings.GOOGLE_CLIENT_ID)}")
    print(f"DEBUG: GOOGLE_CLIENT_ID設定済み: {settings.GOOGLE_CLIENT_ID != 'your-google-client-id.apps.googleusercontent.com'}")
except Exception as e:
    print(f"⚠️ デバッグ出力エラー: {e}")