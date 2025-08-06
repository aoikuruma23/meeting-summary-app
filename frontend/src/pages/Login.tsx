import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { authService } from '../services/authService'
import './Login.css'

const Login: React.FC = () => {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [isRegister, setIsRegister] = useState(false)
  
  // メール・パスワード用の状態
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [showPassword, setShowPassword] = useState(false)

  const handleGoogleLogin = async () => {
    console.log('DEBUG: Googleログインボタンがクリックされました')
    setIsLoading(true)
    setError('')

    try {
      const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
      console.log('DEBUG: GOOGLE_CLIENT_ID:', googleClientId)
      
      if (!googleClientId) {
        console.log('DEBUG: GOOGLE_CLIENT_IDが設定されていません')
        setError('Googleログインは現在準備中です。ダミーログインをご利用ください。')
        setIsLoading(false)
        return
      }

      const redirectUri = window.location.origin
      const googleAuthUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${googleClientId}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=id_token&scope=openid%20email%20profile&nonce=${Date.now()}`
      console.log('DEBUG: Google認証URL:', googleAuthUrl)
      window.location.href = googleAuthUrl
    } catch (err) {
      console.error('DEBUG: Googleログインエラー:', err)
      setError('Googleログインに失敗しました')
      setIsLoading(false)
    }
  }

  const handleLineLogin = async () => {
    console.log('DEBUG: LINEログインボタンがクリックされました')
    setIsLoading(true)
    setError('')

    try {
      const lineChannelId = import.meta.env.VITE_LINE_CHANNEL_ID
      console.log('DEBUG: LINE_CHANNEL_ID:', lineChannelId)
      
      if (!lineChannelId) {
        console.log('DEBUG: LINE_CHANNEL_IDが設定されていません')
        setError('LINEログインは現在準備中です。ダミーログインをご利用ください。')
        setIsLoading(false)
        return
      }

      const lineAuthUrl = `https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id=${lineChannelId}&redirect_uri=${encodeURIComponent(window.location.origin)}&state=line&scope=profile%20openid%20email`
      console.log('DEBUG: LINE認証URL:', lineAuthUrl)
      window.location.href = lineAuthUrl
    } catch (err) {
      console.error('DEBUG: LINEログインエラー:', err)
      setError('LINEログインに失敗しました')
      setIsLoading(false)
    }
  }

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      if (isRegister) {
        // 登録
        const response = await authService.emailRegister({
          email,
          password,
          name
        })
        
        if (response.success && response.data) {
          await login(response.data.access_token, response.data.user)
          navigate('/')
        }
      } else {
        // ログイン
        const response = await authService.emailLogin({
          email,
          password
        })
        
        if (response.success && response.data) {
          await login(response.data.access_token, response.data.user)
          navigate('/')
        }
      }
    } catch (err: any) {
      console.error('メール認証エラー:', err)
      setError(err.message || '認証に失敗しました')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDummyLogin = async () => {
    setIsLoading(true)
    setError('')

    try {
      // ダミーユーザーでログイン
      const dummyUser = {
        id: 1,
        email: 'dummy@example.com',
        name: 'テストユーザー',
        is_premium: 'true'
      }
      
      const dummyToken = 'dummy_token_' + Date.now()
      
      await login(dummyToken, dummyUser)
      navigate('/')
    } catch (err) {
      console.error('ダミーログインエラー:', err)
      setError('ダミーログインに失敗しました')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>{isRegister ? 'アカウント登録' : 'ログイン'}</h1>
        
        {error && <div className="error-message">{error}</div>}
        
        {/* メール・パスワードフォーム */}
        <form onSubmit={handleEmailSubmit} className="email-form">
          {isRegister && (
            <div className="form-group">
              <label htmlFor="name">お名前</label>
              <input
                type="text"
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                placeholder="お名前を入力"
              />
            </div>
          )}
          
          <div className="form-group">
            <label htmlFor="email">メールアドレス</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="メールアドレスを入力"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">パスワード</label>
            <div className="password-input-container">
              <input
                type={showPassword ? "text" : "password"}
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="パスワードを入力"
                minLength={6}
              />
              <button
                type="button"
                className="password-toggle-btn"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? "🙈" : "👁️"}
              </button>
            </div>
          </div>
          
          <button 
            type="submit" 
            className="btn btn-primary email-submit"
            disabled={isLoading}
          >
            {isLoading ? '処理中...' : (isRegister ? '登録' : 'ログイン')}
          </button>
        </form>
        
        <div className="divider">
          <span>または</span>
        </div>
        
        {/* ソーシャルログインボタン */}
        <div className="social-login">
          <button
            onClick={handleGoogleLogin}
            disabled={isLoading}
            className="btn btn-google"
          >
            <span className="icon">🔍</span>
            Googleでログイン
          </button>
          
          <button
            onClick={handleLineLogin}
            disabled={isLoading}
            className="btn btn-line"
          >
            <span className="icon">💬</span>
            LINEでログイン
          </button>
          
          <button
            onClick={handleDummyLogin}
            disabled={isLoading}
            className="btn btn-dummy"
          >
            <span className="icon">🧪</span>
            ダミーログイン（テスト用）
          </button>
        </div>
        
        {/* 登録/ログイン切り替え */}
        <div className="toggle-form">
          <button
            type="button"
            onClick={() => setIsRegister(!isRegister)}
            className="toggle-button"
          >
            {isRegister ? '既にアカウントをお持ちの方はこちら' : '新規登録はこちら'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default Login 