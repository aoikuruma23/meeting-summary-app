import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { billingService } from '../services/billingService';
import './Billing.css';

interface PricingPlan {
  id: string;
  name: string;
  price: number;
  features: string[];
  popular?: boolean;
}

interface SubscriptionStatus {
  isActive: boolean;
  plan: string;
  currentPeriodEnd: string;
  cancelAtPeriodEnd: boolean;
}

const Billing: React.FC = () => {
  const { user } = useAuth();
  const [subscription, setSubscription] = useState<SubscriptionStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [portalLoading, setPortalLoading] = useState(false);

  const pricingPlans: PricingPlan[] = [
    {
      id: 'free',
      name: '無料プラン',
      price: 0,
      features: [
        '最大30分の録音',
        '10回まで利用可能',
        '基本的な要約機能',
        '31日間 + 翌月1日まで'
      ]
    },
    {
      id: 'premium',
      name: 'プレミアムプラン',
      price: 980,
      features: [
        '最大2時間の録音',
        '無制限利用',
        'PDF/Word形式でエクスポート',
        '高度な要約機能',
        '優先サポート'
      ],
      popular: true
    }
  ];

  useEffect(() => {
    fetchSubscriptionStatus();
  }, []);

  const fetchSubscriptionStatus = async () => {
    try {
      const response = await billingService.getSubscriptionStatus();
      setSubscription(response.data);
    } catch (error) {
      console.error('サブスクリプション状態の取得に失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckout = async (planId: string) => {
    if (planId === 'free') return;
    
    setCheckoutLoading(true);
    try {
      const response = await billingService.createCheckoutSession(planId);
      if (response.data.url) {
        window.location.href = response.data.url;
      }
    } catch (error) {
      console.error('チェックアウトセッションの作成に失敗:', error);
      alert('決済の開始に失敗しました。もう一度お試しください。');
    } finally {
      setCheckoutLoading(false);
    }
  };

  const handleManageSubscription = async () => {
    setPortalLoading(true);
    try {
      const response = await billingService.createPortalSession();
      if (response.data.url) {
        window.location.href = response.data.url;
      }
    } catch (error) {
      console.error('ポータルセッションの作成に失敗:', error);
      alert('サブスクリプション管理ページの表示に失敗しました。');
    } finally {
      setPortalLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="billing-container">
        <div className="loading-spinner">読み込み中...</div>
      </div>
    );
  }

  return (
    <div className="billing-container">
      <div className="billing-header">
        <h1>プランと課金</h1>
        <p>あなたに最適なプランを選択してください</p>
      </div>

      {subscription && (
        <div className="current-subscription">
          <h2>現在のサブスクリプション</h2>
          <div className="subscription-card">
            <div className="subscription-info">
              <h3>{subscription.plan === 'premium' ? 'プレミアムプラン' : '無料プラン'}</h3>
              <p>ステータス: {subscription.isActive ? 'アクティブ' : '非アクティブ'}</p>
              {subscription.currentPeriodEnd && (
                <p>次回更新: {new Date(subscription.currentPeriodEnd).toLocaleDateString('ja-JP')}</p>
              )}
              {subscription.cancelAtPeriodEnd && (
                <p className="cancel-notice">期間終了時にキャンセル予定</p>
              )}
            </div>
            {subscription.isActive && subscription.plan === 'premium' && (
              <button 
                onClick={handleManageSubscription}
                disabled={portalLoading}
                className="manage-button"
              >
                {portalLoading ? '読み込み中...' : 'サブスクリプション管理'}
              </button>
            )}
          </div>
        </div>
      )}

      <div className="pricing-section">
        <h2>利用可能なプラン</h2>
        <div className="pricing-grid">
          {pricingPlans.map((plan) => (
            <div 
              key={plan.id} 
              className={`pricing-card ${plan.popular ? 'popular' : ''}`}
            >
              {plan.popular && <div className="popular-badge">人気</div>}
              <div className="plan-header">
                <h3>{plan.name}</h3>
                <div className="price">
                  <span className="amount">¥{plan.price.toLocaleString()}</span>
                  {plan.price > 0 && <span className="period">/月</span>}
                </div>
              </div>
              <ul className="features">
                {plan.features.map((feature, index) => (
                  <li key={index}>{feature}</li>
                ))}
              </ul>
              <button
                onClick={() => handleCheckout(plan.id)}
                disabled={checkoutLoading || (subscription?.isActive && subscription?.plan === plan.id)}
                className={`plan-button ${plan.popular ? 'primary' : 'secondary'}`}
              >
                {checkoutLoading ? '処理中...' : 
                  subscription?.isActive && subscription?.plan === plan.id ? '現在のプラン' :
                  plan.price === 0 ? '無料で開始' : 'プレミアムにアップグレード'
                }
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="billing-info">
        <h3>お支払いについて</h3>
        <ul>
          <li>プレミアムプランは月額980円（税込）です</li>
          <li>いつでもキャンセル可能です</li>
          <li>無料期間中は課金されません</li>
          <li>お支払い情報はStripeで安全に管理されます</li>
        </ul>
      </div>
    </div>
  );
};

export default Billing; 