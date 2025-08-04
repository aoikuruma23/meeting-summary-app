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
          <h2>サポート</h2>
          <p>お困りの際は、以下の方法でサポートを受けることができます：</p>
          <ul>
            <li>このヘルプページの確認</li>
            <li>利用規約の確認</li>
            <li>プライバシーポリシーの確認</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default Help 