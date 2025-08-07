import os
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any
import requests
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.core.database import get_db
from app.models.user import User
from app.core.config import settings

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# メール検証用の一時的なコード保存
verification_codes: Dict[str, Dict[str, Any]] = {}

class EmailRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class EmailLoginRequest(BaseModel):
    email: EmailStr
    password: str

class EmailVerifyRequest(BaseModel):
    email: EmailStr
    verification_code: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any] = {}

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def validate_email_format(email: str) -> bool:
    """基本的なメール形式の検証"""
    try:
        # PydanticのEmailStrで基本的な形式チェック
        EmailStr.validate(email)
        return True
    except:
        return False

def validate_email_username(email: str) -> bool:
    """ユーザー名の検証"""
    username = email.split('@')[0]
    
    # 短すぎるユーザー名を拒否
    if len(username) < 2:
        return False
    
    # 数字のみのユーザー名を拒否
    if username.isdigit():
        return False
    
    return True

def validate_email_domain(email: str) -> bool:
    """ドメインの基本的な検証"""
    domain = email.split('@')[1].lower()
    
    # 明らかに無効なドメインを拒否
    invalid_domains = [
        'example.com', 'test.com', 'invalid.com', 'fake.com',
        'temp.com', 'dummy.com', 'spam.com', 'trash.com'
    ]
    
    if domain in invalid_domains:
        return False
    
    return True

def validate_email(email: str) -> bool:
    """実用的なメール検証"""
    print(f"DEBUG: メール検証開始 - {email}")
    
    # 1. 基本的な形式チェック
    if not validate_email_format(email):
        print(f"DEBUG: メール形式エラー - {email}")
        return False
    
    # 2. ユーザー名チェック
    if not validate_email_username(email):
        print(f"DEBUG: ユーザー名エラー - {email}")
        return False
    
    # 3. ドメインチェック
    if not validate_email_domain(email):
        print(f"DEBUG: ドメインエラー - {email}")
        return False
    
    print(f"DEBUG: メール検証成功 - {email}")
    return True

def get_email_validation_error(email: str) -> str:
    """メール検証エラーメッセージを取得"""
    if not validate_email_format(email):
        return "このメールアドレスの形式が正しくありません。"
    
    if not validate_email_username(email):
        return "このメールアドレスのユーザー名が短すぎるか、数字のみです。"
    
    if not validate_email_domain(email):
        return "このメールアドレスは使用できません。"
    
    return "このメールアドレスは利用できません。正しいメールアドレスを入力してください。"

def send_verification_email(email: str, code: str) -> bool:
    """SendGridを使用してメール送信"""
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        api_key = os.getenv("SENDGRID_API_KEY")
        from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@yourdomain.com")
        
        if not api_key:
            print("DEBUG: SendGrid APIキーが設定されていません")
            return False
        
        message = Mail(
            from_email=from_email,
            to_emails=email,
            subject="メールアドレス確認",
            html_content=f"""
            <h2>メールアドレス確認</h2>
            <p>以下の確認コードを入力してください：</p>
            <h1 style="font-size: 2em; color: #007bff;">{code}</h1>
            <p>このコードは10分間有効です。</p>
            """
        )
        
        sg = SendGridAPIClient(api_key=api_key)
        response = sg.send(message)
        
        # 成功ステータスコードをチェック
        if response.status_code in [200, 201, 202]:
            print(f"DEBUG: メール送信成功 - {email}")
            return True
        else:
            print(f"DEBUG: メール送信失敗 - {email}, ステータス: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"DEBUG: メール送信エラー - {email}: {e}")
        return False

class GoogleAuthRequest(BaseModel):
    id_token: str

class LineAuthRequest(BaseModel):
    code: str

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
    """メールアドレスログイン"""
    print(f"DEBUG: メールログイン開始 - メール: {request.email}")
    
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="メールアドレスまたはパスワードが正しくありません")
    
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="メールアドレスまたはパスワードが正しくありません")
    
    # アクティブユーザーのみログイン可能
    if user.is_active != "active":
        raise HTTPException(status_code=400, detail="メールアドレスの確認が必要です")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    print(f"DEBUG: メールログイン成功 - メール: {request.email}")
    
    return AuthResponse(
        success=True,
        message="ログインが成功しました",
        data={
            "access_token": access_token,
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

@router.post("/email/register", response_model=AuthResponse)
async def email_register(request: EmailRegisterRequest, db: Session = Depends(get_db)):
    """メールアドレス登録"""
    print(f"DEBUG: メール登録開始 - メール: {request.email}")
    
    # メールアドレス検証
    if not validate_email(request.email):
        error_msg = get_email_validation_error(request.email)
        raise HTTPException(status_code=400, detail=error_msg)
    
    # 既存ユーザーチェック
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="このメールアドレスは既に登録されています")
    
    # パスワードハッシュ化
    hashed_password = get_password_hash(request.password)
    
    # ユーザー作成
    user = User(
        email=request.email,
        name=request.name,
        hashed_password=hashed_password,
        auth_provider="email",
        is_premium="false",
        is_active="pending"  # メール確認待ち
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 確認コード生成
    verification_code = ''.join(secrets.choice('0123456789') for _ in range(6))
    verification_codes[request.email] = {
        'code': verification_code,
        'user_id': user.id,
        'expires': datetime.utcnow() + timedelta(minutes=10)
    }
    
    # 確認メール送信
    if send_verification_email(request.email, verification_code):
        print(f"DEBUG: メール登録成功 - ID: {user.id}")
        return AuthResponse(
            success=True,
            message="登録が完了しました。確認メールを送信しました。",
            data={
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
    else:
        # メール送信失敗時はユーザーを削除
        db.delete(user)
        db.commit()
        raise HTTPException(status_code=400, detail="メール送信に失敗しました。このメールアドレスは利用できません。")

@router.post("/email/verify", response_model=AuthResponse)
async def email_verify(request: EmailVerifyRequest, db: Session = Depends(get_db)):
    """メールアドレス確認"""
    if request.email not in verification_codes:
        raise HTTPException(status_code=400, detail="確認コードが見つかりません")
    
    code_data = verification_codes[request.email]
    
    # 有効期限チェック
    if datetime.utcnow() > code_data['expires']:
        del verification_codes[request.email]
        raise HTTPException(status_code=400, detail="確認コードの有効期限が切れています")
    
    # コード確認
    if request.verification_code != code_data['code']:
        raise HTTPException(status_code=400, detail="確認コードが正しくありません")
    
    # ユーザーをアクティブ化
    user = db.query(User).filter(User.id == code_data['user_id']).first()
    if not user:
        raise HTTPException(status_code=400, detail="ユーザーが見つかりません")
    
    user.is_active = "active"
    db.commit()
    
    # 確認コードを削除
    del verification_codes[request.email]
    
    # アクセストークン生成
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return AuthResponse(
        success=True,
        message="メールアドレスが確認されました",
        data={
            "access_token": access_token,
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

@router.get("/me", response_model=AuthResponse)
async def get_current_user_info(current_user: User = Depends(get_db().query(User).filter(User.id == verify_token(oauth2_scheme.tokenUrl)["sub"]).first())):
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