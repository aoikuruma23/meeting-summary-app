import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Header.css'

const Header: React.FC = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null)
  const [isInstalled, setIsInstalled] = useState(false)
  const [installLabel, setInstallLabel] = useState('インストール')

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
      // beforeinstallprompt が来たら保持
    }
    window.addEventListener('beforeinstallprompt', handler as any)
    return () => window.removeEventListener('beforeinstallprompt', handler as any)
  }, [])

  // インストール済みかどうか（デスクトップでも判定）
  useEffect(() => {
    const checkInstalled = () => {
      const standalone = window.matchMedia && window.matchMedia('(display-mode: standalone)').matches
      // iOS Safari
      const iosStandalone = (navigator as any).standalone === true
      setIsInstalled(Boolean(standalone || iosStandalone))
    }
    try {
      checkInstalled()
      const mq = window.matchMedia('(display-mode: standalone)')
      const listener = () => checkInstalled()
      mq.addEventListener?.('change', listener)
      window.addEventListener('appinstalled', checkInstalled)
      return () => {
        mq.removeEventListener?.('change', listener)
        window.removeEventListener('appinstalled', checkInstalled)
      }
    } catch {
      // 失敗しても致命的ではない
    }
  }, [])

  // デバイスに応じたボタン文言
  useEffect(() => {
    try {
      const ua = navigator.userAgent.toLowerCase()
      if (/iphone|ipad|ipod|android/.test(ua)) {
        setInstallLabel('ホーム画面に追加')
      } else {
        setInstallLabel('デスクトップに追加')
      }
    } catch {
      setInstallLabel('インストール')
    }
  }, [])

  const handleInstall = async () => {
    try {
      if (deferredPrompt) {
        deferredPrompt.prompt()
        await deferredPrompt.userChoice
        setDeferredPrompt(null)
        return
      }
      // フォールバック: ブラウザごとの手順を案内
      const ua = navigator.userAgent.toLowerCase()
      if (ua.includes('edg')) {
        alert('インストール手順:\n1. 右上の「…」→ アプリ → このサイトをインストール')
      } else if (ua.includes('chrome')) {
        alert('インストール手順:\n1. アドレスバー右端の「インストール」アイコンをクリック\n   もしくは 右上「⋮」→ インストール')
      } else if (ua.includes('safari') && !ua.includes('chrome')) {
        alert('インストール手順:\n1. 共有アイコン → ホーム画面に追加')
      } else {
        alert('インストール手順:\nブラウザのメニューから「インストール」または「ホーム画面に追加」を選択してください。')
      }
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
              {!isInstalled && (
                <button className="install-btn" onClick={handleInstall}>{installLabel}</button>
              )}
              <div className="user-info">
                <span className="user-name">{user.name}</span>
                {user.is_premium === 'true' && <span className="premium-badge">プレミアム</span>}
                <button onClick={handleLogout} className="logout-btn">ログアウト</button>
              </div>
            </>
            ) : (
            <>
              {!isInstalled && (
                <button className="install-btn" onClick={handleInstall}>{installLabel}</button>
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