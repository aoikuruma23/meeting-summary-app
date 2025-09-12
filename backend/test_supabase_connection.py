#!/usr/bin/env python3
"""
Supabase接続テスト用スクリプト
"""
import os
import sys
from sqlalchemy import create_engine, text

def test_connection(connection_string):
    """データベース接続をテスト"""
    try:
        print(f"🔗 接続テスト中: {connection_string[:50]}...")
        engine = create_engine(connection_string)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            print("✅ 接続成功!")
            print(f"📊 テスト結果: {result.fetchone()}")
            return True
            
    except Exception as e:
        print(f"❌ 接続失敗: {e}")
        return False

def main():
    print("🚀 Supabase接続テスト")
    print("=" * 50)
    
    # 接続文字列の入力
    connection_string = input("Supabase接続文字列を入力してください: ").strip()
    
    if not connection_string:
        print("❌ 接続文字列が入力されていません")
        sys.exit(1)
    
    # 接続テスト
    if test_connection(connection_string):
        print("\n🎉 接続テスト成功!")
        print("\n📋 次のステップ:")
        print("1. この接続文字列を .env ファイルに設定")
        print("2. python setup_supabase.py を実行")
        print("3. アプリケーションを起動")
    else:
        print("\n💡 解決方法:")
        print("1. Supabaseダッシュボードでパスワードを確認")
        print("2. 接続文字列の形式を確認")
        print("3. ネットワーク接続を確認")

if __name__ == "__main__":
    main()
