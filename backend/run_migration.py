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
            # データベースタイプを判定
            database_url = settings.DATABASE_URL
            is_postgresql = database_url.startswith('postgresql://') or database_url.startswith('postgres://')
            
            if is_postgresql:
                # PostgreSQL用の処理
                print("ℹ PostgreSQLデータベースを検出しました")
                
                # 既存のカラムを確認（PostgreSQL用）
                result = db.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND table_schema = 'public'
                """))
                existing_columns = [row[0] for row in result.fetchall()]
                
                # profile_pictureカラムを追加
                if "profile_picture" not in existing_columns:
                    db.execute(text("ALTER TABLE users ADD COLUMN profile_picture VARCHAR"))
                    print("✓ profile_pictureカラムを追加しました")
                else:
                    print("ℹ profile_pictureカラムは既に存在します")
                
                # auth_providerカラムを追加
                if "auth_provider" not in existing_columns:
                    db.execute(text("ALTER TABLE users ADD COLUMN auth_provider VARCHAR"))
                    print("✓ auth_providerカラムを追加しました")
                else:
                    print("ℹ auth_providerカラムは既に存在します")
                
                # line_user_idカラムを追加
                if "line_user_id" not in existing_columns:
                    db.execute(text("ALTER TABLE users ADD COLUMN line_user_id VARCHAR"))
                    print("✓ line_user_idカラムを追加しました")
                else:
                    print("ℹ line_user_idカラムは既に存在します")
            else:
                # SQLite用の処理
                print("ℹ SQLiteデータベースを検出しました")
                
                # 既存のカラムを確認（SQLite用）
                result = db.execute(text("PRAGMA table_info(users)"))
                existing_columns = [row[1] for row in result.fetchall()]
                
                # profile_pictureカラムを追加
                if "profile_picture" not in existing_columns:
                    db.execute(text("ALTER TABLE users ADD COLUMN profile_picture VARCHAR"))
                    print("✓ profile_pictureカラムを追加しました")
                else:
                    print("ℹ profile_pictureカラムは既に存在します")
                
                # auth_providerカラムを追加
                if "auth_provider" not in existing_columns:
                    db.execute(text("ALTER TABLE users ADD COLUMN auth_provider VARCHAR"))
                    print("✓ auth_providerカラムを追加しました")
                else:
                    print("ℹ auth_providerカラムは既に存在します")
                
                # line_user_idカラムを追加
                if "line_user_id" not in existing_columns:
                    db.execute(text("ALTER TABLE users ADD COLUMN line_user_id VARCHAR"))
                    print("✓ line_user_idカラムを追加しました")
                else:
                    print("ℹ line_user_idカラムは既に存在します")
            
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