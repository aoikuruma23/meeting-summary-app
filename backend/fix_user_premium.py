#!/usr/bin/env python3
"""
ユーザーのプレミアム状態を修正するスクリプト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User

def fix_user_premium_status():
    """ユーザーのプレミアム状態を修正"""
    db = SessionLocal()
    try:
        # すべてのユーザーを取得
        users = db.query(User).all()
        
        print(f"DEBUG: 全ユーザー数: {len(users)}")
        
        for user in users:
            print(f"DEBUG: ユーザー {user.id} - email: {user.email}, is_premium: {user.is_premium}")
            
            # GoogleまたはLINEユーザーの場合、プレミアムに設定
            if user.auth_provider in ["google", "line"] or "@line.user" in user.email:
                if user.is_premium != "true":
                    user.is_premium = "true"
                    print(f"DEBUG: ユーザー {user.id} をプレミアムに設定")
                else:
                    print(f"DEBUG: ユーザー {user.id} は既にプレミアム")
            else:
                print(f"DEBUG: ユーザー {user.id} はメール/パスワードユーザー")
        
        # 変更を保存
        db.commit()
        print("DEBUG: データベース更新完了")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_user_premium_status() 