import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.utils.auth import get_password_hash

def create_dummy_user():
    """ダミーユーザーを作成"""
    print("=== ダミーユーザー作成開始 ===")
    
    db = SessionLocal()
    try:
        # 既存のダミーユーザーをチェック
        existing_user = db.query(User).filter(User.username == "dummy_user").first()
        if existing_user:
            print("✅ ダミーユーザーは既に存在します")
            return
        
        # ダミーユーザーを作成
        dummy_user = User(
            username="dummy_user",
            email="dummy@example.com",
            hashed_password=get_password_hash("dummy_password"),
            is_active="active"
        )
        
        db.add(dummy_user)
        db.commit()
        db.refresh(dummy_user)
        
        print(f"✅ ダミーユーザー作成完了: {dummy_user.username}")
        
    except Exception as e:
        print(f"❌ ダミーユーザー作成エラー: {e}")
        import traceback
        print(f"詳細エラー: {traceback.format_exc()}")
    finally:
        db.close()

if __name__ == "__main__":
    create_dummy_user() 