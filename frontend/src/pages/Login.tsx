import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
// import { authService } from '../services/authService'
import './Login.css'

const Login: React.FC = () => {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)

  const handleGoogleLogin = async () => {
    setLoading(true)
    try {
      // Google OAuthの実装（簡略化）
      alert('Googleログイン機能は準備中です')
    } catch (error) {
      console.error('Googleログインエラー:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLineLogin = async () => {
    setLoading(true)
    try {
      // LINE OAuthの実装（簡略化）
      alert('LINEログイン機能は準備中です')
    } catch (error) {
      console.error('LINEログインエラー:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDummyLogin = async () => {
    setLoading(true)
    try {
      // ダミーログインAPIを呼び出し
      const apiUrl = import.meta.env.VITE_API_URL || 'https://meeting-summary-app-backend.onrender.com'
      const response = await fetch(`${apiUrl}/api/auth/dummy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      if (!response.ok) {
        throw new Error('ダミーログインに失敗しました')
      }
      
      const data = await response.json()
      if (data.success && data.data) {
        const token = data.data.access_token
        await login(token)
        // ログイン成功後、ホーム画面に遷移
        navigate('/')
      } else {
        throw new Error(data.message || 'ダミーログインに失敗しました')
      }
    } catch (error) {
      console.error('ダミーログインエラー:', error)
      const errorMessage = error instanceof Error ? error.message : 'ダミーログインに失敗しました'
      alert('ダミーログインに失敗しました: ' + errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>🎤 ログイン</h1>
        <p>議事録要約Webアプリにログインしてください</p>
        
        <div className="login-buttons">
          <button 
            onClick={handleDummyLogin}
            disabled={loading}
            className="login-button dummy"
          >
            <span className="icon">🧪</span>
            ダミーログイン（テスト用）
          </button>
          
          <button 
            onClick={handleGoogleLogin}
            disabled={loading}
            className="login-button google"
          >
            <span className="icon">🔍</span>
            Googleでログイン（準備中）
          </button>
          
          <button 
            onClick={handleLineLogin}
            disabled={loading}
            className="login-button line"
          >
            <span className="icon">💬</span>
            LINEでログイン（準備中）
          </button>
        </div>
        
        {loading && (
          <div className="loading">
            <div className="loading-spinner"></div>
            ログイン中...
          </div>
        )}
        
        <div className="login-info">
          <p>初回ログインでアカウントが作成されます</p>
          <div className="free-trial-info">
            <h3>📅 無料期間について</h3>
            <ul>
              <li>✅ 31日間 + 翌月1日まで</li>
              <li>✅ または10回利用まで</li>
              <li>✅ どちらか早い方で終了</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login 