#!/usr/bin/env python3
"""
Renderのデータベースを初期化するスクリプト
"""

from app.core.database import engine, Base
from app.models.user import User
from app.core.database import get_db
from datetime import datetime

def init_render_database():
    """Renderのデータベースを初期化"""
    try:
        print("=== Renderデータベース初期化 ===")
        
        # テーブルを作成
        Base.metadata.create_all(bind=engine)
        print("✅ テーブルを作成しました")
        
        # ダミーユーザーを作成
        db = next(get_db())
        
        # 既存のユーザーを確認
        existing_user = db.query(User).filter(User.email == "dummy@example.com").first()
        if existing_user:
            print(f"既存ユーザーが見つかりました: ID={existing_user.id}")
            # プレミアム状態に更新
            existing_user.is_premium = "true"
            db.commit()
            print("✅ 既存ユーザーをプレミアムに更新しました")
        else:
            # 新しいユーザーを作成
            new_user = User(
                email="dummy@example.com",
                name="ダミーユーザー",
                is_premium="true",
                usage_count=0,
                trial_start_date=datetime.now(),
                created_at=datetime.now()
            )
            db.add(new_user)
            db.commit()
            print("✅ 新しいダミーユーザーを作成しました")
        
        # 確認
        user = db.query(User).filter(User.email == "dummy@example.com").first()
        if user:
            print(f"確認 - User ID: {user.id}, Email: {user.email}, is_premium: {user.is_premium}")
            print("✅ データベース初期化が完了しました")
        else:
            print("❌ ユーザーの作成に失敗しました")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        import traceback
        print(f"詳細: {traceback.format_exc()}")

if __name__ == "__main__":
    init_render_database() 