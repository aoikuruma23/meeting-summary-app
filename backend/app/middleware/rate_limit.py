from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, List
import time
import logging
from collections import defaultdict

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# レート制限の状態管理
rate_limit_store: Dict[str, List[float]] = defaultdict(list)

# レート制限の設定
RATE_LIMITS = {
    # 認証関連
    "auth": {
        "login": "5/minute",      # ログイン試行: 5回/分
        "register": "3/hour",     # 登録: 3回/時
        "dummy": "10/minute",     # ダミーログイン: 10回/分
    },
    
    # 録音関連
    "recording": {
        "start": "3/minute",      # 録音開始: 3回/分
        "chunk": "60/minute",     # チャンクアップロード: 60回/分
        "end": "5/minute",        # 録音終了: 5回/分
        "list": "30/minute",      # 履歴取得: 30回/分
        "summary": "20/minute",   # 要約取得: 20回/分
        "export": "10/hour",      # エクスポート: 10回/時
    },
    
    # その他
    "general": {
        "health": "100/minute",   # ヘルスチェック: 100回/分
        "storage": "20/minute",   # ストレージ情報: 20回/分
    }
}

def get_rate_limit(endpoint: str) -> str:
    """エンドポイントに応じたレート制限を取得"""
    for category, limits in RATE_LIMITS.items():
        for key, limit in limits.items():
            if key in endpoint:
                return limit
    
    # デフォルト制限
    return "30/minute"

def get_client_ip(request: Request) -> str:
    """クライアントIPを取得"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host

def check_rate_limit(client_ip: str, endpoint: str, limit: str) -> bool:
    """レート制限をチェック"""
    current_time = time.time()
    key = f"{client_ip}:{endpoint}"
    
    # 制限を解析
    if "/minute" in limit:
        count, unit = limit.split("/")
        window = 60  # 60秒
    elif "/hour" in limit:
        count, unit = limit.split("/")
        window = 3600  # 3600秒
    else:
        return True  # 制限なし
    
    max_requests = int(count)
    
    # 古いリクエストを削除
    rate_limit_store[key] = [t for t in rate_limit_store[key] if current_time - t < window]
    
    # 現在のリクエスト数をチェック
    if len(rate_limit_store[key]) >= max_requests:
        logger.warning(f"レート制限超過 - IP: {client_ip}, エンドポイント: {endpoint}")
        return False
    
    # 新しいリクエストを追加
    rate_limit_store[key].append(current_time)
    logger.info(f"レート制限チェック - IP: {client_ip}, エンドポイント: {endpoint}, 現在のリクエスト数: {len(rate_limit_store[key])}")
    return True

def create_rate_limit_decorator(endpoint: str):
    """レート制限デコレータを作成（無効化）"""
    # デコレータを無効化して、ミドルウェアでレート制限を実装
    def decorator(func):
        return func
    return decorator

# ユーザー別レート制限（プレミアムユーザーは緩和）
def get_user_rate_limit(user_type: str, base_limit: str) -> str:
    """ユーザータイプに応じたレート制限を取得"""
    if user_type == "premium":
        # プレミアムユーザーは制限を緩和
        if "minute" in base_limit:
            count, unit = base_limit.split("/")
            return f"{int(count) * 3}/{unit}"
        elif "hour" in base_limit:
            count, unit = base_limit.split("/")
            return f"{int(count) * 2}/{unit}"
    
    return base_limit 

# レート制限の動作確認用ミドルウェア
async def rate_limit_logging_middleware(request: Request, call_next):
    """レート制限の動作をログに記録するミドルウェア"""
    client_ip = get_client_ip(request)
    endpoint = request.url.path
    
    # リクエスト開始をログに記録
    logger.info(f"APIリクエスト開始 - IP: {client_ip}, エンドポイント: {endpoint}, メソッド: {request.method}")
    
    # レート制限チェック
    limit = get_rate_limit(endpoint)
    if not check_rate_limit(client_ip, endpoint, limit):
        logger.warning(f"レート制限超過 - IP: {client_ip}, エンドポイント: {endpoint}")
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "レート制限を超過しました",
                "retry_after": 60,
                "limit": limit,
                "message": "しばらく待ってから再試行してください（60秒後）"
            }
        )
    
    # レスポンスを取得
    response = await call_next(request)
    
    # レスポンスをログに記録
    logger.info(f"APIリクエスト完了 - IP: {client_ip}, エンドポイント: {endpoint}, ステータス: {response.status_code}")
    
    return response

# レート制限統計
rate_limit_stats = {
    "total_requests": 0,
    "rate_limited_requests": 0,
    "endpoints": {}
}

def get_rate_limit_stats():
    """レート制限統計を取得"""
    return rate_limit_stats

def reset_rate_limit_stats():
    """レート制限統計をリセット"""
    global rate_limit_stats
    rate_limit_stats = {
        "total_requests": 0,
        "rate_limited_requests": 0,
        "endpoints": {}
    } 