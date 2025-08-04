from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

# パスワードハッシュ化の設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTPBearerスキーマ
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """パスワードを検証"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """パスワードをハッシュ化"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """アクセストークンを作成"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """トークンを検証"""
    try:
        print(f"DEBUG: verify_token 開始 - トークン長さ: {len(token)}")
        print(f"DEBUG: トークン先頭20文字: {token[:20]}")
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print(f"DEBUG: JWT デコード成功 - payload: {payload}")
        return payload
    except JWTError as e:
        print(f"DEBUG: JWT デコードエラー: {str(e)}")
        return None
    except Exception as e:
        print(f"DEBUG: verify_token 予期しないエラー: {str(e)}")
        return None

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """現在のユーザーを取得"""
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無効なトークンです",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="トークンにユーザー情報が含まれていません",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # ダミーユーザーの場合
        if user_id == 1:
            current_time = datetime.utcnow()
            user = User(
                id=1,
                email="dummy@example.com",
                name="テストユーザー",
                is_premium="true",
                usage_count=0,
                trial_start_date=current_time,
                created_at=current_time
            )
            return user
        
        # データベースからユーザーを取得
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ユーザーが見つかりません"
            )
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証に失敗しました"
        ) 