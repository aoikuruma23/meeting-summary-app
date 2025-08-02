import React from 'react';
import './Help.css';

const Help: React.FC = () => {
  return (
    <div className="help-container">
      <div className="help-content">
        <h1>📚 ヘルプ・サポート</h1>
        
        <section className="help-section">
          <h2>🎯 基本的な使い方</h2>
          <div className="help-item">
            <h3>1. 録音の開始</h3>
            <ol>
              <li>ホーム画面で「録音開始」ボタンをクリック</li>
              <li>会議のタイトルと参加者を入力</li>
              <li>マイクの許可を承認</li>
              <li>「録音開始」で録音を開始</li>
            </ol>
          </div>
          
          <div className="help-item">
            <h3>2. 録音の停止</h3>
            <ol>
              <li>録音中に「録音停止」ボタンをクリック</li>
              <li>自動的に要約が生成されます</li>
              <li>処理完了までお待ちください</li>
            </ol>
          </div>
          
          <div className="help-item">
            <h3>3. 要約の確認</h3>
            <ol>
              <li>「履歴」ページで録音一覧を確認</li>
              <li>録音をクリックして要約を表示</li>
              <li>プレミアム会員はPDF/Wordでダウンロード可能</li>
            </ol>
          </div>
        </section>

        <section className="help-section">
          <h2>💎 プレミアム機能</h2>
          <div className="help-item">
            <h3>プレミアム会員の特典</h3>
            <ul>
              <li>✅ 録音時間：2時間（無料版は30分）</li>
              <li>✅ PDF出力機能</li>
              <li>✅ Word出力機能</li>
              <li>✅ 無制限の使用回数</li>
              <li>✅ 優先サポート</li>
            </ul>
          </div>
          
          <div className="help-item">
            <h3>プレミアムへのアップグレード</h3>
            <ol>
              <li>「設定」ページに移動</li>
              <li>「プレミアムプランにアップグレード」をクリック</li>
              <li>Stripeで安全に決済</li>
              <li>即座にプレミアム機能が利用可能</li>
            </ol>
          </div>
        </section>

        <section className="help-section">
          <h2>🔧 トラブルシューティング</h2>
          <div className="help-item">
            <h3>よくある問題と解決方法</h3>
            
            <div className="troubleshoot-item">
              <h4>Q: マイクが認識されません</h4>
              <p>A: ブラウザの設定でマイクの許可を確認してください。Chrome、Edge、Safariを推奨します。</p>
            </div>
            
            <div className="troubleshoot-item">
              <h4>Q: 録音が途中で止まります</h4>
              <p>A: 無料版は30分まで、プレミアム版は2時間まで録音可能です。長時間の録音にはプレミアム版をご利用ください。</p>
            </div>
            
            <div className="troubleshoot-item">
              <h4>Q: 要約が生成されません</h4>
              <p>A: 音声が小さすぎる場合があります。マイクに近づいて話してください。また、インターネット接続を確認してください。</p>
            </div>
            
            <div className="troubleshoot-item">
              <h4>Q: PDF/Word出力ができません</h4>
              <p>A: プレミアム会員のみ利用可能です。「設定」ページからプレミアムにアップグレードしてください。</p>
            </div>
          </div>
        </section>

        <section className="help-section">
          <h2>📞 サポート</h2>
          <div className="help-item">
            <h3>お問い合わせ</h3>
            <p>問題が解決しない場合は、以下の方法でサポートにお問い合わせください：</p>
            <ul>
              <li>📧 メール: support@meeting-summary-app.com</li>
              <li>💬 チャット: アプリ内チャット（プレミアム会員）</li>
              <li>📱 電話: 平日 9:00-18:00（プレミアム会員）</li>
            </ul>
          </div>
        </section>

        <section className="help-section">
          <h2>🔒 プライバシー・セキュリティ</h2>
          <div className="help-item">
            <h3>データの取り扱い</h3>
            <ul>
              <li>✅ 音声データは暗号化して保存</li>
              <li>✅ 要約データは安全に管理</li>
              <li>✅ 決済情報はStripeで安全に処理</li>
              <li>✅ 個人情報は適切に保護</li>
            </ul>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Help; 