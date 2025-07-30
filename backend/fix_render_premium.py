#!/usr/bin/env python3
"""
Renderのデータベースでプレミアム状態を修正するスクリプト
"""

from app.core.database import get_db
from app.models.user import User

def fix_render_premium():
    """Renderのデータベースでプレミアム状態を修正"""
    try:
        print("=== Renderプレミアム状態修正 ===")
        
        db = next(get_db())
        
        # ユーザーID 1をプレミアムに更新
        user = db.query(User).filter(User.id == 1).first()
        if user:
            print(f"修正前 - User ID: {user.id}, Email: {user.email}, is_premium: {user.is_premium}")
            
            user.is_premium = "true"
            db.commit()
            
            # 修正後の確認
            user = db.query(User).filter(User.id == 1).first()
            print(f"修正後 - User ID: {user.id}, Email: {user.email}, is_premium: {user.is_premium}")
            print("✅ Renderのプレミアム状態修正が完了しました")
        else:
            print("❌ ユーザーが見つかりません")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    fix_render_premium() 