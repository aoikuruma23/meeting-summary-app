from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# データベースURLを直接取得
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

# データベースエンジンの作成（接続プール設定付き）
try:
    database_url = get_database_url()
    print(f"DEBUG: データベース接続文字列: {database_url[:50]}...")
    
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False} if "sqlite" in database_url else {},
        # Supabase用の接続プール設定（課金プラン対応）
        pool_size=20,           # 基本接続数（課金プラン対応）
        max_overflow=30,        # 追加接続数（最大50接続）
        pool_pre_ping=True,     # 接続検証（接続が生きているかチェック）
        pool_recycle=3600,      # 接続リサイクル（1時間）
        pool_timeout=60,        # 接続タイムアウト（60秒）
        echo=False              # SQLログ出力（本番ではFalse）
    )
    print("✅ データベースエンジン作成成功")
except Exception as e:
    print(f"❌ データベースエンジン作成エラー: {e}")
    # フォールバック用のSQLiteエンジン
    engine = create_engine("sqlite:///./meeting_summary.db")
    print("⚠️ SQLiteフォールバックを使用")

# セッションクラスの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Baseクラスの作成
Base = declarative_base()

# データベースセッションの依存性注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# モデルをインポートしてテーブルを作成
from app.models import meeting, user

# テーブル作成を遅延実行（起動時エラー回避）
def create_tables():
    """テーブルを作成（必要時に呼び出し）"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ データベーステーブル作成完了")
    except Exception as e:
        print(f"⚠️ テーブル作成エラー: {e}")
        # エラーでも起動は継続

# 起動時はテーブル作成をスキップ
# create_tables()  # コメントアウト 