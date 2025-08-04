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
      <div className="home">
        <h1>会議要約アプリへようこそ</h1>
        <p>ログインしてください</p>
        <Link to="/login" className="btn btn-primary">
          ログイン
        </Link>
      </div>
    )
  }

  return (
    <div className="home">
      <h1>会議要約アプリへようこそ</h1>
      <div className="user-info">
        <h2>ようこそ、{user.name}さん！</h2>
        {user.profile_picture && (
          <img 
            src={user.profile_picture} 
            alt="プロフィール画像" 
            className="profile-picture"
          />
        )}
        <p>メール: {user.email}</p>
        <p>プレミアム: {user.is_premium === 'true' ? 'はい' : 'いいえ'}</p>
      </div>
      
      <div className="actions">
        <Link to="/recording" className="btn btn-primary">
          録音開始
        </Link>
        <Link to="/history" className="btn btn-secondary">
          履歴
        </Link>
        <Link to="/billing" className="btn btn-secondary">
          課金設定
        </Link>
        <Link to="/settings" className="btn btn-secondary">
          設定
        </Link>
      </div>
    </div>
  )
}

export default Home 