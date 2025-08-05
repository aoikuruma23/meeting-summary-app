from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.utils.auth import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """現在のユーザーを取得（一時的にダミーユーザーを返す）"""
    print(f"DEBUG: get_current_user 開始 - トークン長さ: {len(token) if token else 0}")
    
    # 一時的にダミーユーザーを返す
    class DummyUser:
        id = 1
        email = "yukihiro3million@gmail.com"
        name = "Sato Yukihiro"
        is_premium = "true"
        username = "dummy_user"
        is_active = "active"
    
    print("DEBUG: ダミーユーザーを返します")
    return DummyUser()

# 一時的に認証を無効化（テスト用）
def get_current_user_dummy():
    """ダミーユーザーを返す（テスト用）"""
    class DummyUser:
        id = 1
        username = "dummy_user"
        email = "dummy@example.com"
        is_active = "active"
    
    return DummyUser() 