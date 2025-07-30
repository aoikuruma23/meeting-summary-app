from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.services.billing_service import BillingService
from app.services.auth_service import AuthService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
billing_service = BillingService()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# リクエストモデル
class CheckoutRequest(BaseModel):
    plan_id: str

class PortalRequest(BaseModel):
    return_url: str

class AccessCheckResponse(BaseModel):
    hasAccess: bool

@router.post("/checkout", response_model=dict)
async def create_checkout_session(
    request: CheckoutRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Stripeチェックアウトセッションを作成"""
    try:
        # ユーザー認証
        auth_service = AuthService()
        user_email = auth_service.verify_token(token)
        user = db.query(User).filter(User.email == user_email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ユーザーが見つかりません"
            )
        
        # チェックアウトセッション作成
        result = billing_service.create_checkout_session(user, request.plan_id, db)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"チェックアウトセッション作成エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="チェックアウトセッション作成に失敗しました"
        )

@router.post("/portal", response_model=dict)
async def create_portal_session(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Stripeカスタマーポータルセッションを作成"""
    try:
        # ユーザー認証
        auth_service = AuthService()
        user_email = auth_service.verify_token(token)
        user = db.query(User).filter(User.email == user_email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ユーザーが見つかりません"
            )
        
        # ポータルセッション作成
        result = billing_service.create_portal_session(user)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ポータルセッション作成エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ポータルセッション作成に失敗しました"
        )

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Stripe Webhookを処理"""
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        if not sig_header:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stripe署名が見つかりません"
            )
        
        result = billing_service.handle_webhook(payload, sig_header)
        
        if not result["success"]:
            logger.error(f"Webhook処理エラー: {result.get('error', 'Unknown error')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Webhook処理に失敗しました"
            )
        
        return {"success": True, "message": result.get("message", "Webhook処理完了")}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook処理エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook処理に失敗しました"
        )

@router.get("/access", response_model=dict)
async def check_access(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """ユーザーのアクセス権限をチェック"""
    try:
        # ユーザー認証
        auth_service = AuthService()
        user_email = auth_service.verify_token(token)
        user = db.query(User).filter(User.email == user_email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ユーザーが見つかりません"
            )
        
        # アクセス権限チェック
        result = billing_service.check_access(user)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"アクセス権限チェックエラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="アクセス権限チェックに失敗しました"
        )

@router.get("/subscription", response_model=dict)
async def get_subscription_status(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """ユーザーのサブスクリプション状況を取得"""
    try:
        # ユーザー認証
        auth_service = AuthService()
        user_email = auth_service.verify_token(token)
        print(f"DEBUG: get_subscription_status endpoint - user_email: {user_email}")
        user = db.query(User).filter(User.email == user_email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ユーザーが見つかりません"
            )
        
        print(f"DEBUG: get_subscription_status endpoint - found user: id={user.id}, email={user.email}, is_premium={user.is_premium}")
        # サブスクリプション状況を取得
        result = billing_service.get_subscription_status(user)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"サブスクリプション状況取得エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="サブスクリプション状況取得に失敗しました"
        )

@router.get("/pricing", response_model=dict)
async def get_pricing_info():
    """料金プラン情報を取得"""
    try:
        result = billing_service.get_pricing_info()
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"価格情報取得エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="価格情報取得に失敗しました"
        ) 