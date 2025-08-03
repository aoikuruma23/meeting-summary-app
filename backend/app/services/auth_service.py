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

    async def verify_google_token(self, id_token_str: str) -> Optional[Dict[str, Any]]:
        """Google IDトークンを検証"""
        try:
            print(f"DEBUG: Googleトークン検証開始 - トークン長さ: {len(id_token_str) if id_token_str else 0}")
            
            # Google OAuth設定が未完了の場合
            if not settings.GOOGLE_CLIENT_ID or settings.GOOGLE_CLIENT_ID in ["your-google-client-id", "test-google-client-id", "your-actual-google-client-id.apps.googleusercontent.com"]:
                print("DEBUG: Google OAuth設定が未完了")
                raise ValueError("Google OAuth設定が完了していません。管理者に連絡してください。")
            
            print(f"DEBUG: Googleトークン検証実行 - Client ID: {settings.GOOGLE_CLIENT_ID}")
            
            # トークンの形式を確認（IDトークンかアクセストークンか）
            if id_token_str.startswith('ya29.'):
                # アクセストークンの場合、Google People APIを使用してユーザー情報を取得
                print("DEBUG: アクセストークンを検出、Google People APIを使用")
                return await self.get_user_info_from_access_token(id_token_str)
            else:
                # IDトークンの場合、直接検証
                print("DEBUG: IDトークンを検出、直接検証")
                idinfo = id_token.verify_oauth2_token(
                    id_token_str, 
                    requests.Request(), 
                    settings.GOOGLE_CLIENT_ID
                )
                
                print(f"DEBUG: Googleトークン検証成功 - 発行者: {idinfo.get('iss')}, クライアントID: {idinfo.get('aud')}")
                
                # 発行者とクライアントIDを確認
                if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                    print(f"DEBUG: 発行者が無効 - 発行者: {idinfo['iss']}")
                    raise ValueError('Wrong issuer.')
                
                return idinfo
        except GoogleAuthError as e:
            print(f"DEBUG: Google認証エラー (GoogleAuthError): {e}")
            return None
        except ValueError as e:
            print(f"DEBUG: トークン検証エラー (ValueError): {e}")
            return None
        except Exception as e:
            print(f"DEBUG: 予期しないエラー (Exception): {e}")
            return None

    async def get_user_info_from_access_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """アクセストークンを使用してGoogle People APIからユーザー情報を取得"""
        try:
            import requests
            
            # Google People APIを使用してユーザー情報を取得
            url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            user_info = response.json()
            
            print(f"DEBUG: Google People APIからユーザー情報を取得: {user_info}")
            
            # IDトークンと同じ形式に変換
            return {
                'sub': user_info['id'],
                'email': user_info['email'],
                'name': user_info.get('name', ''),
                'picture': user_info.get('picture', ''),
                'iss': 'accounts.google.com',
                'aud': settings.GOOGLE_CLIENT_ID
            }
            
        except Exception as e:
            print(f"DEBUG: Google People APIエラー: {e}")
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