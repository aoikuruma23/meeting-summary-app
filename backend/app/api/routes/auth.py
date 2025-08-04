import os
import requests
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import AuthService
from app.utils.auth import create_access_token, get_current_user

router = APIRouter()
security = HTTPBearer()

class GoogleAuthRequest(BaseModel):
    token: str

class LineAuthRequest(BaseModel):
    code: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

@router.post("/google", response_model=AuthResponse)
async def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Google OAuth認証"""
    try:
        # Google IDトークンを検証
        google_response = requests.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={request.token}"
        )
        
        if google_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid Google token")
        
        google_data = google_response.json()
        email = google_data.get("email")
        name = google_data.get("name", "")
        picture = google_data.get("picture", "")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email not found in Google token")
        
        # ユーザーを取得または作成
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            user = User(
                email=email,
                name=name,
                profile_picture=picture,
                auth_provider="google"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # アクセストークンを生成
        access_token = create_access_token(data={"sub": user.email})
        
        return AuthResponse(
            success=True,
            message="Google認証が成功しました",
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "profile_picture": user.profile_picture,
                    "is_premium": user.is_premium
                }
            }
        )
        
    except Exception as e:
        print(f"Google認証エラー: {str(e)}")
        raise HTTPException(status_code=500, detail="Google認証に失敗しました")

@router.post("/line", response_model=AuthResponse)
async def line_auth(request: LineAuthRequest, db: Session = Depends(get_db)):
    """LINE OAuth認証"""
    try:
        print(f"DEBUG: LINE認証開始 - コード: {request.code[:10]}...")
        print(f"DEBUG: LINE設定 - Channel ID: {settings.LINE_CHANNEL_ID}")
        print(f"DEBUG: LINE設定 - Redirect URI: {settings.LINE_REDIRECT_URI}")
        
        # LINEアクセストークンを取得
        token_response = requests.post(
            "https://api.line.me/oauth2/v2.1/token",
            data={
                "grant_type": "authorization_code",
                "code": request.code,
                "redirect_uri": settings.LINE_REDIRECT_URI,
                "client_id": settings.LINE_CHANNEL_ID,
                "client_secret": settings.LINE_CHANNEL_SECRET
            }
        )
        
        print(f"DEBUG: LINE token response status: {token_response.status_code}")
        print(f"DEBUG: LINE token response: {token_response.text}")
        
        if token_response.status_code != 200:
            print(f"LINE token error: {token_response.text}")
            raise HTTPException(status_code=400, detail="LINE認証に失敗しました")
        
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="LINE access token not found")
        
        print(f"DEBUG: LINE access token取得成功")
        
        # LINEプロフィールを取得
        profile_response = requests.get(
            "https://api.line.me/v2/profile",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        print(f"DEBUG: LINE profile response status: {profile_response.status_code}")
        print(f"DEBUG: LINE profile response: {profile_response.text}")
        
        if profile_response.status_code != 200:
            raise HTTPException(status_code=400, detail="LINE profile取得に失敗しました")
        
        profile_data = profile_response.json()
        line_user_id = profile_data.get("userId")
        name = profile_data.get("displayName", "")
        picture = profile_data.get("pictureUrl", "")
        
        print(f"DEBUG: LINE profile data - userId: {line_user_id}, name: {name}")
        
        if not line_user_id:
            raise HTTPException(status_code=400, detail="LINE user ID not found")
        
        # ユーザーを取得または作成
        user = db.query(User).filter(User.line_user_id == line_user_id).first()
        
        if not user:
            # LINEユーザーIDをメールアドレスとして使用（一意性のため）
            email = f"{line_user_id}@line.user"
            
            print(f"DEBUG: 新規LINEユーザー作成 - email: {email}, name: {name}")
            
            user = User(
                email=email,
                name=name,
                profile_picture=picture,
                auth_provider="line",
                line_user_id=line_user_id,
                is_premium="true"  # LINEユーザーはプレミアムとして設定
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"DEBUG: LINEユーザー作成完了 - ID: {user.id}")
        else:
            print(f"DEBUG: 既存LINEユーザー取得 - ID: {user.id}")
            # 既存ユーザーの場合もプレミアム状態を確認・更新
            if user.is_premium != "true":
                user.is_premium = "true"
                db.commit()
                print(f"DEBUG: 既存LINEユーザーのプレミアム状態を更新")
        
        # アクセストークンを生成
        access_token = create_access_token(data={"sub": user.email})
        
        print(f"DEBUG: LINE認証成功 - ユーザー: {user.email}")
        
        return AuthResponse(
            success=True,
            message="LINE認証が成功しました",
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "profile_picture": user.profile_picture,
                    "is_premium": user.is_premium
                }
            }
        )
        
    except Exception as e:
        print(f"LINE認証エラー: {str(e)}")
        import traceback
        print(f"DEBUG: スタックトレース: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="LINE認証に失敗しました")

@router.get("/me", response_model=AuthResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """現在のユーザー情報を取得"""
    try:
        return AuthResponse(
            success=True,
            message="ユーザー情報を取得しました",
            data={
                "user": {
                    "id": current_user.id,
                    "email": current_user.email,
                    "name": current_user.name,
                    "profile_picture": current_user.profile_picture,
                    "is_premium": current_user.is_premium
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="ユーザー情報の取得に失敗しました")

@router.post("/logout")
async def logout():
    """ログアウト（クライアント側でトークンを削除）"""
    return {"message": "ログアウトしました"} 