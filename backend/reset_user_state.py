#!/usr/bin/env python3
"""
テスト用: 指定メールのユーザー状態をリセット/削除するユーティリティ

使い方例:
  - リセット（無料へ戻す＋Stripeサブスク/顧客削除＋使用回数/トライアル初期化）
      python backend/reset_user_state.py --email someone@example.com --action reset

  - 完全削除（関連議事録も削除）
      python backend/reset_user_state.py --email someone@example.com --action delete --purge-meetings

注意:
  - 本番Stripeキーで実行すると、実顧客/サブスクリプションを削除します。用途を理解の上で実行してください。
"""

import argparse
import sys
import os
from typing import Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import stripe  # type: ignore
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User
from app.models.meeting import Meeting


def init_stripe() -> None:
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
    except Exception:
        pass


def find_user_by_email(db, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def cancel_stripe_resources(user: User) -> None:
    """ユーザーに紐づくStripeサブスク/顧客を削除(キャンセル)する"""
    try:
        if user.stripe_subscription_id:
            try:
                stripe.Subscription.delete(user.stripe_subscription_id)
                print(f"✓ Stripe サブスクリプション削除: {user.stripe_subscription_id}")
            except Exception as e:
                print(f"! Stripe サブスクリプション削除失敗: {e}")
        if user.stripe_customer_id:
            try:
                stripe.Customer.delete(user.stripe_customer_id)
                print(f"✓ Stripe 顧客削除: {user.stripe_customer_id}")
            except Exception as e:
                print(f"! Stripe 顧客削除失敗: {e}")
    except Exception as e:
        print(f"! Stripe操作エラー: {e}")


def reset_user(db, email: str, purge_meetings: bool) -> None:
    user = find_user_by_email(db, email)
    if not user:
        print(f"✗ ユーザーが見つかりません: {email}")
        return

    print(f"対象ユーザー: id={user.id}, email={user.email}, is_premium={user.is_premium}")
    init_stripe()
    cancel_stripe_resources(user)

    # DBの状態を初期化
    user.is_premium = "false"
    user.stripe_subscription_id = None
    user.stripe_customer_id = None
    try:
        # これらのフィールドが存在しない場合もあるためbest-effortで
        if hasattr(user, 'usage_count'):
            setattr(user, 'usage_count', 0)
        if hasattr(user, 'trial_start_date'):
            setattr(user, 'trial_start_date', None)
    except Exception:
        pass

    if purge_meetings:
        meetings = db.query(Meeting).filter(Meeting.user_id == user.id).all()
        for m in meetings:
            db.delete(m)
        print(f"✓ 議事録削除: {len(meetings)} 件")

    db.commit()
    print("✓ ユーザー状態を無料にリセットしました")


def delete_user(db, email: str, purge_meetings: bool) -> None:
    user = find_user_by_email(db, email)
    if not user:
        print(f"✗ ユーザーが見つかりません: {email}")
        return

    print(f"削除対象: id={user.id}, email={user.email}")
    init_stripe()
    cancel_stripe_resources(user)

    if purge_meetings:
        meetings = db.query(Meeting).filter(Meeting.user_id == user.id).all()
        for m in meetings:
            db.delete(m)
        print(f"✓ 議事録削除: {len(meetings)} 件")

    db.delete(user)
    db.commit()
    print("✓ ユーザーを削除しました")


def main():
    parser = argparse.ArgumentParser(description='テスト向けユーザー状態のリセット/削除')
    parser.add_argument('--email', required=True, help='対象ユーザーのメールアドレス')
    parser.add_argument('--action', choices=['reset', 'delete'], default='reset', help='実行モード')
    parser.add_argument('--purge-meetings', action='store_true', help='議事録も削除する')
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.action == 'reset':
            reset_user(db, args.email, args.purge_meetings)
        else:
            delete_user(db, args.email, args.purge_meetings)
    finally:
        db.close()


if __name__ == '__main__':
    main()


