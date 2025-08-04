import React from 'react';
import { Link } from 'react-router-dom';
import './PrivacyPolicy.css';

const PrivacyPolicy: React.FC = () => {
  return (
    <div className="privacy-policy-container">
      <div className="privacy-policy-card">
        <h1>プライバシーポリシー</h1>
        <p className="last-updated">最終更新日: 2025年8月4日</p>
        
        <section>
          <h2>1. 個人情報の収集について</h2>
          <p>
            当アプリケーション（議事録要約Webアプリ）では、以下の個人情報を収集いたします：
          </p>
          <ul>
            <li>メールアドレス（ログイン時）</li>
            <li>お名前（アカウント作成時）</li>
            <li>Googleアカウント情報（Googleログイン時）</li>
            <li>LINEアカウント情報（LINEログイン時）</li>
            <li>録音データ（会議の音声ファイル）</li>
            <li>利用履歴（録音・要約の履歴）</li>
          </ul>
        </section>

        <section>
          <h2>2. 個人情報の利用目的</h2>
          <p>収集した個人情報は、以下の目的で利用いたします：</p>
          <ul>
            <li>ユーザー認証・アカウント管理</li>
            <li>音声の文字起こし・要約サービス提供</li>
            <li>サービス改善・品質向上</li>
            <li>お客様サポート</li>
            <li>法令に基づく対応</li>
          </ul>
        </section>

        <section>
          <h2>3. 個人情報の第三者提供</h2>
          <p>
            当アプリケーションでは、以下の場合を除き、個人情報を第三者に提供いたしません：
          </p>
          <ul>
            <li>お客様の同意がある場合</li>
            <li>法令に基づく場合</li>
            <li>人の生命、身体または財産の保護のために必要な場合</li>
            <li>公衆衛生の向上または児童の健全な育成の推進のために特に必要な場合</li>
          </ul>
        </section>

        <section>
          <h2>4. 個人情報の管理</h2>
          <p>
            当アプリケーションでは、個人情報の正確性及び安全性確保のために、セキュリティに万全の対策を講じています。
          </p>
        </section>

        <section>
          <h2>5. 個人情報の開示・訂正・削除</h2>
          <p>
            お客様がご本人の個人情報について、開示・訂正・削除を希望される場合には、以下までご連絡ください。
          </p>
          <p>連絡先: support@meeting-summary-app.com</p>
        </section>

        <section>
          <h2>6. クッキーの使用</h2>
          <p>
            当アプリケーションでは、ユーザーエクスペリエンス向上のため、クッキーを使用しています。
            ブラウザの設定でクッキーを無効にすることも可能です。
          </p>
        </section>

        <section>
          <h2>7. お問い合わせ</h2>
          <p>
            プライバシーポリシーに関するお問い合わせは、以下までご連絡ください：
          </p>
          <p>Email: support@meeting-summary-app.com</p>
        </section>

        <div className="back-button">
          <Link to="/" className="back-link">
            ← ホームに戻る
          </Link>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicy; 