import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { authService } from '../services/authService'
import './Home.css'

const Home: React.FC = () => {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const [isProcessing, setIsProcessing] = useState(false)

  useEffect(() => {
    // Google認証のコールバック処理
    const handleGoogleAuth = async () => {
      try {
        const hash = window.location.hash
        if (hash && hash.includes('id_token')) {
          console.log('DEBUG: Google認証トークンを検出')
          const idToken = hash.split('id_token=')[1].split('&')[0]
          
          const response = await authService.googleAuth(idToken)
          
          if (response.success && response.data) {
            await login(response.data.access_token, response.data.user)
            window.history.replaceState({}, document.title, window.location.pathname)
            navigate('/')
          }
        }
      } catch (error) {
        console.error('Google認証エラー:', error)
      }
    }

    // LINE認証のコールバック処理
    const handleLineAuth = async () => {
      if (isProcessing) return // 処理中の場合は何もしない
      
      try {
        const urlParams = new URLSearchParams(window.location.search)
        const code = urlParams.get('code')
        const state = urlParams.get('state')
        
        if (code && state === 'line') {
          console.log('DEBUG: LINE認証コードを検出')
          setIsProcessing(true)
          
          const response = await authService.lineAuth(code)
          
          if (response.success && response.data) {
            await login(response.data.access_token, response.data.user)
            window.history.replaceState({}, document.title, window.location.pathname)
            navigate('/')
          }
        }
      } catch (error) {
        console.error('LINE認証エラー:', error)
      } finally {
        setIsProcessing(false)
      }
    }

    handleGoogleAuth()
    handleLineAuth()
  }, [login, navigate, isProcessing])

  if (!user) {
    return (
      <div className="home-container">
        {/* ヒーローセクション */}
        <div className="hero-section">
          <div className="hero-content">
            <h1 className="hero-title">
              🎤 AI議事録アシスタント
            </h1>
            <p className="hero-subtitle">
              会議音声を自動で文字起こし・要約
            </p>
            <p className="hero-description">
              面倒な議事録作成を自動化。会議に集中して、<br />
              重要なポイントを逃さず記録できます。
            </p>
            <div className="hero-actions">
              <Link to="/login" className="cta-button primary">
                🚀 無料で始める
              </Link>
              <Link to="/help" className="cta-button secondary">
                📖 使い方を確認
              </Link>
            </div>
          </div>
          <div className="hero-stats">
            <div className="stat-item">
              <span className="stat-number">99%</span>
              <span className="stat-label">精度</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">2時間</span>
              <span className="stat-label">最大録音時間</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">5分</span>
              <span className="stat-label">処理時間</span>
            </div>
          </div>
        </div>

        {/* 機能紹介セクション */}
        <div className="features-section">
          <h2 className="section-title">✨ 主な機能</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🎤</div>
              <h3>ワンクリック録音</h3>
              <p>ブラウザ上で簡単録音。リアルタイムで音声を処理し、高品質な文字起こしを実現します。</p>
              <ul className="feature-details">
                <li>ブラウザ標準API使用</li>
                <li>リアルタイム処理</li>
                <li>自動チャンク分割</li>
              </ul>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🤖</div>
              <h3>AI文字起こし</h3>
              <p>OpenAI Whisperによる高精度な日本語音声認識。専門用語や人名も正確に認識します。</p>
              <ul className="feature-details">
                <li>OpenAI Whisper使用</li>
                <li>日本語対応</li>
                <li>専門用語対応</li>
              </ul>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📝</div>
              <h3>AI自動要約</h3>
              <p>ChatGPTによる高度な要約機能。重要なポイント、アクションアイテム、決定事項を自動抽出。</p>
              <ul className="feature-details">
                <li>ChatGPT 4.0使用</li>
                <li>構造化要約</li>
                <li>アクション抽出</li>
              </ul>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📁</div>
              <h3>履歴管理・エクスポート</h3>
              <p>過去の議事録を簡単に確認。PDF・Word形式でエクスポート可能。共有も簡単です。</p>
              <ul className="feature-details">
                <li>PDF/Word出力</li>
                <li>検索機能</li>
                <li>共有機能</li>
              </ul>
            </div>
          </div>
        </div>

        {/* 使用例セクション */}
        <div className="use-cases-section">
          <h2 className="section-title">💼 活用シーン</h2>
          <div className="use-cases-grid">
            <div className="use-case-card">
              <div className="use-case-icon">🏢</div>
              <h3>企業会議</h3>
              <p>取締役会、部門会議、プロジェクト会議など、様々な企業会議での議事録作成を効率化。</p>
            </div>
            <div className="use-case-card">
              <div className="use-case-icon">🎓</div>
              <h3>教育・研修</h3>
              <p>セミナー、研修、講義の内容を記録。重要なポイントを逃さず学習できます。</p>
            </div>
            <div className="use-case-card">
              <div className="use-case-icon">👥</div>
              <h3>チームミーティング</h3>
              <p>リモートワーク、ハイブリッド会議での議事録作成。参加者全員で情報共有。</p>
            </div>
            <div className="use-case-card">
              <div className="use-case-icon">📊</div>
              <h3>インタビュー・調査</h3>
              <p>顧客インタビュー、市場調査、ユーザーリサーチの記録と分析。</p>
            </div>
          </div>
        </div>

        {/* 料金プランセクション */}
        <div className="pricing-section">
          <h2 className="section-title">💰 料金プラン</h2>
          <div className="pricing-grid">
            <div className="pricing-card free">
              <div className="pricing-header">
                <h3>無料プラン</h3>
                <div className="price">¥0</div>
                <p className="price-period">/月</p>
              </div>
              <ul className="pricing-features">
                <li>✅ 30分までの録音</li>
                <li>✅ 31日＋翌月1日まで利用</li>
                <li>✅ またはトータル10回まで利用</li>
                <li>✅ 基本的な要約機能</li>
                <li>✅ 履歴保存</li>
                <li>❌ エクスポート機能</li>
                <li>❌ 優先サポート</li>
              </ul>
              <Link to="/login" className="pricing-button">
                無料で始める
              </Link>
            </div>
            <div className="pricing-card premium">
              <div className="pricing-badge">人気</div>
              <div className="pricing-header">
                <h3>プレミアムプラン</h3>
                <div className="price">¥980</div>
                <p className="price-period">/月</p>
              </div>
              <ul className="pricing-features">
                <li>✅ 2時間までの録音</li>
                <li>✅ 無制限利用</li>
                <li>✅ 高度な要約機能</li>
                <li>✅ PDF/Wordエクスポート</li>
                <li>✅ 優先サポート</li>
                <li>✅ カスタム設定</li>
              </ul>
              <Link to="/login" className="pricing-button premium">
                プレミアムにアップグレード
              </Link>
            </div>
          </div>
        </div>

        {/* 技術仕様セクション */}
        <div className="tech-specs-section">
          <h2 className="section-title">🔧 技術仕様</h2>
          <div className="tech-specs-grid">
            <div className="tech-spec-card">
              <h3>音声処理</h3>
              <ul>
                <li>フォーマット: WAV, MP3, OGG</li>
                <li>サンプリングレート: 44.1kHz</li>
                <li>ビット深度: 16bit</li>
                <li>チャンクサイズ: 10MB</li>
              </ul>
            </div>
            <div className="tech-spec-card">
              <h3>AI技術</h3>
              <ul>
                <li>文字起こし: OpenAI Whisper</li>
                <li>要約: OpenAI ChatGPT 4.0</li>
                <li>言語: 日本語対応</li>
                <li>精度: 99%以上</li>
              </ul>
            </div>
            <div className="tech-spec-card">
              <h3>セキュリティ</h3>
              <ul>
                <li>通信: HTTPS暗号化</li>
                <li>データ: AES-256暗号化</li>
                <li>認証: JWT + OAuth2.0</li>
                <li>決済: Stripe標準</li>
              </ul>
            </div>
            <div className="tech-spec-card">
              <h3>対応環境</h3>
              <ul>
                <li>ブラウザ: Chrome, Firefox, Safari</li>
                <li>OS: Windows, Mac, Linux</li>
                <li>デバイス: PC, タブレット</li>
                <li>ネットワーク: 安定したインターネット接続</li>
              </ul>
            </div>
          </div>
        </div>

        {/* CTAセクション */}
        <div className="final-cta-section">
          <h2>🚀 今すぐ始めましょう</h2>
          <p>面倒な議事録作成から解放され、会議に集中できる環境を提供します。</p>
          <div className="cta-actions">
            <Link to="/login" className="cta-button primary large">
              🎤 無料で録音開始
            </Link>
            <Link to="/help" className="cta-button secondary">
              📖 詳細を見る
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="home-container">
      <div className="user-welcome">
        <h1>👋 ようこそ、{user.name || user.email}さん</h1>
        <div className="user-stats">
          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <h3>利用回数</h3>
            <p className="stat-value">{user.usage_count || 0}回</p>
          </div>
          <div className="stat-card">
            <div className="stat-icon">{user.is_premium === 'true' ? '⭐' : '📋'}</div>
            <h3>プラン</h3>
            <p className="stat-value">{user.is_premium === 'true' ? 'プレミアム' : '無料プラン'}</p>
          </div>
        </div>
      </div>
      
      <div className="main-actions">
        <h2>🎯 今すぐ始める</h2>
        <div className="action-grid">
          <Link to="/recording" className="main-action-button recording">
            <div className="action-icon">🎤</div>
            <div className="action-content">
              <h3>録音開始</h3>
              <p>新しい会議の録音を開始します</p>
            </div>
            <div className="action-arrow">→</div>
          </Link>
          
          <Link to="/history" className="main-action-button history">
            <div className="action-icon">📋</div>
            <div className="action-content">
              <h3>履歴確認</h3>
              <p>過去の議事録を確認・ダウンロード</p>
            </div>
            <div className="action-arrow">→</div>
          </Link>
          
          <Link to="/settings" className="main-action-button settings">
            <div className="action-icon">⚙️</div>
            <div className="action-content">
              <h3>設定・管理</h3>
              <p>アカウント設定とプレミアム機能</p>
            </div>
            <div className="action-arrow">→</div>
          </Link>
        </div>
      </div>
      
      {user.is_premium !== 'true' && (
        <div className="upgrade-section">
          <div className="upgrade-content">
            <h2>⭐ プレミアムプランにアップグレード</h2>
            <p>無制限の利用と追加機能を利用できます</p>
            <ul className="upgrade-features">
              <li>✅ 2時間までの録音（無料は30分）</li>
              <li>✅ PDF/Word形式でエクスポート</li>
              <li>✅ 無制限の使用回数</li>
              <li>✅ 優先サポート</li>
            </ul>
            <Link to="/settings" className="upgrade-button">
              💎 プレミアムにアップグレード
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}

export default Home 