import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Base, engine
from app.models import meeting, user

def create_tables():
    """すべてのテーブルを作成"""
    print("=== テーブル作成開始 ===")
    
    try:
        # すべてのテーブルを作成
        Base.metadata.create_all(bind=engine)
        print("✅ テーブル作成完了")
        
        # テーブル一覧を確認
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📋 作成されたテーブル: {tables}")
        
    except Exception as e:
        print(f"❌ テーブル作成エラー: {e}")
        import traceback
        print(f"詳細エラー: {traceback.format_exc()}")

if __name__ == "__main__":
    create_tables() 