from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta
from app.core.database import Base

def jst_now():
    """日本時間（JST）の現在時刻を返す"""
    jst = timezone(timedelta(hours=9))
    return datetime.now(jst)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)
    is_active = Column(String, default="active")
    
    # ユーザー情報
    name = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    is_premium = Column(String, default="false")
    usage_count = Column(Integer, default=0)
    trial_start_date = Column(DateTime, default=jst_now)
    
    # OAuth関連
    auth_provider = Column(String, nullable=True)  # "google", "line", "email"
    google_id = Column(String, nullable=True)
    line_user_id = Column(String, nullable=True)
    
    # Stripe関連
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    
    # メタデータ（日本時間で保存）
    created_at = Column(DateTime, default=jst_now)
    updated_at = Column(DateTime, default=jst_now, onupdate=jst_now)
    
    # リレーション
    # meetings = relationship("Meeting", back_populates="user")  # 一時的にコメントアウト
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>" 