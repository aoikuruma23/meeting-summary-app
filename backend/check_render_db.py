#!/usr/bin/env python3
"""
Renderのデータベース状態を確認するスクリプト
"""

import os
from app.core.database import get_db
from app.models.user import User

def check_render_database():
    """Renderのデータベース状態を確認"""
    try:
        print("=== Renderデータベース状態確認 ===")
        print(f"Database URL: {os.getenv('DATABASE_URL', 'Not set')}")
        
        db = next(get_db())
        
        # 全ユーザーを取得
        users = db.query(User).all()
        print(f"総ユーザー数: {len(users)}")
        
        for user in users:
            print(f"User ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"is_premium: {user.is_premium}")
            print(f"stripe_subscription_id: {user.stripe_subscription_id}")
            print(f"stripe_customer_id: {user.stripe_customer_id}")
            print("---")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    check_render_database() 