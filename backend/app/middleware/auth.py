from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.utils.auth import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """現在のユーザーを取得"""
    print(f"DEBUG: get_current_user 開始 - トークン長さ: {len(token) if token else 0}")
    
    try:
        # トークンを検証してペイロードを取得
        payload = verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無効なトークンです"
            )
        
        # ペイロードからユーザーIDを取得
        user_id = int(payload.get("sub"))
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="トークンにユーザー情報が含まれていません"
            )
        
        # データベースからユーザーを取得
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="ユーザーが見つかりません"
            )
        
        print(f"DEBUG: ユーザー取得成功 - ID: {user.id}, Email: {user.email}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: 認証エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証に失敗しました"
        )

# 一時的に認証を無効化（テスト用）
def get_current_user_dummy():
    """ダミーユーザーを返す（テスト用）"""
    class DummyUser:
        id = 1
        username = "dummy_user"
        email = "dummy@example.com"
        is_active = "active"
    
    return DummyUser() 