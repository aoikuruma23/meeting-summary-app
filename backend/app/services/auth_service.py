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

    def verify_token(self, token: str) -> Optional[str]:
        """JWTトークンを検証してユーザーIDを返す"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload.get("sub")  # ユーザーIDを返す
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
    
    def get_or_create_user_from_line(self, line_user_info: Dict[str, Any], db: Session) -> User:
        """LINEユーザー情報からユーザーを取得または作成"""
        line_user_id = line_user_info.get('userId')
        email = line_user_info.get('email', f"line_{line_user_id}@line.user")
        
        # 既存ユーザーを検索
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            # 既存ユーザーの情報を更新
            user.name = line_user_info.get('displayName', user.name)
            user.picture = line_user_info.get('pictureUrl', user.picture)
            db.commit()
            return user
        else:
            # 新規ユーザーを作成
            new_user = User(
                email=email,
                name=line_user_info.get('displayName', ''),
                picture=line_user_info.get('pictureUrl', ''),
                is_premium=False,
                auth_provider='line'
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user

    async def verify_line_token(self, code: str) -> Dict[str, Any]:
        """LINE OAuth2.0トークンを検証"""
        try:
            import requests
            
            # LINE OAuth2.0トークンエンドポイント
            token_url = "https://api.line.me/oauth2/v2.1/token"
            
            # アクセストークンを取得
            token_data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': settings.LINE_REDIRECT_URI,
                'client_id': settings.LINE_CHANNEL_ID,
                'client_secret': settings.LINE_CHANNEL_SECRET,
            }
            
            token_response = requests.post(token_url, data=token_data)
            token_response.raise_for_status()
            token_info = token_response.json()
            
            # ユーザー情報を取得
            profile_url = "https://api.line.me/v2/profile"
            headers = {
                'Authorization': f"Bearer {token_info['access_token']}"
            }
            
            profile_response = requests.get(profile_url, headers=headers)
            profile_response.raise_for_status()
            user_info = profile_response.json()
            
            return user_info
            
        except Exception as e:
            print(f"LINE認証エラー: {e}")
            raise ValueError(f"LINE認証に失敗しました: {str(e)}")

    def is_trial_valid(self, user) -> bool:
        """無料期間が有効かチェック"""
        if user.is_premium == "true":
            return True
        
        trial_end = user.trial_start_date + timedelta(days=31)
        return datetime.utcnow() < trial_end

    def get_trial_remaining_days(self, user) -> int:
        """無料期間の残り日数を取得"""
        if user.is_premium == "true":
            return 999  # プレミアムユーザー
        
        trial_end = user.trial_start_date + timedelta(days=31)
        remaining = (trial_end - datetime.utcnow()).days
        return max(0, remaining)

    def get_usage_remaining(self, user) -> int:
        """残り利用回数を取得"""
        if user.is_premium == "true":
            return 999  # プレミアムユーザー
        
        used = user.usage_count
        return max(0, 10 - used)

    def get_current_user_token(self, token: str) -> str:
        """現在のユーザーのトークンを取得"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload.get("sub")
        except jwt.PyJWTError:
            raise ValueError("無効なトークンです") 