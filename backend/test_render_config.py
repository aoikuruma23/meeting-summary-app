#!/usr/bin/env python3
"""
Render環境変数設定テスト用スクリプト
"""
import os
from app.core.config import settings

def test_database_config():
    """データベース設定をテスト"""
    print("🔧 データベース設定確認")
    print("=" * 50)
    
    print(f"📊 DATABASE_URL: {settings.DATABASE_URL[:50]}...")
    print(f"📊 DB_HOST: {settings.DB_HOST}")
    print(f"📊 DB_PORT: {settings.DB_PORT}")
    print(f"📊 DB_NAME: {settings.DB_NAME}")
    print(f"📊 DB_USER: {settings.DB_USER}")
    print(f"📊 DB_PASSWORD: {'*' * len(settings.DB_PASSWORD) if settings.DB_PASSWORD else 'Not set'}")
    
    print(f"\n🔗 最終的な接続文字列: {settings.database_url[:50]}...")
    
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
    test_database_config()
