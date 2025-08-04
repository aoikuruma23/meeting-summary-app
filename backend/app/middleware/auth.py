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
    print(f"DEBUG: トークン先頭20文字: {token[:20] if token else 'なし'}")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token)
        print(f"DEBUG: verify_token 結果: {payload}")
        
        if payload is None:
            print("DEBUG: payload が None")
            raise credentials_exception
            
        user_id: int = int(payload.get("sub"))
        print(f"DEBUG: user_id: {user_id}, 型: {type(user_id)}")
        
        if user_id is None:
            print("DEBUG: user_id が None")
            raise credentials_exception
            
    except Exception as e:
        print(f"DEBUG: 認証処理でエラー: {str(e)}")
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    print(f"DEBUG: データベースから取得したユーザー: {user.id if user else 'なし'}")
    
    if user is None:
        print("DEBUG: ユーザーが見つかりません")
        raise credentials_exception
        
    print(f"DEBUG: 認証成功 - user_id: {user.id}, email: {user.email}")
    return user

# 一時的に認証を無効化（テスト用）
def get_current_user_dummy():
    """ダミーユーザーを返す（テスト用）"""
    class DummyUser:
        id = 1
        username = "dummy_user"
        email = "dummy@example.com"
        is_active = "active"
    
    return DummyUser() 