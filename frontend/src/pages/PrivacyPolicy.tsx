import React, { useEffect } from 'react'
import { Link } from 'react-router-dom'
import './PrivacyPolicy.css'

const PrivacyPolicy: React.FC = () => {
  useEffect(() => {
    // ページトップにスクロール
    window.scrollTo(0, 0)
  }, [])

  return (
    <div className="privacy-container">
      <Link to="/" className="back-button">
        ← 戻る
      </Link>
      
      <div className="privacy-content">
        <h1>プライバシーポリシー</h1>
        <p className="last-updated">最終更新日: 2025年1月</p>
        
        <div className="privacy-section">
          <h2>1. 個人情報の収集</h2>
          <p>当社は、本サービスの提供にあたり、以下の個人情報を収集いたします：</p>
          <ul>
            <li>メールアドレス</li>
            <li>お名前</li>
            <li>プロフィール画像</li>
            <li>録音データ</li>
            <li>要約データ</li>
          </ul>
        </div>
        
        <div className="privacy-section">
          <h2>2. 個人情報の利用目的</h2>
          <p>収集した個人情報は、以下の目的で利用いたします：</p>
          <ul>
            <li>本サービスの提供</li>
            <li>お客様サポート</li>
            <li>サービスの改善</li>
            <li>法令に基づく対応</li>
          </ul>
        </div>
        
        <div className="privacy-section">
          <h2>3. 個人情報の第三者提供</h2>
          <p>当社は、以下の場合を除き、個人情報を第三者に提供いたしません：</p>
          <ul>
            <li>お客様の同意がある場合</li>
            <li>法令に基づく場合</li>
            <li>人の生命、身体または財産の保護のために必要な場合</li>
          </ul>
        </div>
        
        <div className="privacy-section">
          <h2>4. 個人情報の管理</h2>
          <p>当社は、個人情報の正確性及び安全性を確保するために、セキュリティ対策を実施し、個人情報の漏洩、滅失またはき損の防止に努めます。</p>
        </div>
        
        <div className="privacy-section">
          <h2>5. 個人情報の開示・訂正・利用停止</h2>
          <p>お客様は、当社に対して、個人情報の開示、訂正、利用停止を求めることができます。その場合は、当社が定める方法によりお申し込みください。</p>
        </div>
        
        <div className="privacy-section">
          <h2>6. アクセス解析ツールについて</h2>
          <p>当社は、お客様により良いサービスを提供するため、アクセス解析ツールを使用しております。アクセス解析ツールは、お客様の個人情報を収集することはありません。</p>
        </div>
        
        <div className="privacy-section">
          <h2>7. お問い合わせ</h2>
          <p>本プライバシーポリシーに関するお問い合わせは、以下の方法でお願いいたします：</p>
          <ul>
            <li>メール: jibunkaikakulab@gmail.com</li>
            <li>LINE: @meeting-summary-app</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default PrivacyPolicy 