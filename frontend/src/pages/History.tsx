import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { recordingService } from '../services/recordingService'
import './History.css'

// interface Summary {
//   summary: string
//   meeting_id: number
// }

interface Meeting {
  id: number
  title: string
  status: string
  drive_file_url: string | null
  created_at: string
  whisper_tokens: number
  gpt_tokens: number
}

const History: React.FC = () => {
  const { user, isNewUser } = useAuth()
  const [meetings, setMeetings] = useState<Meeting[]>([])
  const [loading, setLoading] = useState(true)
  // const [selectedMeeting, setSelectedMeeting] = useState<number | null>(null)
  const [summary, setSummary] = useState<string>('')
  const [showSummary, setShowSummary] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [showNewUserMessage, setShowNewUserMessage] = useState(false)

  useEffect(() => {
    const fetchMeetings = async () => {
      try {
        console.log('DEBUG: 履歴取得開始 - ユーザーID:', user?.id)
        console.log('DEBUG: 新規ユーザーフラグ:', isNewUser)
        
        const response = await recordingService.getRecordingList()
        console.log('DEBUG: 履歴取得レスポンス:', response)
        
        if (response.data && response.data.meetings) {
          setMeetings(response.data.meetings)
          console.log('DEBUG: 取得した履歴数:', response.data.meetings.length)
          
          // 新規ユーザーかどうかを判定（AuthContextのフラグと履歴が0件の場合）
          if (isNewUser || response.data.meetings.length === 0) {
            setShowNewUserMessage(true)
            console.log('DEBUG: 新規ユーザーメッセージを表示')
          } else {
            console.log('DEBUG: 既存ユーザーとして履歴を表示')
          }
        }
      } catch (error) {
        console.error('履歴取得エラー:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchMeetings()
  }, [isNewUser, user?.id])

  const handleViewSummary = async (meetingId: number) => {
    try {
      const response = await recordingService.getSummary(meetingId)
      if (response.data && response.data.summary) {
        setSummary(response.data.summary)
        // setSelectedMeeting(meetingId)
        setShowSummary(true)
      }
    } catch (error) {
      console.error('要約取得エラー:', error)
      alert('要約の取得に失敗しました')
    }
  }

  const handleExport = async (meetingId: number, format: 'pdf' | 'docx') => {
    setExporting(true)
    try {
      const response = await recordingService.exportSummary(meetingId, format)
      if (response.data && response.data.download_url) {
        // ファイルをダウンロード
        const link = document.createElement('a')
        link.href = response.data.download_url
        link.download = response.data.filename || `meeting_${meetingId}.${format}`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }
    } catch (error) {
      console.error('エクスポートエラー:', error)
      alert('エクスポートに失敗しました')
    } finally {
      setExporting(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    
    // 日本時間（JST）に変換
    const jstDate = new Date(date.getTime() + (9 * 60 * 60 * 1000))
    
    return jstDate.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'Asia/Tokyo'
    })
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return '✅'
      case 'processing':
        return '⏳'
      case 'error':
        return '❌'
      default:
        return '📝'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return '完了'
      case 'processing':
        return '処理中'
      case 'error':
        return 'エラー'
      default:
        return '不明'
    }
  }

  // 文字数を概算で計算（Whisperトークンから）
  const getCharacterCount = (whisperTokens: number) => {
    // 概算: 1トークン ≈ 4文字
    return Math.round(whisperTokens * 4)
  }

  // 処理時間を概算で計算（GPTトークンから）
  const getProcessingTime = (gptTokens: number) => {
    // 概算: 1トークン ≈ 0.1秒
    const seconds = Math.round(gptTokens * 0.1)
    if (seconds < 60) {
      return `${seconds}秒`
    } else {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}分${remainingSeconds}秒`
    }
  }

  if (loading) {
    return (
      <div className="history-container">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>履歴を読み込み中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="history-container">
      <div className="history-header">
        <h1>📋 議事録履歴</h1>
        <p>過去の議事録を確認・ダウンロードできます</p>
      </div>

      {showNewUserMessage ? (
        <div className="new-user-welcome">
          <div className="welcome-icon">🎉</div>
          <h2>ようこそ！</h2>
          <p>初回ログインですね。録音を開始して、最初の議事録を作成しましょう。</p>
          <div className="welcome-actions">
            <button 
              onClick={() => window.location.href = '/recording'}
              className="welcome-btn"
            >
              🎤 録音を開始する
            </button>
          </div>
        </div>
      ) : meetings.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📝</div>
          <h2>議事録がありません</h2>
          <p>録音を開始して、最初の議事録を作成しましょう</p>
        </div>
      ) : (
        <div className="meetings-grid">
          {meetings.map((meeting) => (
            <div key={meeting.id} className="meeting-card">
              <div className="meeting-header">
                <div className="meeting-status">
                  <span className="status-icon">{getStatusIcon(meeting.status)}</span>
                  <span className="status-text">{getStatusText(meeting.status)}</span>
                </div>
                <div className="meeting-date">
                  {formatDate(meeting.created_at)}
                </div>
              </div>
              
              <div className="meeting-content">
                <h3 className="meeting-title">{meeting.title}</h3>
                
                <div className="meeting-stats">
                  <div className="stat-item">
                    <span className="stat-icon">📝</span>
                    <span className="stat-label">文字数</span>
                    <span className="stat-value">{getCharacterCount(meeting.whisper_tokens || 0)}文字</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-icon">⏱️</span>
                    <span className="stat-label">処理時間</span>
                    <span className="stat-value">{getProcessingTime(meeting.gpt_tokens || 0)}</span>
                  </div>
                </div>
              </div>
              
              <div className="meeting-actions">
                <button
                  onClick={() => handleViewSummary(meeting.id)}
                  className="action-btn view-summary"
                  disabled={meeting.status !== 'completed'}
                >
                  👁️ 要約を見る
                </button>
                
                {user?.is_premium && meeting.status === 'completed' && (
                  <div className="export-buttons">
                    <button
                      onClick={() => handleExport(meeting.id, 'pdf')}
                      className="action-btn export-pdf"
                      disabled={exporting}
                    >
                      📄 PDF
                    </button>
                    <button
                      onClick={() => handleExport(meeting.id, 'docx')}
                      className="action-btn export-docx"
                      disabled={exporting}
                    >
                      📝 Word
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {showSummary && (
        <div className="summary-modal">
          <div className="summary-content">
            <div className="summary-header">
              <h2>📝 議事録要約</h2>
              <button
                onClick={() => setShowSummary(false)}
                className="close-btn"
              >
                ✕
              </button>
            </div>
            <div className="summary-text">
              <pre>{summary}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default History 