from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import jwt
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.services.auth_service import AuthService
from app.middleware.rate_limit import create_rate_limit_decorator

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# レスポンスモデル
class AuthResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    is_premium: str
    usage_count: int
    trial_start_date: datetime
    created_at: Optional[datetime] = None

class GoogleAuthRequest(BaseModel):
    token: str

class LineAuthRequest(BaseModel):
    code: str

class UpdateUserRequest(BaseModel):
    name: Optional[str] = None

class UserStatsResponse(BaseModel):
    trial_remaining_days: int
    usage_remaining: int
    total_meetings: int
    completed_meetings: int

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

@router.post("/dummy", response_model=AuthResponse)
@create_rate_limit_decorator("dummy")
async def dummy_auth(db: Session = Depends(get_db)):
    """ダミー認証（テスト用）"""
    try:
        current_time = datetime.utcnow()
        
        # ダミーユーザーの作成
        user = User(
            id=1,
            email="dummy@example.com",
            name="テストユーザー",
            is_premium="false",
            usage_count=0,
            trial_start_date=current_time,
            created_at=current_time
        )
        
        # JWTトークンの生成
        auth_service = AuthService()
        access_token = auth_service.create_access_token(data={"sub": user.email})
        
        return AuthResponse(
            success=True,
            message="ダミー認証が成功しました",
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "user": UserResponse(
                    id=user.id,
                    email=user.email,
                    name=user.name,
                    is_premium=user.is_premium,
                    usage_count=user.usage_count,
                    trial_start_date=user.trial_start_date,
                    created_at=user.created_at
                ).dict()
            }
        )
    
    except Exception as e:
        print(f"dummy_auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ダミー認証に失敗しました: {str(e)}"
        )

@router.post("/google", response_model=AuthResponse)
async def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Google OAuth認証"""
    try:
        auth_service = AuthService()
        user_info = await auth_service.verify_google_token(request.token)
        
        # ユーザーの取得または作成
        user = db.query(User).filter(User.google_id == user_info["sub"]).first()
        if not user:
            # 同じメールアドレスのユーザーが存在するかチェック
            existing_user = db.query(User).filter(User.email == user_info["email"]).first()
            if existing_user:
                # 既存ユーザーにGoogle IDを追加
                existing_user.google_id = user_info["sub"]
                existing_user.name = user_info["name"]
                user = existing_user
            else:
                # 新規ユーザー作成
                user = User(
                    email=user_info["email"],
                    name=user_info["name"],
                    google_id=user_info["sub"],
                    is_premium="false",
                    usage_count=0,
                    trial_start_date=datetime.utcnow()
                )
                db.add(user)
            
            db.commit()
            db.refresh(user)
        
        # JWTトークンの生成
        access_token = auth_service.create_access_token(data={"sub": user.email})
        
        return AuthResponse(
            success=True,
            message="Google認証が成功しました",
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "user": UserResponse(
                    id=user.id,
                    email=user.email,
                    name=user.name,
                    is_premium=user.is_premium,
                    usage_count=user.usage_count,
                    trial_start_date=user.trial_start_date,
                    created_at=user.created_at
                ).dict()
            }
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"認証処理中にエラーが発生しました: {str(e)}"
        )

@router.post("/line", response_model=AuthResponse)
async def line_auth(request: LineAuthRequest, db: Session = Depends(get_db)):
    """LINE OAuth認証"""
    try:
        auth_service = AuthService()
        user_info = await auth_service.verify_line_token(request.code)
        
        # ユーザーの取得または作成
        user = db.query(User).filter(User.line_id == user_info["userId"]).first()
        if not user:
            # 同じメールアドレスのユーザーが存在するかチェック
            email = user_info.get("email", "")
            if email:
                existing_user = db.query(User).filter(User.email == email).first()
                if existing_user:
                    # 既存ユーザーにLINE IDを追加
                    existing_user.line_id = user_info["userId"]
                    existing_user.name = user_info["displayName"]
                    user = existing_user
                else:
                    # 新規ユーザー作成
                    user = User(
                        email=email,
                        name=user_info["displayName"],
                        line_id=user_info["userId"],
                        is_premium="false",
                        usage_count=0,
                        trial_start_date=datetime.utcnow()
                    )
                    db.add(user)
            else:
                # メールアドレスがない場合は新規作成
                user = User(
                    email=f"line_{user_info['userId']}@line.user",
                    name=user_info["displayName"],
                    line_id=user_info["userId"],
                    is_premium="false",
                    usage_count=0,
                    trial_start_date=datetime.utcnow()
                )
                db.add(user)
            
            db.commit()
            db.refresh(user)
        
        # JWTトークンの生成
        access_token = auth_service.create_access_token(data={"sub": user.email})
        
        return AuthResponse(
            success=True,
            message="LINE認証が成功しました",
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "user": UserResponse(
                    id=user.id,
                    email=user.email,
                    name=user.name,
                    is_premium=user.is_premium,
                    usage_count=user.usage_count,
                    trial_start_date=user.trial_start_date,
                    created_at=user.created_at
                ).dict()
            }
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"認証処理中にエラーが発生しました: {str(e)}"
        )

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """メールアドレスとパスワードでのログイン"""
    try:
        # 簡易的な認証（実際の実装ではパスワードハッシュ化が必要）
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="メールアドレスまたはパスワードが正しくありません"
            )
        
        # JWTトークンの生成
        auth_service = AuthService()
        access_token = auth_service.create_access_token(data={"sub": user.email})
        
        return AuthResponse(
            success=True,
            message="ログインが成功しました",
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "user": UserResponse(
                    id=user.id,
                    email=user.email,
                    name=user.name,
                    is_premium=user.is_premium,
                    usage_count=user.usage_count,
                    trial_start_date=user.trial_start_date,
                    created_at=user.created_at
                ).dict()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ログインに失敗しました: {str(e)}"
        )

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """新規ユーザー登録"""
    try:
        # 既存ユーザーをチェック
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="このメールアドレスは既に登録されています"
            )
        
        # 新規ユーザーを作成
        new_user = User(
            email=request.email,
            name=request.name,
            is_premium="false",
            usage_count=0,
            trial_start_date=datetime.utcnow()
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # JWTトークンの生成
        auth_service = AuthService()
        access_token = auth_service.create_access_token(data={"sub": new_user.email})
        
        return AuthResponse(
            success=True,
            message="ユーザー登録が成功しました",
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "user": UserResponse(
                    id=new_user.id,
                    email=new_user.email,
                    name=new_user.name,
                    is_premium=new_user.is_premium,
                    usage_count=new_user.usage_count,
                    trial_start_date=new_user.trial_start_date,
                    created_at=new_user.created_at
                ).dict()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ユーザー登録に失敗しました: {str(e)}"
        )

@router.get("/me", response_model=AuthResponse)
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """現在のユーザー情報を取得"""
    try:
        auth_service = AuthService()
        user_email = auth_service.verify_token(token)
        
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無効なトークンです"
            )
        
        # ダミーユーザーの場合
        if user_email == "dummy@example.com":
            current_time = datetime.utcnow()
            user = User(
                id=1,
                email="dummy@example.com",
                name="テストユーザー",
                is_premium="false",
                usage_count=0,
                trial_start_date=current_time,
                created_at=current_time
            )
        else:
            # データベースからユーザーを取得
            user = db.query(User).filter(User.email == user_email).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="ユーザーが見つかりません"
                )
        
        return AuthResponse(
            success=True,
            message="ユーザー情報を取得しました",
            data={
                "user": UserResponse(
                    id=user.id,
                    email=user.email,
                    name=user.name,
                    is_premium=user.is_premium,
                    usage_count=user.usage_count,
                    trial_start_date=user.trial_start_date,
                    created_at=user.created_at
                ).dict()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"get_current_user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ユーザー情報の取得に失敗しました: {str(e)}"
        )

@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """トークンの更新"""
    try:
        auth_service = AuthService()
        user_email = auth_service.verify_token(token)
        user = db.query(User).filter(User.email == user_email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ユーザーが見つかりません"
            )
        
        # 新しいトークンを生成
        new_access_token = auth_service.create_access_token(data={"sub": user.email})
        
        return AuthResponse(
            success=True,
            message="トークンを更新しました",
            data={
                "access_token": new_access_token,
                "token_type": "bearer"
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なトークンです"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"トークン更新に失敗しました: {str(e)}"
        )

@router.put("/me", response_model=AuthResponse)
async def update_user(
    request: UpdateUserRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """ユーザー情報の更新"""
    try:
        auth_service = AuthService()
        user_email = auth_service.verify_token(token)
        user = db.query(User).filter(User.email == user_email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ユーザーが見つかりません"
            )
        
        # 更新可能なフィールドのみ更新
        if request.name is not None:
            user.name = request.name
        
        db.commit()
        db.refresh(user)
        
        return AuthResponse(
            success=True,
            message="ユーザー情報を更新しました",
            data={
                "user": UserResponse(
                    id=user.id,
                    email=user.email,
                    name=user.name,
                    is_premium=user.is_premium,
                    usage_count=user.usage_count,
                    trial_start_date=user.trial_start_date,
                    created_at=user.created_at
                ).dict()
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なトークンです"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ユーザー情報の更新に失敗しました: {str(e)}"
        )

@router.get("/stats", response_model=AuthResponse)
async def get_user_stats(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """ユーザーの利用統計を取得"""
    try:
        auth_service = AuthService()
        user_email = auth_service.verify_token(token)
        user = db.query(User).filter(User.email == user_email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ユーザーが見つかりません"
            )
        
        # 統計情報を計算
        from app.models.meeting import Meeting
        
        total_meetings = db.query(Meeting).filter(Meeting.user_id == user.id).count()
        completed_meetings = db.query(Meeting).filter(
            Meeting.user_id == user.id,
            Meeting.status == "completed"
        ).count()
        
        # 無料期間と利用回数の残りを取得
        trial_remaining = auth_service.get_trial_remaining_days(user)
        usage_remaining = auth_service.get_usage_remaining(user)
        
        return AuthResponse(
            success=True,
            message="利用統計を取得しました",
            data={
                "stats": UserStatsResponse(
                    trial_remaining_days=trial_remaining,
                    usage_remaining=usage_remaining,
                    total_meetings=total_meetings,
                    completed_meetings=completed_meetings
                ).dict()
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なトークンです"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"統計情報の取得に失敗しました: {str(e)}"
        )

@router.get("/health")
async def auth_health_check():
    """認証APIのヘルスチェック"""
    return AuthResponse(
        success=True,
        message="認証APIは正常に動作しています",
        data={
            "version": "1.0.0",
            "endpoints": [
                "POST /api/auth/google",
                "POST /api/auth/line", 
                "GET /api/auth/me",
                "POST /api/auth/refresh",
                "PUT /api/auth/me",
                "GET /api/auth/stats"
            ]
        }
    ) 