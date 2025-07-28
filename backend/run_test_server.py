#!/usr/bin/env python3
"""
テスト用サーバー起動スクリプト
"""

import os
import uvicorn
import asyncio
from app.core.database import engine, Base
from app.models.user import User
from app.models.meeting import Meeting, AudioChunk

def setup_test_environment():
    print("[DEBUG] setup_test_environment() 開始")
    # テスト用の環境変数を設定
    os.environ["ENV_FILE"] = "test.env"
    print("[DEBUG] ENV_FILE 設定完了")
    # データベーステーブルを作成
    print("🗄️  データベーステーブルを作成中...")
    Base.metadata.create_all(bind=engine)
    print("✅ データベーステーブル作成完了")
    print("[DEBUG] setup_test_environment() 終了")

def main():
    print("[DEBUG] main() 開始")
    print("🚀 テスト用サーバーを起動します...")
    # テスト環境のセットアップ
    setup_test_environment()
    print("[DEBUG] setup_test_environment() 完了")
    # サーバー設定
    config = {
        "app": "main:app",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": True,
        "log_level": "info"
    }
    print(f"🌐 サーバーURL: http://localhost:{config['port']}")
    print("📚 API ドキュメント: http://localhost:8000/docs")
    print("🔍 対話的API ドキュメント: http://localhost:8000/redoc")
    print("\n🛑 サーバーを停止するには Ctrl+C を押してください")
    print("[DEBUG] uvicorn.run() 実行直前")
    # サーバー起動
    uvicorn.run(**config)
    print("[DEBUG] main() 終了")

if __name__ == "__main__":
    print("[DEBUG] __main__ 実行")
    main() 