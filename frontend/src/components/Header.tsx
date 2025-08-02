import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Header.css'

const Header: React.FC = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="header">
      <div className="header-container">
        <Link to="/" className="header-logo">
          <h1>議事録要約</h1>
        </Link>
        
        <nav className="header-nav">
          {user ? (
            <>
              <Link to="/" className="nav-link">ホーム</Link>
              <Link to="/recording" className="nav-link">録音</Link>
              <Link to="/history" className="nav-link">履歴</Link>
              <Link to="/billing" className="nav-link">プラン</Link>
              <Link to="/settings" className="nav-link">設定</Link>
              <Link to="/help" className="nav-link">ヘルプ</Link>
              <div className="user-info">
                <span className="user-name">{user.name}</span>
                {user.is_premium && <span className="premium-badge">プレミアム</span>}
                <button onClick={handleLogout} className="logout-btn">ログアウト</button>
              </div>
            </>
          ) : (
            <Link to="/login" className="nav-link">ログイン</Link>
          )}
        </nav>
      </div>
    </header>
  )
}

export default Header 