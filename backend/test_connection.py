#!/usr/bin/env python3
"""
Supabase接続テスト用スクリプト
"""
import urllib.parse
from sqlalchemy import create_engine, text

def test_supabase_connection():
    """Supabase接続をテスト"""
    # パスワードをURLエンコード
    password = "Y$!.4A@NfR8zyXQ"
    encoded_password = urllib.parse.quote_plus(password)
    
    # 接続文字列を作成
    connection_string = f"postgresql://postgres:{encoded_password}@db.vkjxsjkboafefejspape.supabase.co:5432/postgres"
    
    print(f"🔗 接続文字列: {connection_string[:50]}...")
    
    try:
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            print("✅ 接続成功!")
            print(f"📊 テスト結果: {result.fetchone()}")
            return True, connection_string
            
    except Exception as e:
        print(f"❌ 接続失敗: {e}")
        return False, None

if __name__ == "__main__":
    success, conn_str = test_supabase_connection()
    if success:
        print(f"\n🎉 接続成功!")
        print(f"📋 正しい接続文字列: {conn_str}")
    else:
        print("\n💡 解決方法:")
        print("1. Supabaseダッシュボードでパスワードを確認")
        print("2. ネットワーク接続を確認")
