import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.routes import auth, recording, summary, billing
from app.core.database import engine, Base
from app.middleware.rate_limit import rate_limit_logging_middleware

# データベーステーブルを作成（既存データは保持）
print("データベーステーブルを作成中...")
try:
    from app.core.database import create_tables
    create_tables()
    print("✓ データベーステーブルの作成完了")
except Exception as e:
    print(f"⚠️ データベーステーブル作成エラー: {e}")
    print("⚠️ アプリケーションは起動を継続します")

# マイグレーションを実行（念のため）
try:
    from run_migration import run_migration
    print("データベースマイグレーションを実行中...")
    run_migration()
    print("マイグレーション完了")
except Exception as e:
    print(f"マイグレーションエラー（無視可能）: {e}")

# ユーザープレミアム状態を修正
try:
    from fix_user_premium import fix_user_premium_status
    print("ユーザープレミアム状態を修正中...")
    fix_user_premium_status()
    print("ユーザープレミアム状態修正完了")
except Exception as e:
    print(f"ユーザープレミアム状態修正エラー（無視可能）: {e}")

app = FastAPI(title="Meeting Summary API", version="1.0.0")

# CORS設定 - より包括的に設定
origins = [
    "https://meeting-summary-app.jibunkaikaku-lab.com",
    "https://meeting-summary-app-backend.jibunkaikaku-lab.com",
    "https://meeting-summary-app.onrender.com",
    "https://meeting-summary-app-backend.onrender.com",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
    # 開発環境用
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
]

# 環境変数から追加のオリジンを取得
env_origins = os.environ.get("ALLOWED_ORIGINS", "")
if env_origins:
    try:
        import json
        additional_origins = json.loads(env_origins)
        if isinstance(additional_origins, list):
            origins.extend(additional_origins)
    except:
        pass

print(f"CORS設定 - 許可されるオリジン: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# レート制限ミドルウェアを追加
@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    return await rate_limit_logging_middleware(request, call_next)

# グローバルエラーハンドラー
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    print(f"グローバルエラー: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

# APIルーターを追加
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(recording.router, prefix="/api/recording", tags=["recording"])
app.include_router(summary.router, prefix="/api/summary", tags=["summary"])
app.include_router(billing.router, prefix="/api/billing", tags=["billing"])

@app.get("/")
async def root():
    return {"message": "Meeting Summary API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running normally"}

@app.get("/db-status")
async def database_status():
    """データベース接続状況を確認"""
    try:
        from app.core.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            return {
                "status": "connected",
                "message": "データベース接続成功",
                "test_result": result.fetchone()
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"データベース接続エラー: {str(e)}",
            "suggestion": "環境変数 DB_HOST, DB_USER, DB_PASSWORD を確認してください"
        }

@app.get("/cors-test")
async def cors_test():
    return {"message": "CORS test successful", "origins": origins}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    ) 