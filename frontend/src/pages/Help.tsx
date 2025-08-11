import React, { useEffect } from 'react'
import { Link } from 'react-router-dom'
import './Help.css'

const Help: React.FC = () => {
  useEffect(() => {
    // ページトップにスクロール
    window.scrollTo(0, 0)
  }, [])

  return (
    <div className="help-container">
      <Link to="/" className="back-button">
        ← 戻る
      </Link>
      
      <div className="help-content">
        <h1>ヘルプ</h1>
        
        <div className="help-section">
          <h2>アプリの使い方</h2>
          <h3>1. 録音開始</h3>
          <p>ホーム画面の「録音開始」ボタンをクリックして、会議の録音を開始します。</p>
          
          <h3>2. 録音中</h3>
          <p>録音中は音声がリアルタイムで文字起こしされ、画面に表示されます。</p>
          
          <h3>3. 録音停止</h3>
          <p>録音を停止すると、自動的に要約が生成されます。</p>
          
          <h3>4. 結果確認</h3>
          <p>生成された要約は履歴ページで確認できます。</p>
        </div>
        
        <div className="help-section">
          <h2>よくある質問</h2>
          <h3>Q: 録音時間の制限はありますか？</h3>
          <p>A: 無料プランでは30分、プレミアムプランでは2時間まで録音できます。</p>
          
          <h3>Q: 音声の品質は重要ですか？</h3>
          <p>A: より良い音質の方が文字起こしの精度が向上します。静かな環境での録音をお勧めします。</p>
          
          <h3>Q: 要約の精度はどの程度ですか？</h3>
          <p>A: AI技術を使用して高精度な要約を提供していますが、音声の品質や話者の明瞭さに依存します。</p>
        </div>

        <div className="help-section">
          <h2>特定商取引法に基づく表記</h2>
          
          <h3>事業者の名称</h3>
          <p>自分改革ラボ</p>
          
          <h3>代表者の氏名</h3>
          <p>佐藤 幸弘</p>
          
          <h3>所在地</h3>
          <p>〒100-0001 東京都千代田区千代田1-1-1</p>
          
          <h3>連絡先</h3>
          <ul>
            <li><strong>メールアドレス</strong>: jibunkaikakulab@gmail.com</li>
            <li><strong>電話番号</strong>: 03-1234-5678（平日9:00-18:00）</li>
          </ul>
          
          <h3>料金体系</h3>
          <ul>
            <li><strong>無料プラン</strong>: 月30分まで録音可能</li>
            <li><strong>プレミアムプラン</strong>: 月額980円（税込）、月2時間まで録音可能</li>
          </ul>
          
          <h3>支払い方法</h3>
          <p>クレジットカード決済（Visa、Mastercard、American Express、JCB）</p>
          
          <h3>返品・キャンセルポリシー</h3>
          <ul>
            <li>デジタルコンテンツのため、返品はお受けできません</li>
            <li>プレミアムプランの解約はいつでも可能です</li>
            <li>解約後は次回更新日までサービスをご利用いただけます</li>
          </ul>
          
          <h3>サービス提供開始時期</h3>
          <p>2024年8月1日</p>
          
          <h3>利用規約・プライバシーポリシー</h3>
          <p>本サービスの利用にあたっては、利用規約およびプライバシーポリシーをご確認ください。</p>
        </div>
        
        <div className="help-section">
          <h2>サポート</h2>
          <p>お困りの際は、以下の方法でサポートを受けることができます：</p>
          <ul>
            <li>このヘルプページの確認</li>
            <li>利用規約の確認</li>
            <li>プライバシーポリシーの確認</li>
          </ul>
          
          <h3>お問い合わせ</h3>
          <p>上記で解決しない場合は、以下の方法でお問い合わせください：</p>
          <ul>
            <li><strong>📧 メール</strong>: jibunkaikakulab@gmail.com</li>
            <li><strong>💬 LINE</strong>: @meeting-summary-app</li>
          </ul>
          
          <h3>お問い合わせの際にご準備ください</h3>
          <ul>
            <li>お使いのブラウザ（Chrome、Firefox、Safari等）</li>
            <li>発生している問題の詳細</li>
            <li>エラーメッセージがある場合はその内容</li>
            <li>問題が発生した手順</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default Help 