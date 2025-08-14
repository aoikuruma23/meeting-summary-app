import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Header.css'

const Header: React.FC = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null)
  const [canInstall, setCanInstall] = useState(false)

  const scrollToTop = () => {
    try {
      window.scrollTo({ top: 0, left: 0, behavior: 'auto' })
    } catch {
      window.scrollTo(0, 0)
    }
  }

  // PWA: beforeinstallprompt を保持して「インストール」ボタンを表示
  useEffect(() => {
    const handler = (e: any) => {
      e.preventDefault()
      setDeferredPrompt(e)
      setCanInstall(true)
    }
    window.addEventListener('beforeinstallprompt', handler as any)
    return () => window.removeEventListener('beforeinstallprompt', handler as any)
  }, [])

  const handleInstall = async () => {
    try {
      if (!deferredPrompt) return
      deferredPrompt.prompt()
      const { outcome } = await deferredPrompt.userChoice
      if (outcome === 'accepted') setCanInstall(false)
      setDeferredPrompt(null)
    } catch {}
  }

  const handleLogout = () => {
    logout()
    scrollToTop()
    navigate('/login')
  }

  return (
    <header className="header">
      <div className="header-container">
        <Link to="/" className="header-logo" onClick={scrollToTop}>
          <h1>議事録要約</h1>
        </Link>
        
        <nav className="header-nav">
          {user ? (
            <>
              <Link to="/" className="nav-link" onClick={scrollToTop}>ホーム</Link>
              <Link to="/recording" className="nav-link" onClick={scrollToTop}>録音</Link>
              <Link to="/history" className="nav-link" onClick={scrollToTop}>履歴</Link>
              <Link to="/billing" className="nav-link" onClick={scrollToTop}>プラン</Link>
              <Link to="/settings" className="nav-link" onClick={scrollToTop}>設定</Link>
              <Link to="/help" className="nav-link" onClick={scrollToTop}>ヘルプ</Link>
              {canInstall && (
                <button className="install-btn" onClick={handleInstall}>インストール</button>
              )}
              <div className="user-info">
                <span className="user-name">{user.name}</span>
                {user.is_premium === 'true' && <span className="premium-badge">プレミアム</span>}
                <button onClick={handleLogout} className="logout-btn">ログアウト</button>
              </div>
            </>
            ) : (
            <>
              {canInstall && (
                <button className="install-btn" onClick={handleInstall}>インストール</button>
              )}
              <Link to="/login" className="nav-link" onClick={scrollToTop}>ログイン</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  )
}

export default Header 