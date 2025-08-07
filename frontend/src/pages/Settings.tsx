import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import './Settings.css'

const Settings: React.FC = () => {
  const { user } = useAuth()
  // 無料期間の残り日数を計算する関数
  const calculateTrialDaysRemaining = (trialStartDate: string | undefined) => {
    if (!trialStartDate || user?.is_premium === 'true') {
      return 0
    }
    
    const trialStart = new Date(trialStartDate)
    const trialEnd = new Date(trialStart.getTime() + (31 * 24 * 60 * 60 * 1000)) // 31日後
    const now = new Date()
    const remaining = Math.ceil((trialEnd.getTime() - now.getTime()) / (24 * 60 * 60 * 1000))
    
    return Math.max(0, remaining)
  }

  const [subscriptionStatus, _setSubscriptionStatus] = useState({
    is_premium: user?.is_premium === 'true',
    trial_days_remaining: calculateTrialDaysRemaining(user?.trial_start_date),
    usage_count: user?.usage_count || 0,
    free_usage_limit: 10
  })

  useEffect(() => {
    // ユーザーの状態を更新
    _setSubscriptionStatus(prev => ({
      ...prev,
      is_premium: user?.is_premium === 'true',
      usage_count: user?.usage_count || 0,
      trial_days_remaining: calculateTrialDaysRemaining(user?.trial_start_date)
    }))
  }, [user?.is_premium, user?.usage_count, user?.trial_start_date])

  const handleUpgrade = async () => {
    try {
      // プランページにリダイレクト
      window.location.href = '/billing'
    } catch (error) {
      console.error('アップグレードエラー:', error)
    }
  }

  return (
    <div className="settings-container">
      <h1>設定</h1>
      
      <div className="settings-section">
        <h2>アカウント情報</h2>
        <div className="account-info">
          <p><strong>名前:</strong> {user?.name}</p>
          <p><strong>メール:</strong> {user?.email}</p>
          <p><strong>プラン:</strong> {user?.is_premium === 'true' ? 'プレミアム' : '無料プラン'}</p>
        </div>
      </div>
      
      <div className="settings-section">
        <h2>利用状況</h2>
        <div className="usage-info">
          <p>利用回数: {subscriptionStatus.usage_count} / {subscriptionStatus.free_usage_limit}</p>
          {!subscriptionStatus.is_premium && (
            <p>無料期間残り: {subscriptionStatus.trial_days_remaining}日</p>
          )}
        </div>
      </div>
      
      {!subscriptionStatus.is_premium && (
        <div className="settings-section">
          <h2>プレミアムプラン</h2>
          <div className="premium-info">
            <h3>月額980円</h3>
            <ul>
              <li>無制限の録音・要約</li>
              <li>優先サポート</li>
              <li>追加機能（予定）</li>
            </ul>
            <button onClick={handleUpgrade} className="upgrade-button">
              プレミアムにアップグレード
            </button>
          </div>
        </div>
      )}
      
      <div className="settings-section">
        <h2>アプリ情報</h2>
        <div className="app-info">
          <p>バージョン: 1.0.0</p>
          <p>議事録要約Webアプリ</p>
        </div>
      </div>
    </div>
  )
}

export default Settings 