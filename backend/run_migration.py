#!/usr/bin/env python3
"""
データベースマイグレーション実行スクリプト
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.database import Base

def run_migration():
    """データベースマイグレーションを実行"""
    try:
        # データベースエンジンを作成
        engine = create_engine(settings.DATABASE_URL)
        
        # セッションを作成
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print("データベースマイグレーションを開始します...")
        
        # 新しいカラムを追加
        try:
            # profile_pictureカラムを追加
            db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_picture VARCHAR"))
            print("✓ profile_pictureカラムを追加しました")
            
            # auth_providerカラムを追加
            db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider VARCHAR"))
            print("✓ auth_providerカラムを追加しました")
            
            # line_user_idカラムを追加
            db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS line_user_id VARCHAR"))
            print("✓ line_user_idカラムを追加しました")
            
            # 既存のline_idカラムをline_user_idにリネーム（存在する場合）
            try:
                db.execute(text("ALTER TABLE users RENAME COLUMN line_id TO line_user_id"))
                print("✓ line_idカラムをline_user_idにリネームしました")
            except:
                print("ℹ line_idカラムは存在しないか、既にリネーム済みです")
            
            # 変更をコミット
            db.commit()
            print("✓ データベースマイグレーションが完了しました")
            
        except Exception as e:
            print(f"❌ マイグレーションエラー: {e}")
            db.rollback()
            raise
        
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ データベース接続エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration() 