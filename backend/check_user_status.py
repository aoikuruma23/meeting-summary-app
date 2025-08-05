#!/usr/bin/env python3
"""
ユーザーのデータベース状態を確認するスクリプト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User

def check_user_status():
    """ユーザーの状態を確認"""
    db = SessionLocal()
    try:
        # すべてのユーザーを取得
        users = db.query(User).all()
        
        print(f"DEBUG: 全ユーザー数: {len(users)}")
        
        for user in users:
            print(f"DEBUG: ユーザー {user.id}")
            print(f"  - email: {user.email}")
            print(f"  - name: {user.name}")
            print(f"  - is_premium: {user.is_premium} (型: {type(user.is_premium)})")
            print(f"  - auth_provider: {user.auth_provider}")
            print(f"  - google_id: {user.google_id}")
            print(f"  - line_user_id: {user.line_user_id}")
            print(f"  - created_at: {user.created_at}")
            print(f"  - updated_at: {user.updated_at}")
            print("---")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_user_status() 