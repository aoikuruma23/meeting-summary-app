import React from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

const Footer: React.FC = () => {
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
            <li><Link to="/">ホーム</Link></li>
            <li><Link to="/help">ヘルプ</Link></li>
            <li><Link to="/privacy">プライバシーポリシー</Link></li>
            <li><Link to="/terms">利用規約</Link></li>
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
  );
};

export default Footer; 