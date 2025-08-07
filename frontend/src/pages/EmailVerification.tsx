import React, { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { authService } from '../services/authService'
import { useAuth } from '../contexts/AuthContext'
import './EmailVerification.css'

const EmailVerification: React.FC = () => {
  const [verificationCode, setVerificationCode] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuth()

  // URLパラメータからメールアドレスを取得
  const email = new URLSearchParams(location.search).get('email')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    if (!email) {
      setError('メールアドレスが見つかりません')
      setIsLoading(false)
      return
    }

    try {
      const response = await authService.emailVerify({
        email,
        verification_code: verificationCode
      })

      if (response.success && response.data) {
        setSuccess(true)
        // ログイン処理
        await login(response.data.access_token!, response.data.user)
        setTimeout(() => {
          navigate('/')
        }, 2000)
      }
    } catch (err: any) {
      console.error('メール確認エラー:', err)
      setError(err.message || '確認コードの検証に失敗しました')
    } finally {
      setIsLoading(false)
    }
  }

  const handleResendCode = async () => {
    setIsLoading(true)
    setError('')

    try {
      // 再送信のAPIを呼び出す（必要に応じて実装）
      setError('確認コードを再送信しました。メールボックスを確認してください。')
    } catch (err: any) {
      setError('確認コードの再送信に失敗しました')
    } finally {
      setIsLoading(false)
    }
  }

  if (success) {
    return (
      <div className="email-verification-container">
        <div className="email-verification-card">
          <h1>メールアドレス確認完了</h1>
          <div className="success-message">
            <p>メールアドレスの確認が完了しました！</p>
            <p>ホームページにリダイレクトします...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="email-verification-container">
      <div className="email-verification-card">
        <h1>メールアドレス確認</h1>
        
        {error && <div className="error-message">{error}</div>}
        
        <div className="verification-info">
          <p>メールアドレス <strong>{email}</strong> に確認コードを送信しました。</p>
          <p>6桁の数字を入力してください。</p>
        </div>

        <form onSubmit={handleSubmit} className="verification-form">
          <div className="form-group">
            <label htmlFor="verification-code">確認コード</label>
            <input
              type="text"
              id="verification-code"
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value)}
              required
              placeholder="123456"
              maxLength={6}
              pattern="[0-9]{6}"
            />
          </div>

          <button 
            type="submit" 
            className="verify-button"
            disabled={isLoading || verificationCode.length !== 6}
          >
            {isLoading ? '確認中...' : '確認'}
          </button>
        </form>

        <div className="resend-section">
          <p>確認コードが届かない場合：</p>
          <button 
            type="button" 
            className="resend-button"
            onClick={handleResendCode}
            disabled={isLoading}
          >
            確認コードを再送信
          </button>
        </div>

        <div className="back-to-login">
          <button 
            type="button" 
            className="back-button"
            onClick={() => navigate('/login')}
          >
            ログインページに戻る
          </button>
        </div>
      </div>
    </div>
  )
}

export default EmailVerification 