from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# データベースエンジンの作成（接続プール設定付き）
engine = create_engine(
    settings.database_url,  # プロパティを使用
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    # Supabase用の接続プール設定
    pool_size=20,           # 基本接続数
    max_overflow=30,        # 追加接続数（最大50接続）
    pool_pre_ping=True,     # 接続検証（接続が生きているかチェック）
    pool_recycle=3600,      # 接続リサイクル（1時間）
    echo=False              # SQLログ出力（本番ではFalse）
)

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

# すべてのテーブルを作成
Base.metadata.create_all(bind=engine) 