import React from 'react'
import { Link } from 'react-router-dom'
import './TermsOfService.css'

const TermsOfService: React.FC = () => {
  return (
    <div className="terms-container">
      <Link to="/" className="back-button">
        ← 戻る
      </Link>
      
      <div className="terms-content">
        <h1>利用規約</h1>
        <p className="last-updated">最終更新日: 2025年1月</p>
        
        <div className="terms-section">
          <h2>第1条（適用）</h2>
          <p>本規約は、当社が提供する会議要約アプリケーション（以下「本サービス」）の利用に関する条件を定めるものです。</p>
        </div>
        
        <div className="terms-section">
          <h2>第2条（登録）</h2>
          <p>本サービスの利用を希望する者は、本規約に同意の上、当社の定める方法により登録を行うものとします。</p>
        </div>
        
        <div className="terms-section">
          <h2>第3条（利用料金）</h2>
          <p>本サービスの利用料金は、当社が別途定める料金体系に従うものとします。</p>
        </div>
        
        <div className="terms-section">
          <h2>第4条（禁止事項）</h2>
          <p>利用者は、本サービスの利用にあたり、以下の行為をしてはなりません：</p>
          <ol>
            <li>法令または公序良俗に違反する行為</li>
            <li>犯罪行為に関連する行為</li>
            <li>当社のサーバーまたはネットワークの機能を破壊する行為</li>
            <li>他の利用者に迷惑をかける行為</li>
          </ol>
        </div>
        
        <div className="terms-section">
          <h2>第5条（サービスの停止）</h2>
          <p>当社は、以下のいずれかの事由があると判断した場合、利用者に事前に通知することなく本サービスの全部または一部の提供を停止することがあります。</p>
        </div>
        
        <div className="terms-section">
          <h2>第6条（利用制限）</h2>
          <p>当社は、利用者が以下のいずれかに該当する場合、事前の通知なく、利用者に対して、本サービスの全部もしくは一部の利用を制限することがあります。</p>
        </div>
        
        <div className="terms-section">
          <h2>第7条（免責事項）</h2>
          <p>当社は、本サービスに関して、利用者と他の利用者または第三者との間において生じた取引、連絡または紛争等について一切責任を負いません。</p>
        </div>
        
        <div className="terms-section">
          <h2>第8条（サービス内容の変更等）</h2>
          <p>当社は、利用者に通知することなく、本サービスの内容を変更しまたは本サービスの提供を中止することができるものとし、これによって利用者に生じた損害について一切の責任を負いません。</p>
        </div>
        
        <div className="terms-section">
          <h2>第9条（利用規約の変更）</h2>
          <p>当社は、必要と判断した場合には、利用者に通知することなくいつでも本規約を変更することができるものとします。</p>
        </div>
        
        <div className="terms-section">
          <h2>第10条（通知または連絡）</h2>
          <p>利用者と当社との間の通知または連絡は、当社の定める方法によって行うものとします。</p>
        </div>
        
        <div className="terms-section">
          <h2>第11条（権利義務の譲渡の禁止）</h2>
          <p>利用者は、当社の書面による事前の承諾なく、利用契約上の地位または本規約に基づく権利もしくは義務を第三者に譲渡し、または担保に供することはできません。</p>
        </div>
        
        <div className="terms-section">
          <h2>第12条（準拠法・裁判管轄）</h2>
          <p>本規約の解釈にあたっては、日本法を準拠法とします。また、本サービスに関して紛争が生じた場合には、当社の本店所在地を管轄する裁判所を専属的合意管轄とします。</p>
        </div>
      </div>
    </div>
  )
}

export default TermsOfService 