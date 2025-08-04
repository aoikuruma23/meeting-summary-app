import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, recording, summary, billing
from app.core.database import engine, Base
from app.middleware.rate_limit import rate_limit_logging_middleware

# データベーステーブルを作成
Base.metadata.create_all(bind=engine)

# マイグレーションを実行
try:
    from run_migration import run_migration
    print("データベースマイグレーションを実行中...")
    run_migration()
    print("マイグレーション完了")
except Exception as e:
    print(f"マイグレーションエラー（無視可能）: {e}")

app = FastAPI(title="Meeting Summary API", version="1.0.0")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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