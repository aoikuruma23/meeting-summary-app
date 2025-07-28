from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from app.core.config import settings

class AuthService:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def create_access_token(self, data: dict) -> str:
        """JWTアクセストークンを生成"""
        try:
            to_encode = data.copy()
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            to_encode.update({"exp": expire, "iat": datetime.utcnow()})
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            raise ValueError(f"トークン生成に失敗しました: {str(e)}")
    
    def verify_token(self, token: str) -> str:
        """JWTトークンを検証"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            if email is None:
                raise ValueError("無効なトークンです")
            
            # トークンの有効期限をチェック
            exp = payload.get("exp")
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                raise ValueError("トークンの有効期限が切れています")
            
            return email
        except jwt.ExpiredSignatureError:
            raise ValueError("トークンの有効期限が切れています")
        except jwt.InvalidTokenError:
            raise ValueError("無効なトークンです")
        except Exception as e:
            raise ValueError(f"トークン検証に失敗しました: {str(e)}")
    
    async def verify_google_token(self, token: str) -> Dict[str, Any]:
        """Google IDトークンを検証（簡易版）"""
        try:
            # 簡易版 - 実際の検証は無効化
            raise ValueError("Google OAuthは現在無効化されています")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Googleトークンの検証に失敗しました: {str(e)}")
    
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