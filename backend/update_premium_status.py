#!/usr/bin/env python3
"""
Renderのデータベースでユーザーのプレミアム状態を更新するスクリプト
"""

from app.core.database import get_db
from app.models.user import User

def update_premium_status():
    """ユーザーのプレミアム状態を更新"""
    try:
        db = next(get_db())
        
        # ユーザーID 1をプレミアムに更新
        user = db.query(User).filter(User.id == 1).first()
        if user:
            print(f"更新前 - User ID: {user.id}, Email: {user.email}, is_premium: {user.is_premium}")
            
            user.is_premium = "true"
            db.commit()
            
            # 更新後の確認
            user = db.query(User).filter(User.id == 1).first()
            print(f"更新後 - User ID: {user.id}, Email: {user.email}, is_premium: {user.is_premium}")
            print("✅ プレミアム状態の更新が完了しました")
        else:
            print("❌ ユーザーが見つかりません")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    update_premium_status() 