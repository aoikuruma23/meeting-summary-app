import React, { useEffect } from 'react'
import { Link } from 'react-router-dom'
import './CommercialTransactions.css'

interface Row {
  label: string
  value: React.ReactNode
}

const rows: Row[] = [
  { label: '販売事業者', value: '自分改革ラボ' },
  { label: '運営責任者', value: '佐藤 幸弘' },
  {
    label: '所在地',
    value: (
      <>
        〒160-0023
        <br />
        東京都新宿区西新宿3丁目3番13号 西新宿水間ビル2F
      </>
    ),
  },
  {
    label: '電話番号',
    value: (
      <>
        070-1326-8481
        <br />
        <span className="ct-note">受付時間：平日10:00〜17:00</span>
      </>
    ),
  },
  { label: 'メールアドレス', value: 'jibunkaikakulab@gmail.com' },
  {
    label: '販売価格',
    value: (
      <>
        プレミアムプラン：月額 999円（税込）
        <br />
        <span className="ct-note">
          無料トライアル：登録から31日間、または累計10回まで（いずれか早い方）
        </span>
      </>
    ),
  },
  {
    label: '商品代金以外の必要料金',
    value:
      '本サービスの利用にともなうインターネット通信料・通信機器等の費用は、お客様のご負担となります。',
  },
  {
    label: '支払方法',
    value: (
      <>
        クレジットカード決済（Visa／Mastercard／American Express／JCB）
        <br />
        <span className="ct-note">決済代行：Stripe</span>
      </>
    ),
  },
  {
    label: '支払時期',
    value:
      'プレミアムプランへのお申し込み時に課金され、以降は毎月、同日に自動更新・課金されます。',
  },
  { label: 'サービスの提供時期', value: '決済完了後、ただちにご利用いただけます。' },
  {
    label: '解約について',
    value:
      'いつでも解約いただけます。解約後も、次回更新日まではプレミアム機能をご利用いただけます。日割りでの返金は行っておりません。',
  },
  {
    label: '返品・キャンセル',
    value:
      'デジタルサービスの性質上、決済後の返金・キャンセルはお受けできません。お申し込み前に、無料トライアルにて内容をご確認ください。',
  },
  {
    label: '動作環境',
    value:
      'Chrome／Firefox／Safari などの主要ブラウザ（PC・タブレット）。インストールは不要です。',
  },
]

const CommercialTransactions: React.FC = () => {
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [])

  return (
    <div className="ct-container">
      <Link to="/" className="back-button">
        ← 戻る
      </Link>

      <div className="ct-content">
        <h1>特定商取引法に基づく表記</h1>
        <p className="ct-subtitle">AI議事録アシスタント</p>

        <table className="ct-table">
          <tbody>
            {rows.map((row) => (
              <tr key={row.label}>
                <th scope="row">{row.label}</th>
                <td>{row.value}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <p className="ct-footnote">
          本表記の内容は予告なく変更される場合があります。最新の内容は本ページにてご確認ください。
        </p>
      </div>
    </div>
  )
}

export default CommercialTransactions
