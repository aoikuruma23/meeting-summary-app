#!/usr/bin/env python3
"""
環境変数デバッグ用スクリプト
"""
import os
from app.core.config import settings

def debug_environment():
    """環境変数をデバッグ"""
    print("🔧 環境変数デバッグ")
    print("=" * 50)
    
    # 個別環境変数
    print(f"DB_HOST: {os.getenv('DB_HOST', 'Not set')}")
    print(f"DB_PORT: {os.getenv('DB_PORT', 'Not set')}")
    print(f"DB_NAME: {os.getenv('DB_NAME', 'Not set')}")
    print(f"DB_USER: {os.getenv('DB_USER', 'Not set')}")
    print(f"DB_PASSWORD: {'*' * len(os.getenv('DB_PASSWORD', '')) if os.getenv('DB_PASSWORD') else 'Not set'}")
    
    # 従来のDATABASE_URL
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')[:50]}...")
    
    # 最終的な接続文字列
    print(f"Final database_url: {settings.database_url[:50]}...")
    
    # 接続テスト
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            print("✅ 接続成功!")
            return True
    except Exception as e:
        print(f"❌ 接続失敗: {e}")
        return False

if __name__ == "__main__":
    debug_environment()
