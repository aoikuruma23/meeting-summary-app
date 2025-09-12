from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# データベースエンジンの作成（接続プール設定付き）
engine = create_engine(
    settings.database_url,  # プロパティを使用
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    # Supabase用の接続プール設定（無料プラン対応）
    pool_size=5,            # 基本接続数（無料プラン対応）
    max_overflow=10,        # 追加接続数（最大15接続）
    pool_pre_ping=True,     # 接続検証（接続が生きているかチェック）
    pool_recycle=1800,      # 接続リサイクル（30分）
    pool_timeout=30,        # 接続タイムアウト（30秒）
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