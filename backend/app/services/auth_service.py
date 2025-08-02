import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from google.oauth2 import id_token
from google.auth.transport import requests
from google.auth.exceptions import GoogleAuthError
from app.core.config import settings
from app.models.user import User
from app.core.database import get_db
from sqlalchemy.orm import Session

class AuthService:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            return None

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        # ダミーユーザー認証（既存）
        if email == "dummy@example.com" and password == "password":
            return User(
                id=1,
                email="dummy@example.com",
                name="テストユーザー",
                is_premium=False
            )
        return None

    def verify_google_token(self, id_token_str: str) -> Optional[Dict[str, Any]]:
        """Google IDトークンを検証"""
        try:
            # Googleの公開鍵でトークンを検証
            idinfo = id_token.verify_oauth2_token(
                id_token_str, 
                requests.Request(), 
                settings.GOOGLE_CLIENT_ID
            )
            
            # 発行者とクライアントIDを確認
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return idinfo
        except GoogleAuthError as e:
            print(f"Google認証エラー: {e}")
            return None
        except ValueError as e:
            print(f"トークン検証エラー: {e}")
            return None

    def get_or_create_user_from_google(self, google_user_info: Dict[str, Any], db: Session) -> User:
        """Googleユーザー情報からユーザーを取得または作成"""
        email = google_user_info.get('email')
        
        # 既存ユーザーを検索
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            # 既存ユーザーの情報を更新
            user.name = google_user_info.get('name', user.name)
            user.picture = google_user_info.get('picture', user.picture)
            db.commit()
            return user
        else:
            # 新規ユーザーを作成
            new_user = User(
                email=email,
                name=google_user_info.get('name', ''),
                picture=google_user_info.get('picture', ''),
                is_premium=False,
                auth_provider='google'
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user

    def login_with_google(self, id_token_str: str, db: Session) -> Optional[Dict[str, Any]]:
        """Googleログイン処理"""
        # Googleトークンを検証
        google_user_info = self.verify_google_token(id_token_str)
        if not google_user_info:
            return None
        
        # ユーザーを取得または作成
        user = self.get_or_create_user_from_google(google_user_info, db)
        
        # アクセストークンを生成
        access_token = self.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_premium": user.is_premium,
                "picture": user.picture
            }
        }
    
    async def verify_line_token(self, code: str) -> Dict[str, Any]:
        """LINE OAuthトークンを検証（簡易版）"""
        try:
            # 簡易版 - 実際の検証は無効化
            raise ValueError("LINE OAuthは現在無効化されています")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"LINEトークンの検証に失敗しました: {str(e)}")
    
    def is_trial_valid(self, user) -> bool:
        """無料期間が有効かチェック（簡易版）"""
        try:
            # 簡易版 - 常にTrueを返す
            return True
        except Exception as e:
            # エラーの場合は安全のためFalseを返す
            return False
    
    def get_trial_remaining_days(self, user) -> int:
        """無料期間の残り日数を取得（簡易版）"""
        try:
            # 簡易版 - 常に30日を返す
            return 30
        except Exception:
            return 0
    
    def get_usage_remaining(self, user) -> int:
        """残り利用回数を取得（簡易版）"""
        try:
            # 簡易版 - 常に10回を返す
            return 10
        except Exception:
            return 0
    
    def get_current_user_token(self, token: str) -> str:
        """現在のユーザートークンを取得（依存性注入用）"""
        return token 