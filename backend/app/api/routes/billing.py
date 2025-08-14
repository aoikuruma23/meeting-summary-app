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
from app.middleware.auth import get_current_user
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stripeチェックアウトセッションを作成"""
    try:
        # チェックアウトセッション作成
        result = billing_service.create_checkout_session(current_user, request.plan_id, db)
        
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stripeカスタマーポータルセッションを作成"""
    try:
        # ポータルセッション作成
        result = billing_service.create_portal_session(current_user, db)
        
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
        
        # Webhook処理
        result = billing_service.handle_webhook(payload, sig_header)
        
        return result
        
    except Exception as e:
        logger.error(f"Webhook処理エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook処理に失敗しました"
        )

@router.get("/access", response_model=dict)
async def check_access(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """アクセス権限をチェック"""
    try:
        # アクセス権限チェック
        has_access = billing_service.check_access(current_user, db)
        
        return has_access
        
    except Exception as e:
        logger.error(f"アクセス権限チェックエラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="アクセス権限チェックに失敗しました"
        )

@router.get("/subscription", response_model=dict)
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """サブスクリプション状態を取得"""
    try:
        print(f"DEBUG: get_subscription_status エンドポイント - user_id: {current_user.id}")
        
        # サブスクリプション状態取得
        subscription_info = billing_service.get_subscription_status(current_user, db)
        
        return {
            "success": True,
            "message": "サブスクリプション状態を取得しました",
            "data": subscription_info
        }
        
    except Exception as e:
        logger.error(f"サブスクリプション状況取得エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="サブスクリプション状態の取得に失敗しました"
        )

@router.get("/pricing", response_model=dict)
async def get_pricing_info():
    """価格情報を取得"""
    try:
        # 価格情報取得
        pricing_info = billing_service.get_pricing_info()
        
        return {
            "success": True,
            "message": "価格情報を取得しました",
            "data": pricing_info
        }
        
    except Exception as e:
        logger.error(f"価格情報取得エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="価格情報の取得に失敗しました"
        ) 