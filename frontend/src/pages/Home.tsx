import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { authService } from '../services/authService'
import './Home.css'

const Home: React.FC = () => {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const [isProcessing, setIsProcessing] = useState(false)

  useEffect(() => {
    // Google認証のコールバック処理
    const handleGoogleAuth = async () => {
      try {
        const hash = window.location.hash
        if (hash && hash.includes('id_token')) {
          console.log('DEBUG: Google認証トークンを検出')
          const idToken = hash.split('id_token=')[1].split('&')[0]
          
          const response = await authService.googleAuth(idToken)
          
          if (response.success && response.data) {
            await login(response.data.access_token, response.data.user)
            window.history.replaceState({}, document.title, window.location.pathname)
            navigate('/')
          }
        }
      } catch (error) {
        console.error('Google認証エラー:', error)
      }
    }

    // LINE認証のコールバック処理
    const handleLineAuth = async () => {
      if (isProcessing) return // 処理中の場合は何もしない
      
      try {
        const urlParams = new URLSearchParams(window.location.search)
        const code = urlParams.get('code')
        const state = urlParams.get('state')
        
        if (code && state === 'line') {
          console.log('DEBUG: LINE認証コードを検出')
          setIsProcessing(true)
          
          const response = await authService.lineAuth(code)
          
          if (response.success && response.data) {
            await login(response.data.access_token, response.data.user)
            window.history.replaceState({}, document.title, window.location.pathname)
            navigate('/')
          }
        }
      } catch (error) {
        console.error('LINE認証エラー:', error)
      } finally {
        setIsProcessing(false)
      }
    }

    handleGoogleAuth()
    handleLineAuth()
  }, [login, navigate, isProcessing])

  if (!user) {
    return (
      <div className="home-container">
        <div className="welcome-section">
          <h1>🎤 議事録要約Webアプリ</h1>
          <p className="subtitle">会議音声を自動で文字起こし・要約</p>
          <p className="description">
            簡単な操作で会議の録音から要約まで自動化。<br />
            誰でも簡単に使える議事録作成ツールです。
          </p>
          <Link to="/login" className="cta-button">
            🚀 ログインして開始
          </Link>
        </div>
        
        <div className="features-section">
          <h2>✨ 主な機能</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🎤</div>
              <h3>簡単録音</h3>
              <p>ワンクリック録音開始。安定した処理</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🤖</div>
              <h3>AI文字起こし</h3>
              <p>AI活用で高精度な日本語文字起こし</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📝</div>
              <h3>自動要約</h3>
              <p>AIで議事録を自動要約。アクションアイテムも抽出</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📁</div>
              <h3>履歴管理</h3>
              <p>過去の議事録を簡単に確認・ダウンロード</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="home-container">
      <div className="user-welcome">
        <h1>👋 ようこそ、{user.name || user.email}さん</h1>
        <div className="user-stats">
          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <h3>利用回数</h3>
            <p className="stat-value">{user.usage_count || 0}回</p>
          </div>
          <div className="stat-card">
            <div className="stat-icon">{user.is_premium === 'true' ? '⭐' : '📋'}</div>
            <h3>プラン</h3>
            <p className="stat-value">{user.is_premium === 'true' ? 'プレミアム' : '無料プラン'}</p>
          </div>
        </div>
      </div>
      
      <div className="main-actions">
        <h2>🎯 今すぐ始める</h2>
        <div className="action-grid">
          <Link to="/recording" className="main-action-button recording">
            <div className="action-icon">🎤</div>
            <div className="action-content">
              <h3>録音開始</h3>
              <p>新しい会議の録音を開始します</p>
            </div>
            <div className="action-arrow">→</div>
          </Link>
          
          <Link to="/history" className="main-action-button history">
            <div className="action-icon">📋</div>
            <div className="action-content">
              <h3>履歴確認</h3>
              <p>過去の議事録を確認・ダウンロード</p>
            </div>
            <div className="action-arrow">→</div>
          </Link>
          
          <Link to="/settings" className="main-action-button settings">
            <div className="action-icon">⚙️</div>
            <div className="action-content">
              <h3>設定・管理</h3>
              <p>アカウント設定とプレミアム機能</p>
            </div>
            <div className="action-arrow">→</div>
          </Link>
        </div>
      </div>
      
      {user.is_premium !== 'true' && (
        <div className="upgrade-section">
          <div className="upgrade-content">
            <h2>⭐ プレミアムプランにアップグレード</h2>
            <p>無制限の利用と追加機能を利用できます</p>
            <ul className="upgrade-features">
              <li>✅ 2時間までの録音（無料は30分）</li>
              <li>✅ PDF/Word形式でエクスポート</li>
              <li>✅ 無制限の使用回数</li>
              <li>✅ 優先サポート</li>
            </ul>
            <Link to="/settings" className="upgrade-button">
              💎 プレミアムにアップグレード
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}

export default Home 