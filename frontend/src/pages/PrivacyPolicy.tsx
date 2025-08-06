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
        <p className="last-updated">最終更新日: 2025年1月27日</p>
        
        <div className="privacy-section">
          <h2>1. 事業者の名称</h2>
          <p>Meeting Summary App（以下「当社」）</p>
        </div>
        
        <div className="privacy-section">
          <h2>2. 個人情報の収集</h2>
          <p>当社は、本サービスの提供にあたり、以下の個人情報を収集いたします：</p>
          <h3>2.1 認証情報</h3>
          <ul>
            <li>メールアドレス（Google認証、LINE認証、メール認証）</li>
            <li>お名前（表示名）</li>
            <li>プロフィール画像</li>
            <li>認証プロバイダー情報（Google、LINE）</li>
            <li>認証プロバイダーのユーザーID</li>
          </ul>
          
          <h3>2.2 サービス利用情報</h3>
          <ul>
            <li>音声録音データ（会議・ミーティングの録音）</li>
            <li>音声文字起こしデータ</li>
            <li>AI生成要約データ</li>
            <li>利用履歴・使用統計</li>
            <li>エクスポートファイル（PDF、Word）</li>
          </ul>
          
          <h3>2.3 決済情報</h3>
          <ul>
            <li>Stripe決済情報（クレジットカード情報はStripeが管理）</li>
            <li>サブスクリプション情報</li>
            <li>支払い履歴</li>
          </ul>
        </div>
        
        <div className="privacy-section">
          <h2>3. 個人情報の利用目的</h2>
          <p>収集した個人情報は、以下の目的で利用いたします：</p>
          <ul>
            <li>本サービスの提供（音声録音、文字起こし、AI要約）</li>
            <li>ユーザー認証・アカウント管理</li>
            <li>決済処理・サブスクリプション管理</li>
            <li>お客様サポート・お問い合わせ対応</li>
            <li>サービスの改善・新機能開発</li>
            <li>セキュリティ対策・不正利用防止</li>
            <li>法令に基づく対応</li>
          </ul>
        </div>
        
        <div className="privacy-section">
          <h2>4. 個人情報の第三者提供</h2>
          <p>当社は、以下の場合を除き、個人情報を第三者に提供いたしません：</p>
          <ul>
            <li>お客様の事前の同意がある場合</li>
            <li>法令に基づく場合</li>
            <li>人の生命、身体または財産の保護のために必要な場合</li>
            <li>公衆衛生の向上または児童の健全な育成の推進のために特に必要な場合</li>
          </ul>
          
          <h3>4.1 委託先への提供</h3>
          <p>当社は、以下の委託先に個人情報の処理を委託する場合があります：</p>
          <ul>
            <li>OpenAI（音声文字起こし・AI要約処理）</li>
            <li>Stripe（決済処理）</li>
            <li>Google（認証処理）</li>
            <li>LINE（認証処理）</li>
            <li>Render（ホスティング・データベース管理）</li>
          </ul>
        </div>
        
        <div className="privacy-section">
          <h2>5. 個人情報の管理・セキュリティ</h2>
          <p>当社は、個人情報の正確性及び安全性を確保するために、以下のセキュリティ対策を実施します：</p>
          <ul>
            <li>SSL暗号化通信の使用</li>
            <li>データベースの暗号化</li>
            <li>アクセス制御・認証システム</li>
            <li>定期的なセキュリティ監査</li>
            <li>従業員への個人情報保護教育</li>
          </ul>
        </div>
        
        <div className="privacy-section">
          <h2>6. 個人情報の保存期間</h2>
          <p>当社は、以下の期間、個人情報を保存いたします：</p>
          <ul>
            <li>アカウント情報：サービス利用期間中</li>
            <li>音声データ：30日間（自動削除）</li>
            <li>要約データ：サービス利用期間中</li>
            <li>決済情報：法令で定められた期間</li>
          </ul>
        </div>
        
        <div className="privacy-section">
          <h2>7. 個人情報の開示・訂正・利用停止</h2>
          <p>お客様は、当社に対して、個人情報の開示、訂正、利用停止を求めることができます。その場合は、以下の方法によりお申し込みください：</p>
          <ul>
            <li>メール: jibunkaikakulab@gmail.com</li>
            <li>LINE: @meeting-summary-app</li>
          </ul>
          <p>※ 開示等の請求により、当社が開示等を行う場合は、お客様ご本人であることを確認させていただきます。</p>
        </div>
        
        <div className="privacy-section">
          <h2>8. アクセス解析ツールについて</h2>
          <p>当社は、お客様により良いサービスを提供するため、アクセス解析ツールを使用しております。アクセス解析ツールは、お客様の個人情報を収集することはありません。</p>
        </div>
        
        <div className="privacy-section">
          <h2>9. クッキー（Cookie）の使用</h2>
          <p>当社は、お客様により良いサービスを提供するため、クッキーを使用することがあります。クッキーの使用を希望されない場合は、ブラウザの設定により、クッキーを無効にすることができます。</p>
        </div>
        
        <div className="privacy-section">
          <h2>10. 未成年者の個人情報について</h2>
          <p>未成年者のお客様が個人情報を提供する場合は、保護者の同意を得てから提供してください。</p>
        </div>
        
        <div className="privacy-section">
          <h2>11. プライバシーポリシーの変更</h2>
          <p>当社は、必要に応じて、本プライバシーポリシーを変更することがあります。重要な変更がある場合は、お客様に通知いたします。</p>
        </div>
        
        <div className="privacy-section">
          <h2>12. お問い合わせ</h2>
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