import os
import requests
import jwt
import re
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import AuthService
from app.utils.auth import create_access_token, get_current_user, get_password_hash, verify_password

router = APIRouter()
security = HTTPBearer()

def validate_email(email: str) -> bool:
    """メールアドレスの形式を検証"""
    # 基本的なメールアドレス形式の検証
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
    
    # 短すぎるユーザー名（2文字未満）を拒否
    username = email.split('@')[0]
    if len(username) < 2:
        return False
    
    # 数字のみのユーザー名を拒否
    if username.isdigit():
        return False
    
    # 架空のドメインをチェック
    suspicious_domains = [
        'example.com', 'test.com', 'fake.com', 'dummy.com', 'temp.com',
        'localhost', '127.0.0.1', '0.0.0.0', 'invalid.com', 'nonexistent.com',
        'anstuma.com', 'anstuma.net', 'anstuma.org', 'anstuma.info',
        'test.org', 'test.net', 'test.info', 'test.biz',
        'fake.org', 'fake.net', 'fake.info', 'fake.biz',
        'dummy.org', 'dummy.net', 'dummy.info', 'dummy.biz',
        'temp.org', 'temp.net', 'temp.info', 'temp.biz',
        'example.org', 'example.net', 'example.info', 'example.biz',
        'localhost.com', 'localhost.net', 'localhost.org',
        '127.0.0.1.com', '127.0.0.1.net', '127.0.0.1.org',
        '0.0.0.0.com', '0.0.0.0.net', '0.0.0.0.org',
        'invalid.org', 'invalid.net', 'invalid.info', 'invalid.biz',
        'nonexistent.org', 'nonexistent.net', 'nonexistent.info', 'nonexistent.biz'
    ]
    
    domain = email.split('@')[1].lower()
    if domain in suspicious_domains:
        return False
    
    # 架空のユーザー名パターンをチェック
    suspicious_usernames = [
        'test', 'fake', 'dummy', 'temp', 'admin', 'user', 'guest',
        'demo', 'sample', 'example', 'anonymous', 'unknown', 'nobody',
        'antasu', 'anstuma', 'testuser', 'fakeuser', 'dummyuser',
        'tempuser', 'adminuser', 'guestuser', 'demouser', 'sampleuser',
        'exampleuser', 'anonymoususer', 'unknownuser', 'nobodyuser',
        'a', 'aa', 'aaa', 'ab', 'abc', 'abcd', 'abcde',
        'q', 'qq', 'qqq', 'qqqq', 'qqqqq',
        '1', '11', '111', '1111', '11111',
        'x', 'xx', 'xxx', 'xxxx', 'xxxxx',
        'z', 'zz', 'zzz', 'zzzz', 'zzzzz',
        'kisitakanodesu', 'snskaizoku', 'akaisimituru'
    ]
    
    if username.lower() in suspicious_usernames:
        return False
    
    # 連続した文字や数字のパターン
    if re.match(r'^(.)\1{2,}$', username):  # 同じ文字が3回以上連続
        return False
    
    return True

def get_email_validation_error(email: str) -> str:
    """メールアドレスの検証エラーメッセージを取得"""
    # 基本的なメールアドレス形式の検証
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return "このメールアドレスは使用できません。正しいメールアドレスを入力してください。"
    
    # 短すぎるユーザー名（2文字未満）を拒否
    username = email.split('@')[0]
    if len(username) < 2:
        return "このメールアドレスは使用できません。メールアドレスの@より前の部分が短すぎます。"
    
    # 数字のみのユーザー名を拒否
    if username.isdigit():
        return "このメールアドレスは使用できません。数字のみのメールアドレスは使用できません。"
    
    # 架空のドメインをチェック
    suspicious_domains = [
        'example.com', 'test.com', 'fake.com', 'dummy.com', 'temp.com',
        'localhost', '127.0.0.1', '0.0.0.0', 'invalid.com', 'nonexistent.com',
        'anstuma.com', 'anstuma.net', 'anstuma.org', 'anstuma.info',
        'test.org', 'test.net', 'test.info', 'test.biz',
        'fake.org', 'fake.net', 'fake.info', 'fake.biz',
        'dummy.org', 'dummy.net', 'dummy.info', 'dummy.biz',
        'temp.org', 'temp.net', 'temp.info', 'temp.biz',
        'example.org', 'example.net', 'example.info', 'example.biz',
        'localhost.com', 'localhost.net', 'localhost.org',
        '127.0.0.1.com', '127.0.0.1.net', '127.0.0.1.org',
        '0.0.0.0.com', '0.0.0.0.net', '0.0.0.0.org',
        'invalid.org', 'invalid.net', 'invalid.info', 'invalid.biz',
        'nonexistent.org', 'nonexistent.net', 'nonexistent.info', 'nonexistent.biz'
    ]
    
    domain = email.split('@')[1].lower()
    if domain in suspicious_domains:
        return "このメールアドレスは使用できません。架空のドメインは使用できません。"
    
    # 架空のユーザー名パターンをチェック
    suspicious_usernames = [
        'test', 'fake', 'dummy', 'temp', 'admin', 'user', 'guest',
        'demo', 'sample', 'example', 'anonymous', 'unknown', 'nobody',
        'antasu', 'anstuma', 'testuser', 'fakeuser', 'dummyuser',
        'tempuser', 'adminuser', 'guestuser', 'demouser', 'sampleuser',
        'exampleuser', 'anonymoususer', 'unknownuser', 'nobodyuser',
        'a', 'aa', 'aaa', 'ab', 'abc', 'abcd', 'abcde',
        'q', 'qq', 'qqq', 'qqqq', 'qqqqq',
        '1', '11', '111', '1111', '11111',
        'x', 'xx', 'xxx', 'xxxx', 'xxxxx',
        'z', 'zz', 'zzz', 'zzzz', 'zzzzz',
        'kisitakanodesu', 'snskaizoku', 'akaisimituru'
    ]
    
    if username.lower() in suspicious_usernames:
        return "このメールアドレスは使用できません。架空のユーザー名は使用できません。"
    
    # 連続した文字や数字のパターン
    if re.match(r'^(.)\1{2,}$', username):  # 同じ文字が3回以上連続
        return "このメールアドレスは使用できません。不自然なパターンは使用できません。"
    
    return "このメールアドレスは使用できません。別のメールアドレスをお試しください。"

class GoogleAuthRequest(BaseModel):
    id_token: str

class LineAuthRequest(BaseModel):
    code: str

class EmailLoginRequest(BaseModel):
    email: EmailStr
    password: str

class EmailRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    data: dict = None

@router.post("/google", response_model=AuthResponse)
async def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Google OAuth認証"""
    try:
        print(f"DEBUG: Google認証開始 - トークン長さ: {len(request.id_token)}")
        
        # Googleトークンを検証
        google_response = requests.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={request.id_token}"
        )
        
        if google_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Googleトークンが無効です")
        
        google_data = google_response.json()
        email = google_data.get("email")
        name = google_data.get("name", "")
        picture = google_data.get("picture", "")
        
        if not email:
            raise HTTPException(status_code=400, detail="Google email not found")
        
        # メールアドレスの形式を検証
        if not validate_email(email):
            raise HTTPException(status_code=400, detail="無効なメールアドレス形式です")
        
        print(f"DEBUG: Google認証成功 - email: {email}")
        
        # ユーザーを取得または作成
        user = db.query(User).filter(User.email == email).first()
        is_new_user = False
        
        if not user:
            # 新規ユーザーを作成
            is_new_user = True
            user = User(
                email=email,
                name=name,
                profile_picture=picture,
                auth_provider="google",
                google_id=google_data.get("sub"), # Google IDを保存
                is_premium="true"  # Googleユーザーもプレミアムとして設定
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"DEBUG: Googleユーザー作成完了 - ID: {user.id}")
        else:
            print(f"DEBUG: 既存Googleユーザー取得 - ID: {user.id}")
            # 既存ユーザーの場合もプレミアム状態を確認・更新
            if user.is_premium != "true":
                user.is_premium = "true"
                db.commit()
                print(f"DEBUG: 既存Googleユーザーのプレミアム状態を更新")
        
        # アクセストークンを生成
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return AuthResponse(
            success=True,
            message="Google認証が成功しました",
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "is_new_user": is_new_user,
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
        is_new_user = False
        
        if not user:
            # LINEユーザーIDをメールアドレスとして使用（一意性のため）
            email = f"{line_user_id}@line.user"
            
            print(f"DEBUG: 新規LINEユーザー作成 - email: {email}, name: {name}")
            is_new_user = True
            
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
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return AuthResponse(
            success=True,
            message="LINE認証が成功しました",
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "is_new_user": is_new_user,
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

@router.post("/email/login", response_model=AuthResponse)
async def email_login(request: EmailLoginRequest, db: Session = Depends(get_db)):
    """メール・パスワードログイン"""
    try:
        print(f"DEBUG: メールログイン開始 - email: {request.email}")
        
        # ユーザーを取得
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(status_code=400, detail="メールアドレスまたはパスワードが正しくありません")
        
        # パスワードを検証
        if not verify_password(request.password, user.hashed_password):
            raise HTTPException(status_code=400, detail="メールアドレスまたはパスワードが正しくありません")
        
        # 無料プランの使用制限をチェック
        if user.is_premium == "false":
            # 無料プランは月10回まで
            if user.usage_count >= 10:
                raise HTTPException(status_code=400, detail="無料プランの利用回数上限に達しました。プレミアムプランにアップグレードしてください。")
        
        print(f"DEBUG: メールログイン成功 - email: {request.email}")
        
        # アクセストークンを生成
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return AuthResponse(
            success=True,
            message="ログインが成功しました",
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "profile_picture": user.profile_picture,
                    "is_premium": user.is_premium,
                    "usage_count": user.usage_count
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"メールログインエラー: {str(e)}")
        raise HTTPException(status_code=500, detail="ログインに失敗しました")

@router.post("/email/register", response_model=AuthResponse)
async def email_register(request: EmailRegisterRequest, db: Session = Depends(get_db)):
    """メール・パスワード登録"""
    try:
        print(f"DEBUG: メール登録開始 - email: {request.email}")
        
        # 既存ユーザーをチェック
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="このメールアドレスは既に登録されています")
        
        # メールアドレスの形式を検証
        print(f"DEBUG: メール検証開始 - {request.email}")
        if not validate_email(request.email):
            error_message = get_email_validation_error(request.email)
            print(f"DEBUG: メール検証失敗 - {request.email}: {error_message}")
            raise HTTPException(status_code=400, detail=error_message)
        
        print(f"DEBUG: メール検証成功 - {request.email}")

        # パスワードをハッシュ化
        hashed_password = get_password_hash(request.password)
        
        # 新規ユーザーを作成（直接アクティブ）
        user = User(
            email=request.email,
            name=request.name,
            hashed_password=hashed_password,
            auth_provider="email",
            is_premium="false",  # メール登録は無料プラン
            is_active="active"  # 直接アクティブにする
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"DEBUG: メール登録成功 - ID: {user.id}")
        
        # アクセストークンを生成
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return AuthResponse(
            success=True,
            message="登録が成功しました",
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "profile_picture": user.profile_picture,
                    "is_premium": user.is_premium,
                    "is_active": user.is_active
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"メール登録エラー: {str(e)}")
        raise HTTPException(status_code=500, detail="登録に失敗しました")

@router.get("/me", response_model=AuthResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """現在のユーザー情報を取得"""
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

@router.post("/logout")
async def logout():
    """ログアウト（クライアント側でトークンを削除）"""
    return {"message": "ログアウトしました"} 