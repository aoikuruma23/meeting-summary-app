import stripe
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.config import settings
from typing import Optional
from datetime import datetime
import hashlib

# Stripeの初期化
stripe.api_key = settings.STRIPE_SECRET_KEY
# APIバージョンを明示（SDK/バックエンド互換の安定版）
try:
    # 明示固定で apps/objects 解決の不整合を回避
    stripe.api_version = "2024-06-20"
except Exception:
    pass
# 一時ワークアラウンド: 古いSDKで stripe.apps が None の場合に Secret 参照で落ちるのを回避
try:
    if getattr(stripe, 'apps', None) is None:
        class _DummySecret:
            OBJECT_NAME = 'apps.secret'
        class _DummyApps:
            pass
        stripe.apps = _DummyApps()
        setattr(stripe.apps, 'Secret', _DummySecret)
        print("DEBUG: Applied dummy stripe.apps.Secret workaround")
except Exception as e:
    print(f"DEBUG: stripe.apps workaround error: {e}")
try:
    # 事前に _object_classes を読み込んでマッピングを確定させる
    import stripe._object_classes  # type: ignore
    print("DEBUG: stripe._object_classes imported successfully")
except Exception as e:
    print(f"DEBUG: stripe._object_classes import error: {e}")
print(f"DEBUG: Stripe SDK version: {getattr(stripe, '__version__', 'unknown')}, api_version: {getattr(stripe, 'api_version', 'unset')}, apps_is_none: {getattr(stripe, 'apps', None) is None}")

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
                
                # unit_amount は最小通貨単位の整数（JPY は円単位）。環境値は文字列のため int へ変換
                try:
                    unit_amount = int(settings.MONTHLY_PRICE)
                except Exception:
                    unit_amount = 999

                # Idempotency-Key は一旦未使用（ライブラリ互換性の切り分けのため）

                # 可能ならStripeのPrice IDを利用（推奨）
                if settings.STRIPE_PRICE_ID:
                    price_id = settings.STRIPE_PRICE_ID.strip()
                    print(f"DEBUG: Using STRIPE_PRICE_ID: {price_id}")
                    # 1st try: line_items（一般的）
                    try:
                        session = stripe.checkout.Session.create(
                            customer=customer_id,
                            line_items=[{'price': price_id, 'quantity': 1}],
                            mode='subscription',
                            success_url='https://meeting-summary-app.jibunkaikaku-lab.com/billing?success=true',
                            cancel_url='https://meeting-summary-app.jibunkaikaku-lab.com/billing?canceled=true',
                            metadata={'user_id': str(user.id), 'plan_id': plan_id}
                        )
                    except stripe.error.StripeError as se:
                        # 2nd try: subscription_data.items（APIバージョン差異の回避）
                        print(f"WARN: line_items failed: {getattr(se, 'user_message', None) or str(se)}; retry with subscription_data.items")
                        session = stripe.checkout.Session.create(
                            customer=customer_id,
                            subscription_data={'items': [{'price': price_id, 'quantity': 1}]},
                            mode='subscription',
                            success_url='https://meeting-summary-app.jibunkaikaku-lab.com/billing?success=true',
                            cancel_url='https://meeting-summary-app.jibunkaikaku-lab.com/billing?canceled=true',
                            metadata={'user_id': str(user.id), 'plan_id': plan_id}
                        )
                else:
                    print(f"DEBUG: Using price_data unit_amount={unit_amount}")
                    session = stripe.checkout.Session.create(
                        customer=customer_id,
                        line_items=[{
                            'price_data': {
                                'currency': 'jpy',
                                'product_data': {
                                    'name': 'プレミアムプラン',
                                    'description': '無制限録音、PDF/Word出力、高度な要約機能',
                                },
                                'unit_amount': unit_amount,
                                'recurring': { 'interval': 'month' },
                            },
                            'quantity': 1,
                        }],
                        mode='subscription',
                        success_url='https://meeting-summary-app.jibunkaikaku-lab.com/billing?success=true',
                        cancel_url='https://meeting-summary-app.jibunkaikaku-lab.com/billing?canceled=true',
                        metadata={'user_id': str(user.id), 'plan_id': plan_id}
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
                        "url": "https://meeting-summary-app.jibunkaikaku-lab.com/"
                    }
                }
                
        except stripe.error.StripeError as se:
            # Stripeの詳細エラーを返す
            message = getattr(se, 'user_message', None) or str(se)
            print(f"ERROR: StripeError in checkout.create: {message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripeエラー: {message}"
            )
        except Exception as e:
            import traceback
            print(f"ERROR: checkout.create unexpected error: {e}\n{traceback.format_exc()}")
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
            
            print(f"DEBUG: Create portal for customer: {user.stripe_customer_id}")
            # idempotency_key は相性問題を避けるため一旦外す
            try:
                create_kwargs = {
                    'customer': user.stripe_customer_id,
                    'return_url': 'https://meeting-summary-app.jibunkaikaku-lab.com/billing',
                }
                # ライブモードでデフォルト設定が未保存な場合は、明示的に configuration を指定
                config_id = self._get_or_create_portal_configuration_id()
                if config_id:
                    create_kwargs['configuration'] = config_id
                session = stripe.billing_portal.Session.create(**create_kwargs)
            except stripe.error.StripeError as se:
                message = getattr(se, 'user_message', None) or str(se)
                print(f"ERROR: StripeError in portal.create: {message}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stripeエラー: {message}"
                )
            
            return {
                "success": True,
                "message": "ポータルセッションを作成しました",
                "data": {
                    "url": session.url
                }
            }
            
        except Exception as e:
            print(f"ERROR: portal.create unexpected error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"ポータルセッションの作成に失敗しました: {str(e)}"
            )

    def _get_or_create_portal_configuration_id(self) -> Optional[str]:
        """ポータル設定IDを取得。なければ1件作成してIDを返す（失敗時はNone）。"""
        try:
            # 環境変数の優先
            if settings.STRIPE_PORTAL_CONFIGURATION_ID:
                return settings.STRIPE_PORTAL_CONFIGURATION_ID.strip()

            # 既存設定を検索（最新1件）
            conf_list = stripe.billing_portal.Configuration.list(limit=1)
            data = getattr(conf_list, 'data', []) or []
            if len(data) > 0 and data[0].get('id'):
                return data[0]['id']

            # なければ最小構成で作成
            # NOTE: subscription_update を有効にする場合は products の指定が必須（Stripe要件）
            #       products には「プランの product ID」を指定する必要がある
            product_id: Optional[str] = None
            try:
                if settings.STRIPE_PRICE_ID:
                    price_obj = stripe.Price.retrieve(settings.STRIPE_PRICE_ID.strip())
                    product_id = price_obj.get('product') if isinstance(price_obj, dict) else getattr(price_obj, 'product', None)
                    print(f"DEBUG: Resolved product_id from price: {product_id}")
            except Exception as e:
                print(f"DEBUG: Failed to resolve product from price: {e}")

            products_param = []
            if product_id:
                products_param = [{ 'product': product_id }]
            else:
                # 価格IDが未設定の場合は、最新の有効な価格から製品を推定
                try:
                    price_list = stripe.Price.list(active=True, limit=1)
                    price_data = (getattr(price_list, 'data', []) or [])
                    if len(price_data) > 0:
                        pid = price_data[0].get('product')
                        if pid:
                            products_param = [{ 'product': pid }]
                            print(f"DEBUG: Resolved product_id from price list: {pid}")
                except Exception as e:
                    print(f"DEBUG: Failed to resolve product from price list: {e}")

            created = stripe.billing_portal.Configuration.create(
                business_profile={
                    'privacy_policy_url': 'https://meeting-summary-app.jibunkaikaku-lab.com/privacy',
                    'terms_of_service_url': 'https://meeting-summary-app.jibunkaikaku-lab.com/terms',
                },
                features={
                    'invoice_history': {'enabled': True},
                    'payment_method_update': {'enabled': True},
                    'subscription_cancel': {'enabled': True},
                    'subscription_update': {
                        'enabled': True,
                        # 必須: 更新対象にできる製品を指定
                        'products': products_param if products_param else [],
                    },
                    'customer_update': {
                        'allowed_updates': ['address', 'email', 'name', 'phone'],
                        'enabled': True,
                    },
                },
            )
            return getattr(created, 'id', None)
        except Exception as e:
            print(f"DEBUG: portal configuration resolve/create failed: {e}")
        return None
    
    def get_subscription_status(self, user: User, db: Session) -> dict:
        """サブスクリプション状態を取得"""
        try:
            print(f"DEBUG: get_subscription_status - user_id: {user.id}, is_premium: {user.is_premium}, type: {type(user.is_premium)}")
            # データベースの実際の値を確認
            db_user = db.query(User).filter(User.id == user.id).first()
            if db_user and db_user.is_premium != user.is_premium:
                print(f"WARNING: データベースのis_premium ({db_user.is_premium}) とユーザーオブジェクトのis_premium ({user.is_premium}) が一致しません")
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
    
    def check_access(self, user: User, db: Session) -> dict:
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