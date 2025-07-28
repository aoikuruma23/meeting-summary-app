#!/usr/bin/env python3
"""
レート制限のテストスクリプト
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_rate_limit():
    """レート制限をテストする"""
    print("=== レート制限テスト開始 ===")
    
    # 1. ダミー認証でトークンを取得
    print("\n1. ダミー認証でトークンを取得...")
    auth_response = requests.post(f"{BASE_URL}/api/auth/dummy")
    if auth_response.status_code == 200:
        token = auth_response.json()["data"]["access_token"]
        print("✓ 認証成功")
    else:
        print("✗ 認証失敗")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 録音開始を複数回実行してレート制限をテスト
    print("\n2. 録音開始のレート制限テスト（3回/分）...")
    for i in range(5):
        print(f"  録音開始 {i+1}回目...")
        response = requests.post(
            f"{BASE_URL}/api/recording/start",
            headers=headers,
            json={"title": f"テスト録音{i+1}"}
        )
        
        if response.status_code == 200:
            print(f"  ✓ 成功 (ステータス: {response.status_code})")
        elif response.status_code == 429:
            print(f"  ✗ レート制限超過 (ステータス: {response.status_code})")
            error_detail = response.json()
            print(f"    詳細: {error_detail}")
        else:
            print(f"  ✗ エラー (ステータス: {response.status_code})")
            print(f"    詳細: {response.text}")
        
        time.sleep(1)  # 1秒待機
    
    # 3. 履歴取得のレート制限テスト
    print("\n3. 履歴取得のレート制限テスト（30回/分）...")
    for i in range(35):
        print(f"  履歴取得 {i+1}回目...")
        response = requests.get(f"{BASE_URL}/api/recording/list", headers=headers)
        
        if response.status_code == 200:
            print(f"  ✓ 成功 (ステータス: {response.status_code})")
        elif response.status_code == 429:
            print(f"  ✗ レート制限超過 (ステータス: {response.status_code})")
            error_detail = response.json()
            print(f"    詳細: {error_detail}")
            break
        else:
            print(f"  ✗ エラー (ステータス: {response.status_code})")
            print(f"    詳細: {response.text}")
        
        time.sleep(0.1)  # 0.1秒待機
    
    # 4. レート制限統計を取得
    print("\n4. レート制限統計を取得...")
    stats_response = requests.get(f"{BASE_URL}/rate-limit-stats")
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print("✓ 統計取得成功")
        print(f"  総リクエスト数: {stats.get('total_requests', 0)}")
        print(f"  レート制限されたリクエスト数: {stats.get('rate_limited_requests', 0)}")
    else:
        print("✗ 統計取得失敗")
    
    print("\n=== レート制限テスト完了 ===")

def test_rapid_requests():
    """高速リクエストでレート制限をテスト"""
    print("\n=== 高速リクエストテスト開始 ===")
    
    # ダミー認証でトークンを取得
    auth_response = requests.post(f"{BASE_URL}/api/auth/dummy")
    if auth_response.status_code != 200:
        print("✗ 認証失敗")
        return
    
    token = auth_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 高速でリクエストを送信
    print("高速リクエスト送信中...")
    start_time = time.time()
    
    for i in range(10):
        response = requests.get(f"{BASE_URL}/api/recording/list", headers=headers)
        print(f"リクエスト {i+1}: ステータス {response.status_code}")
        
        if response.status_code == 429:
            print("レート制限に到達しました！")
            break
    
    end_time = time.time()
    print(f"実行時間: {end_time - start_time:.2f}秒")
    print("=== 高速リクエストテスト完了 ===")

if __name__ == "__main__":
    print("レート制限テストを開始します...")
    print("注意: バックエンドサーバーが起動していることを確認してください")
    
    try:
        # サーバーの応答確認
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code == 200:
            print("✓ サーバーに接続できました")
        else:
            print("✗ サーバーに接続できません")
            exit(1)
        
        # テスト実行
        test_rate_limit()
        test_rapid_requests()
        
    except requests.exceptions.ConnectionError:
        print("✗ サーバーに接続できません。バックエンドサーバーが起動しているか確認してください。")
    except Exception as e:
        print(f"✗ テスト実行中にエラーが発生しました: {e}") 