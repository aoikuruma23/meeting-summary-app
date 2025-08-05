#!/usr/bin/env python3
"""
データベースの状態を詳細に確認するスクリプト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine
from app.models.user import User
from sqlalchemy import text

def debug_database():
    """データベースの状態を確認"""
    print("=== データベース状態確認 ===")
    
    # データベース接続テスト
    try:
        db = SessionLocal()
        print("✓ データベース接続成功")
        
        # テーブル一覧を確認
        result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = [row[0] for row in result]
        print(f"✓ テーブル一覧: {tables}")
        
        # usersテーブルの構造を確認
        try:
            result = db.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users'"))
            columns = [(row[0], row[1]) for row in result]
            print(f"✓ usersテーブル構造: {columns}")
        except Exception as e:
            print(f"✗ usersテーブル構造確認エラー: {str(e)}")
        
        # ユーザーデータを確認
        try:
            users = db.query(User).all()
            print(f"✓ ユーザー数: {len(users)}")
            
            for user in users:
                print(f"  - ID: {user.id}, Email: {user.email}, Name: {user.name}, Premium: {user.is_premium}")
                
        except Exception as e:
            print(f"✗ ユーザーデータ取得エラー: {str(e)}")
        
        # 特定のユーザーIDで検索
        try:
            user = db.query(User).filter(User.id == 1).first()
            if user:
                print(f"✓ ユーザーID 1 が見つかりました: {user.email}")
            else:
                print("✗ ユーザーID 1 が見つかりません")
        except Exception as e:
            print(f"✗ ユーザーID 1 検索エラー: {str(e)}")
        
        db.close()
        
    except Exception as e:
        print(f"✗ データベース接続エラー: {str(e)}")

if __name__ == "__main__":
    debug_database() 