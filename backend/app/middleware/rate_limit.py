from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, List
import time
import logging
from collections import defaultdict
import threading

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# リクエスト履歴を保存する辞書
request_history = defaultdict(list)
lock = threading.Lock()

# レート制限設定（開発用に緩和）
MAX_REQUESTS_PER_MINUTE = 100  # 1分間に100リクエストまで
MAX_REQUESTS_PER_HOUR = 1000   # 1時間に1000リクエストまで

def is_rate_limited(ip: str, endpoint: str) -> bool:
    """レート制限チェック"""
    current_time = time.time()
    
    with lock:
        # 古いリクエスト履歴を削除
        request_history[ip] = [
            req_time for req_time in request_history[ip] 
            if current_time - req_time < 3600  # 1時間前のデータを削除
        ]
        
        # 現在のリクエスト数をカウント
        recent_requests = [
            req_time for req_time in request_history[ip] 
            if current_time - req_time < 60  # 1分以内のリクエスト
        ]
        
        # レート制限チェック
        if len(recent_requests) >= MAX_REQUESTS_PER_MINUTE:
            logger.warning(f"レート制限超過 - IP: {ip}、エンドポイント: {endpoint}")
            return True
        
        # 新しいリクエストを記録
        request_history[ip].append(current_time)
        
        return False

async def rate_limit_logging_middleware(request: Request, call_next):
    """レート制限とログ記録を行うミドルウェア"""
    client_ip = request.client.host
    endpoint = request.url.path
    method = request.method
    
    logger.info(f"APIリクエスト開始 - IP: {client_ip}, エンドポイント: {endpoint}, メソッド: {method}")
    
    # レート制限チェック
    if is_rate_limited(client_ip, endpoint):
        logger.warning(f"レート制限超過 - IP: {client_ip}、エンドポイント: {endpoint}")
        raise HTTPException(status_code=429, detail="リクエストが多すぎます。しばらく待ってから再試行してください。")
    
    # リクエスト処理
    start_time = time.time()
    response = await call_next(request)
    end_time = time.time()
    
    # レスポンスログ
    logger.info(f"APIリクエスト完了 - IP: {client_ip}、エンドポイント: {endpoint}、ステータス: {response.status_code}")
    
    return response 