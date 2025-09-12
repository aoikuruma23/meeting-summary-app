#!/usr/bin/env python3
"""
Supabase移行用のセットアップスクリプト
"""
import os
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

def test_connection():
    """データベース接続をテスト"""
    try:
        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ データベース接続成功")
            return True
    except Exception as e:
        print(f"❌ データベース接続失敗: {e}")
        return False

def create_tables():
    """テーブルを作成"""
    try:
        from app.core.database import Base, engine
        Base.metadata.create_all(bind=engine)
        print("✅ テーブル作成完了")
        return True
    except Exception as e:
        print(f"❌ テーブル作成失敗: {e}")
        return False

def main():
    print("🚀 Supabase移行セットアップ開始")
    print(f"📊 データベースURL: {settings.database_url[:50]}...")
    
    # 接続テスト
    if not test_connection():
        print("\n💡 解決方法:")
        print("1. SupabaseプロジェクトでデータベースURLを確認")
        print("2. 環境変数 DATABASE_URL を正しく設定")
        print("3. ネットワーク接続を確認")
        sys.exit(1)
    
    # テーブル作成
    if not create_tables():
        print("\n💡 解決方法:")
        print("1. データベース権限を確認")
        print("2. テーブル名の競合を確認")
        sys.exit(1)
    
    print("\n🎉 Supabase移行セットアップ完了！")
    print("\n📋 次のステップ:")
    print("1. 既存データの移行（必要に応じて）")
    print("2. アプリケーションの動作テスト")
    print("3. 本番環境でのデプロイ")

if __name__ == "__main__":
    main()
