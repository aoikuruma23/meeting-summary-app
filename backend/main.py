from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
from app.core.config import settings
from app.api.routes import auth, recording, summary, billing
from app.core.database import engine, Base
from app.middleware.rate_limit import rate_limit_logging_middleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # アプリケーション起動時の処理
    Base.metadata.create_all(bind=engine)
    yield
    # アプリケーション終了時の処理

app = FastAPI(
    title="議事録要約Webアプリ",
    description="会議音声を自動で文字起こし・要約するWebアプリケーション",
    version="1.0.0",
    lifespan=lifespan
)

# レート制限ログミドルウェアを追加
@app.middleware("http")
async def rate_limit_logging(request: Request, call_next):
    return await rate_limit_logging_middleware(request, call_next)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173",
        "https://meeting-summary-app.vercel.app",  # Vercelフロントエンド
        "https://meeting-summary-app-frontend.vercel.app",  # 代替URL
        "https://meeting-summary-app.onrender.com",  # Renderフロントエンド
        "https://meeting-summary-app-frontend.onrender.com"  # Renderフロントエンド代替
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(auth.router, prefix="/api/auth", tags=["認証"])
app.include_router(recording.router, prefix="/api/recording", tags=["録音"])
app.include_router(summary.router, prefix="/api/summary", tags=["要約"])
app.include_router(billing.router, prefix="/api/billing", tags=["課金"])

@app.get("/")
async def root():
    return {"message": "議事録要約Webアプリ API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/rate-limit-stats")
async def get_rate_limit_stats():
    """レート制限統計を取得"""
    from app.middleware.rate_limit import get_rate_limit_stats
    return get_rate_limit_stats()

@app.post("/rate-limit-stats/reset")
async def reset_rate_limit_stats():
    """レート制限統計をリセット"""
    from app.middleware.rate_limit import reset_rate_limit_stats
    reset_rate_limit_stats()
    return {"message": "レート制限統計をリセットしました"}

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False  # 本番環境ではreloadを無効化
    ) 