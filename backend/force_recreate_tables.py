#!/usr/bin/env python3
"""
データベーステーブルを強制的に再作成するスクリプト
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.database import Base, engine
from app.models.user import User

def force_recreate_tables():
    """データベーステーブルを強制的に再作成"""
    try:
        print("データベーステーブルを強制的に再作成します...")
        
        # 既存のテーブルを削除
        Base.metadata.drop_all(bind=engine)
        print("✓ 既存のテーブルを削除しました")
        
        # 新しいテーブルを作成
        Base.metadata.create_all(bind=engine)
        print("✓ 新しいテーブルを作成しました")
        
        # テーブル構造を確認
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                ORDER BY ordinal_position
            """))
            
            print("\n=== usersテーブルの構造 ===")
            for row in result:
                print(f"  {row[0]}: {row[1]} ({'NULL' if row[2] == 'YES' else 'NOT NULL'})")
        
        print("\n✓ データベーステーブルの再作成が完了しました")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        print(f"スタックトレース: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    force_recreate_tables() 