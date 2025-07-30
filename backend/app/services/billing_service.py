import stripe
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.config import settings
from typing import Optional

# Stripeの初期化
stripe.api_key = settings.STRIPE_SECRET_KEY

class BillingService:
    def __init__(self):
        self.stripe = stripe
    
    def create_checkout_session(self, user: User, plan_id: str, db: Session) -> dict:
        """チェックアウトセッションを作成"""
        try:
            # プレミアムプランの場合のみStripeセッションを作成
            if plan_id == 'premium':
                # 顧客IDを取得または作成
                customer_id = self._get_or_create_customer(user, db)
                
                # チェックアウトセッションを作成
                session = stripe.checkout.Session.create(
                    customer=customer_id,
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'jpy',
                            'product_data': {
                                'name': 'プレミアムプラン',
                                'description': '無制限録音、PDF/Word出力、高度な要約機能',
                            },
                            'unit_amount': settings.MONTHLY_PRICE,
                            'recurring': {
                                'interval': 'month',
                            },
                        },
                        'quantity': 1,
                    }],
                    mode='subscription',
                    success_url='http://localhost:3000/billing?success=true',
                    cancel_url='http://localhost:3000/billing?canceled=true',
                    metadata={
                        'user_id': str(user.id),
                        'plan_id': plan_id
                    }
                )
                
                return {
                    "success": True,
                    "message": "チェックアウトセッションを作成しました",
                    "data": {
                        "url": session.url
                    }
                }
            else:
                # 無料プランの場合は直接アクセス権限を付与
                return {
                    "success": True,
                    "message": "無料プランにアクセスしました",
                    "data": {
                        "url": "http://localhost:3000/"
                    }
                }
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"チェックアウトセッションの作成に失敗しました: {str(e)}"
            )
    
    def create_portal_session(self, user: User) -> dict:
        """ポータルセッションを作成（サブスクリプション管理）"""
        try:
            if not user.stripe_customer_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="サブスクリプションが見つかりません"
                )
            
            session = stripe.billing_portal.Session.create(
                customer=user.stripe_customer_id,
                return_url='http://localhost:3000/billing',
            )
            
            return {
                "success": True,
                "message": "ポータルセッションを作成しました",
                "data": {
                    "url": session.url
                }
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"ポータルセッションの作成に失敗しました: {str(e)}"
            )
    
    def get_subscription_status(self, user: User) -> dict:
        """サブスクリプション状態を取得"""
        try:
            print(f"DEBUG: get_subscription_status - user_id: {user.id}, is_premium: {user.is_premium}, type: {type(user.is_premium)}")
            print(f"ERROR: データベースのis_premiumがfalseになっています！Webhookが正しく処理されていない可能性があります。")
            # プレミアムユーザーの場合
            if user.is_premium == "true":
                if user.stripe_subscription_id:
                    try:
                        subscription = stripe.Subscription.retrieve(user.stripe_subscription_id)
                        return {
                            "success": True,
                            "message": "サブスクリプション状態を取得しました",
                            "data": {
                                "isActive": subscription.status == 'active',
                                "plan": "premium",
                                "currentPeriodEnd": subscription.current_period_end,
                                "cancelAtPeriodEnd": subscription.cancel_at_period_end
                            }
                        }
                    except Exception as e:
                        print(f"DEBUG: Stripe subscription retrieval error: {str(e)}")
                        # Stripeエラーの場合でもプレミアム状態を返す
                        return {
                            "success": True,
                            "message": "サブスクリプション状態を取得しました",
                            "data": {
                                "isActive": True,
                                "plan": "premium",
                                "currentPeriodEnd": None,
                                "cancelAtPeriodEnd": False
                            }
                        }
                else:
                    # プレミアムユーザーだがStripeサブスクリプションIDがない場合
                    return {
                        "success": True,
                        "message": "サブスクリプション状態を取得しました",
                        "data": {
                            "isActive": True,
                            "plan": "premium",
                            "currentPeriodEnd": None,
                            "cancelAtPeriodEnd": False
                        }
                    }
            
            # 無料ユーザーの場合
            return {
                "success": True,
                "message": "サブスクリプション状態を取得しました",
                "data": {
                    "isActive": False,
                    "plan": "free",
                    "currentPeriodEnd": None,
                    "cancelAtPeriodEnd": False
                }
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"サブスクリプション状態の取得に失敗しました: {str(e)}"
            )
    
    def get_pricing_info(self) -> dict:
        """価格情報を取得"""
        try:
            return {
                "success": True,
                "message": "価格情報を取得しました",
                "data": {
                    "monthlyPrice": settings.MONTHLY_PRICE,
                    "freeTrialDays": settings.FREE_TRIAL_DAYS,
                    "freeUsageLimit": settings.FREE_USAGE_LIMIT
                }
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"価格情報の取得に失敗しました: {str(e)}"
            )
    
    def check_access(self, user: User) -> dict:
        """アクセス権限をチェック"""
        try:
            # プレミアムユーザーの場合
            if user.is_premium == "true":
                return {
                    "success": True,
                    "message": "アクセス権限を確認しました",
                    "data": {
                        "hasAccess": True
                    }
                }
            
            # 無料ユーザーの場合、利用制限をチェック
            from app.services.auth_service import AuthService
            auth_service = AuthService()
            
            if auth_service.is_trial_valid(user):
                return {
                    "success": True,
                    "message": "アクセス権限を確認しました",
                    "data": {
                        "hasAccess": True
                    }
                }
            else:
                return {
                    "success": True,
                    "message": "アクセス権限を確認しました",
                    "data": {
                        "hasAccess": False
                    }
                }
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"アクセス権限の確認に失敗しました: {str(e)}"
            )
    
    def _get_or_create_customer(self, user: User, db: Session) -> str:
        """Stripe顧客IDを取得または作成"""
        if user.stripe_customer_id:
            return user.stripe_customer_id
        
        # 新しい顧客を作成
        customer = stripe.Customer.create(
            email=user.email,
            name=user.name,
            metadata={
                'user_id': str(user.id)
            }
        )
        
        # データベースに顧客IDを保存
        user.stripe_customer_id = customer.id
        db.commit()
        
        return customer.id
    
    def handle_webhook(self, payload: bytes, sig_header: str) -> dict:
        """Stripe webhookを処理"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            
            # データベースセッションを取得
            from app.core.database import get_db
            db = next(get_db())
            
            try:
                if event['type'] == 'checkout.session.completed':
                    session = event['data']['object']
                    self._handle_checkout_completed(session, db)
                elif event['type'] == 'customer.subscription.updated':
                    subscription = event['data']['object']
                    self._handle_subscription_updated(subscription, db)
                elif event['type'] == 'customer.subscription.deleted':
                    subscription = event['data']['object']
                    self._handle_subscription_deleted(subscription, db)
                
                db.commit()
                return {"success": True, "message": "Webhookを処理しました"}
                
            except Exception as e:
                db.rollback()
                raise e
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Webhookの処理に失敗しました: {str(e)}"
            )
    
    def _handle_checkout_completed(self, session: dict, db: Session):
        """チェックアウト完了時の処理"""
        try:
            # ユーザーIDを取得
            user_id = session.metadata.get('user_id')
            print(f"ERROR: Webhook処理開始 - user_id: {user_id}")
            if not user_id:
                print(f"ERROR: user_idが見つかりません")
                return
            
            # ユーザーを取得
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                print(f"ERROR: ユーザーが見つかりません - user_id: {user_id}")
                return
            
            print(f"ERROR: ユーザー発見 - id: {user.id}, email: {user.email}, is_premium: {user.is_premium}")
            
            # サブスクリプションIDを保存
            subscription_id = session.subscription
            if subscription_id:
                user.stripe_subscription_id = subscription_id
                user.is_premium = "true"
                db.commit()
                print(f"ERROR: サブスクリプション完了 - user_id: {user_id}, subscription_id: {subscription_id}")
                print(f"ERROR: is_premiumをtrueに更新しました")
            else:
                print(f"ERROR: subscription_idが見つかりません")
                
        except Exception as e:
            print(f"ERROR: チェックアウト完了処理エラー - {str(e)}")
            raise e
        
    def _handle_subscription_updated(self, subscription: dict, db: Session):
        """サブスクリプション更新時の処理"""
        try:
            # サブスクリプションIDでユーザーを検索
            user = db.query(User).filter(User.stripe_subscription_id == subscription.id).first()
            if not user:
                return
            
            # サブスクリプション状態を更新
            if subscription.status == 'active':
                user.is_premium = "true"
            elif subscription.status in ['canceled', 'unpaid']:
                user.is_premium = "false"
            
            db.commit()
            print(f"DEBUG: サブスクリプション更新 - user_id: {user.id}, status: {subscription.status}")
            
        except Exception as e:
            print(f"DEBUG: サブスクリプション更新処理エラー - {str(e)}")
            raise e
        
    def _handle_subscription_deleted(self, subscription: dict, db: Session):
        """サブスクリプション削除時の処理"""
        try:
            # サブスクリプションIDでユーザーを検索
            user = db.query(User).filter(User.stripe_subscription_id == subscription.id).first()
            if not user:
                return
            
            # ユーザーを無料プランに戻す
            user.is_premium = "false"
            user.stripe_subscription_id = None
            db.commit()
            print(f"DEBUG: サブスクリプション削除 - user_id: {user.id}")
            
        except Exception as e:
            print(f"DEBUG: サブスクリプション削除処理エラー - {str(e)}")
            raise e 