import React from 'react'
import { useNavigate } from 'react-router-dom'
import './Footer.css'

const Footer: React.FC = () => {
  const navigate = useNavigate()

  const scrollToTop = () => {
    window.scrollTo(0, 0)
  }

  const handleHomeClick = () => {
    navigate('/')
    scrollToTop()
  }

  const handleHelpClick = () => {
    navigate('/help')
    scrollToTop()
  }

  const handlePrivacyClick = () => {
    navigate('/privacy')
    scrollToTop()
  }

  const handleTermsClick = () => {
    navigate('/terms')
    scrollToTop()
  }

  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-section">
          <h3>議事録要約Webアプリ</h3>
          <p>会議音声を自動で文字起こし・要約するWebアプリケーション</p>
        </div>
        
        <div className="footer-section">
          <h4>リンク</h4>
          <ul>
            <li><button onClick={handleHomeClick} className="footer-link">ホーム</button></li>
            <li><button onClick={handleHelpClick} className="footer-link">ヘルプ</button></li>
            <li><button onClick={handlePrivacyClick} className="footer-link">プライバシーポリシー</button></li>
            <li><button onClick={handleTermsClick} className="footer-link">利用規約</button></li>
          </ul>
        </div>
        
        <div className="footer-section">
          <h4>お問い合わせ</h4>
          <p>Email: support@meeting-summary-app.com</p>
        </div>
      </div>
      
      <div className="footer-bottom">
        <p>&copy; 2025 議事録要約Webアプリ. All rights reserved.</p>
      </div>
    </footer>
  )
}

export default Footer 