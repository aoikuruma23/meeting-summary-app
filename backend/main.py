import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, recording, summary, billing
from app.core.database import engine, Base
from app.middleware.rate_limit import rate_limit_logging_middleware

# データベーステーブルを作成（既存データは保持）
print("データベーステーブルを作成中...")
Base.metadata.create_all(bind=engine)
print("✓ データベーステーブルの作成完了")

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

# CORS設定
origins = [
    "https://meeting-summary-app.jibunkaikaku-lab.com",
    "https://meeting-summary-app-backend.jibunkaikaku-lab.com",
    "https://meeting-summary-app.onrender.com",
    "https://meeting-summary-app-backend.onrender.com",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# レート制限ミドルウェアを追加
@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    return await rate_limit_logging_middleware(request, call_next)

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

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    ) 