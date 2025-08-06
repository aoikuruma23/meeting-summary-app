#!/usr/bin/env python3
"""
ユーザーデータと履歴データを確認するデバッグスクリプト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.meeting import Meeting
from sqlalchemy import text

def debug_user_data():
    """ユーザーデータと履歴データを確認"""
    print("=== ユーザーデータ・履歴データ確認 ===")
    
    try:
        db = SessionLocal()
        print("✓ データベース接続成功")
        
        # ユーザーデータを確認
        users = db.query(User).all()
        print(f"✓ ユーザー数: {len(users)}")
        
        for user in users:
            print(f"\nユーザーID: {user.id}")
            print(f"  メール: {user.email}")
            print(f"  名前: {user.name}")
            print(f"  認証プロバイダー: {user.auth_provider}")
            print(f"  プレミアム: {user.is_premium}")
            print(f"  作成日時: {user.created_at}")
            
            # このユーザーの議事録を確認
            meetings = db.query(Meeting).filter(Meeting.user_id == user.id).all()
            print(f"  議事録数: {len(meetings)}")
            
            for meeting in meetings:
                print(f"    議事録ID: {meeting.id}")
                print(f"      タイトル: {meeting.title}")
                print(f"      ステータス: {meeting.status}")
                print(f"      作成日時: {meeting.created_at}")
                print(f"      要約あり: {'はい' if meeting.summary else 'いいえ'}")
        
        # 全議事録の確認
        all_meetings = db.query(Meeting).all()
        print(f"\n=== 全議事録数: {len(all_meetings)} ===")
        
        for meeting in all_meetings:
            print(f"議事録ID: {meeting.id}, ユーザーID: {meeting.user_id}, タイトル: {meeting.title}")
        
    except Exception as e:
        print(f"✗ エラー: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_user_data() 