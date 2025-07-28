#!/usr/bin/env python3
"""
API動作テストスクリプト
"""

import os
import sys
import asyncio
import httpx
import json
from datetime import datetime

# テスト用の環境変数を設定
os.environ["ENV_FILE"] = "test.env"

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app
from app.core.database import engine, Base
from app.models.user import User
from app.models.meeting import Meeting, AudioChunk
from app.services.auth_service import AuthService
from app.core.database import get_db

class APITester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.client = httpx.AsyncClient()
        self.test_user = None
        self.test_token = None
    
    async def setup_database(self):
        """テスト用データベースのセットアップ"""
        print("🗄️  データベースをセットアップ中...")
        Base.metadata.create_all(bind=engine)
        print("✅ データベースセットアップ完了")
    
    async def create_test_user(self):
        """テスト用ユーザーの作成"""
        print("👤 テストユーザーを作成中...")
        
        # データベースセッションの取得
        db = next(get_db())
        
        # テスト用ユーザーが既に存在するかチェック
        test_email = "test@example.com"
        existing_user = db.query(User).filter(User.email == test_email).first()
        
        if existing_user:
            self.test_user = existing_user
            print(f"✅ 既存のテストユーザーを使用: {test_email}")
        else:
            # 新しいテストユーザーを作成
            self.test_user = User(
                email=test_email,
                name="テストユーザー",
                is_premium=False,
                usage_count=0
            )
            db.add(self.test_user)
            db.commit()
            db.refresh(self.test_user)
            print(f"✅ 新しいテストユーザーを作成: {test_email}")
        
        # 認証サービスの初期化
        auth_service = AuthService()
        
        # テスト用のJWTトークンを生成
        self.test_token = auth_service.create_access_token(data={"sub": test_email})
        
        print(f"🔑 テストトークン: {self.test_token[:50]}...")
    
    async def test_health_endpoints(self):
        """ヘルスチェックエンドポイントのテスト"""
        print("\n🏥 ヘルスチェックエンドポイントをテスト中...")
        
        # メインのヘルスチェック
        response = await self.client.get(f"{self.base_url}/health")
        print(f"📊 メインヘルスチェック: {response.status_code}")
        
        # 各APIのヘルスチェック
        apis = ["auth", "recording", "summary", "billing"]
        for api in apis:
            try:
                response = await self.client.get(f"{self.base_url}/api/{api}/health")
                print(f"📊 {api} API ヘルスチェック: {response.status_code}")
            except Exception as e:
                print(f"❌ {api} API ヘルスチェック失敗: {e}")
    
    async def test_auth_api(self):
        """認証APIのテスト"""
        print("\n🔐 認証APIをテスト中...")
        
        # 現在のユーザー情報取得
        headers = {"Authorization": f"Bearer {self.test_token}"}
        try:
            response = await self.client.get(f"{self.base_url}/api/auth/me", headers=headers)
            print(f"👤 ユーザー情報取得: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"📋 レスポンス: {json.dumps(data, indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"❌ ユーザー情報取得失敗: {e}")
        
        # 利用統計取得
        try:
            response = await self.client.get(f"{self.base_url}/api/auth/stats", headers=headers)
            print(f"📊 利用統計取得: {response.status_code}")
        except Exception as e:
            print(f"❌ 利用統計取得失敗: {e}")
    
    async def test_recording_api(self):
        """録音APIのテスト"""
        print("\n🎙️  録音APIをテスト中...")
        
        headers = {"Authorization": f"Bearer {self.test_token}"}
        
        # 録音開始
        try:
            start_data = {"title": "テスト会議"}
            response = await self.client.post(
                f"{self.base_url}/api/recording/start",
                json=start_data,
                headers=headers
            )
            print(f"🎬 録音開始: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                meeting_id = data.get("data", {}).get("meeting", {}).get("id")
                print(f"📋 会議ID: {meeting_id}")
        except Exception as e:
            print(f"❌ 録音開始失敗: {e}")
        
        # 録音一覧取得
        try:
            response = await self.client.get(f"{self.base_url}/api/recording/list", headers=headers)
            print(f"📋 録音一覧取得: {response.status_code}")
        except Exception as e:
            print(f"❌ 録音一覧取得失敗: {e}")
        
        # ストレージ情報取得
        try:
            response = await self.client.get(f"{self.base_url}/api/recording/storage", headers=headers)
            print(f"💾 ストレージ情報取得: {response.status_code}")
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    print(f"❌ エラー詳細: {error_data}")
                except:
                    print(f"❌ エラーレスポンス: {response.text}")
        except Exception as e:
            print(f"❌ ストレージ情報取得失敗: {e}")
    
    async def test_summary_api(self):
        """要約APIのテスト"""
        print("\n📝 要約APIをテスト中...")
        
        headers = {"Authorization": f"Bearer {self.test_token}"}
        
        # 要約履歴取得
        try:
            response = await self.client.get(f"{self.base_url}/api/summary/history", headers=headers)
            print(f"📋 要約履歴取得: {response.status_code}")
        except Exception as e:
            print(f"❌ 要約履歴取得失敗: {e}")
        
        # 利用統計取得
        try:
            response = await self.client.get(f"{self.base_url}/api/summary/stats", headers=headers)
            print(f"📊 要約統計取得: {response.status_code}")
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    print(f"❌ エラー詳細: {error_data}")
                except:
                    print(f"❌ エラーレスポンス: {response.text}")
        except Exception as e:
            print(f"❌ 要約統計取得失敗: {e}")
        
        # コスト推定
        try:
            cost_data = {"text_length": 1000, "model": "gpt-4"}
            response = await self.client.post(
                f"{self.base_url}/api/summary/estimate-cost",
                json=cost_data,
                headers=headers
            )
            print(f"💰 コスト推定: {response.status_code}")
        except Exception as e:
            print(f"❌ コスト推定失敗: {e}")
    
    async def test_billing_api(self):
        """課金APIのテスト"""
        print("\n💳 課金APIをテスト中...")
        
        headers = {"Authorization": f"Bearer {self.test_token}"}
        
        # サブスクリプション状況取得
        try:
            response = await self.client.get(f"{self.base_url}/api/billing/subscription", headers=headers)
            print(f"📊 サブスクリプション状況取得: {response.status_code}")
        except Exception as e:
            print(f"❌ サブスクリプション状況取得失敗: {e}")
        
        # 料金プラン情報取得
        try:
            response = await self.client.get(f"{self.base_url}/api/billing/pricing")
            print(f"💰 料金プラン情報取得: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"📋 料金情報: {json.dumps(data, indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"❌ 料金プラン情報取得失敗: {e}")
    
    async def run_all_tests(self):
        """すべてのテストを実行"""
        print("🚀 API動作テストを開始します...")
        
        try:
            # データベースセットアップ
            await self.setup_database()
            
            # テストユーザー作成
            await self.create_test_user()
            
            # 各APIのテスト
            await self.test_health_endpoints()
            await self.test_auth_api()
            await self.test_recording_api()
            await self.test_summary_api()
            await self.test_billing_api()
            
            print("\n✅ すべてのテストが完了しました！")
            
        except Exception as e:
            print(f"\n❌ テスト実行中にエラーが発生しました: {e}")
        
        finally:
            await self.client.aclose()

async def main():
    """メイン関数"""
    tester = APITester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 