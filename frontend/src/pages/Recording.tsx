import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useRecording } from '../contexts/RecordingContext'
import { recordingService } from '../services/recordingService'
import './Recording.css'

const Recording: React.FC = () => {
  const { user } = useAuth()
  const { recordingState, startRecording, stopRecording, uploadChunk: _, resetRecording } = useRecording()
  const navigate = useNavigate()
  
  const [title, setTitle] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null)
  const [chunkInterval, setChunkInterval] = useState<NodeJS.Timeout | null>(null)
  const [chunkNumber, setChunkNumber] = useState(0)
  const [currentMeetingId, setCurrentMeetingId] = useState<number | null>(null)
  const currentMeetingIdRef = useRef<number | null>(null)
  
  // 録音時間関連
  const [recordingTime, setRecordingTime] = useState(0)
  const [maxDuration, setMaxDuration] = useState<number | null>(null)
  const [timeInterval, setTimeInterval] = useState<NodeJS.Timeout | null>(null)
  
  const audioChunks = useRef<Blob[]>([])
  const stream = useRef<MediaStream | null>(null)

  useEffect(() => {
    if (!user) {
      navigate('/login')
    }
  }, [user, navigate])

  const startRecordingHandler = async () => {
    // タイトルが空の場合は現在の日時で自動生成
    const recordingTitle = title.trim() || (() => {
      const now = new Date()
      const year = now.getFullYear()
      const month = String(now.getMonth() + 1).padStart(2, '0')
      const day = String(now.getDate()).padStart(2, '0')
      const hours = String(now.getHours()).padStart(2, '0')
      const minutes = String(now.getMinutes()).padStart(2, '0')
      return `${year}.${month}.${day} ${hours}:${minutes}`
    })()
    
    try {
      // マイクの権限を取得
      const mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
      stream.current = mediaStream
      
      // MediaRecorderを初期化
      const recorder = new MediaRecorder(mediaStream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      
      // データが利用可能になったときのイベントハンドラーを設定
      recorder.ondataavailable = async (event) => {
        if (event.data.size > 0) {
          console.log('音声データ受信:', event.data.size, 'bytes')
          await handleChunkUpload(event.data)
        }
      }
      
      setMediaRecorder(recorder)
      
      // APIで録音開始
      const response = await startRecording(recordingTitle)
      // meetingIdを即座に設定
      if (response && response.data && response.data.meeting) {
        const meetingId = response.data.meeting.id
        setCurrentMeetingId(meetingId)
        currentMeetingIdRef.current = meetingId
        console.log('currentMeetingId設定:', meetingId)
        
        // 録音時間制限を設定（無料ユーザーは30分、プレミアムユーザーは2時間）
        const isPremium = String(user?.is_premium) === "true"
        const maxDuration = isPremium ? 120 : 30
        console.log('フロントエンドプレミアム状態:', user?.is_premium, '判定結果:', isPremium, '最大時間:', maxDuration)
        setMaxDuration(maxDuration)
        setRecordingTime(0)
        
        // 録音開始を少し遅らせて、meetingIdが確実に設定されるようにする
        setTimeout(() => {
          recorder.start(600000) // 10分ごとにデータを取得（コスト効率的）
          setIsRecording(true)
          setChunkNumber(0)
          audioChunks.current = []
          
          // 10分ごとのチャンク化（コスト効率的）
          const interval = setInterval(() => {
            if (recorder.state === 'recording') {
              setChunkNumber(prev => prev + 1)
            }
          }, 600000) // 10分ごと
          
          setChunkInterval(interval)
          
          // 録音時間のカウントダウン開始
          const timeInterval = setInterval(() => {
            setRecordingTime(prev => {
              const newTime = prev + 1
              // 制限時間に達した場合、録音を自動停止
              if (maxDuration && newTime >= maxDuration * 60) {
                stopRecordingHandler()
                return prev
              }
              return newTime
            })
          }, 1000) // 1秒ごと
          
          setTimeInterval(timeInterval)
        }, 100)
      }
    } catch (error) {
      console.error('録音開始エラー:', error)
      alert('録音を開始できませんでした。マイクの権限を確認してください。')
    }
  }

  const stopRecordingHandler = async () => {
    try {
      if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop()
      }
      
      if (stream.current) {
        stream.current.getTracks().forEach(track => track.stop())
      }
      
      if (chunkInterval) {
        clearInterval(chunkInterval)
      }
      
      if (timeInterval) {
        clearInterval(timeInterval)
      }
      
      setIsRecording(false)
      
      // 録音終了APIを呼び出し
      if (currentMeetingId) {
        await stopRecording()
      }
      
      // 状態をリセット
      setRecordingTime(0)
      setMaxDuration(null)
      setCurrentMeetingId(null)
      currentMeetingIdRef.current = null
      setChunkNumber(0)
      
      // 録音コンテキストをリセット
      resetRecording()
      
      // 履歴ページに遷移
      navigate('/history')
      
    } catch (error) {
      console.error('録音停止エラー:', error)
      alert('録音の停止中にエラーが発生しました。')
    }
  }

  const handleChunkUpload = async (audioBlob: Blob) => {
    try {
      if (!currentMeetingIdRef.current) {
        console.log('meetingIdが設定されていません')
        return
      }
      
      console.log('handleChunkUpload開始 - meetingId:', currentMeetingIdRef.current, 'chunkNumber:', chunkNumber)
      console.log('音声データサイズ:', audioBlob.size, 'bytes')
      
      // currentMeetingIdRefを使用して直接APIを呼び出す
      if (currentMeetingIdRef.current) {
        const file = new File([audioBlob], `chunk_${chunkNumber}.webm`, { type: 'audio/webm' })
        await recordingService.uploadChunk(currentMeetingIdRef.current, chunkNumber, file)
      } else {
        console.error('currentMeetingIdRefが設定されていません')
      }
      console.log('チャンクアップロード成功')
      
    } catch (error: any) {
      console.error('チャンクアップロードエラー:', error)
      console.error('エラー詳細:', error.response?.data || error.message)
    }
  }

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const formatRemainingTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }

  const getRemainingTime = () => {
    if (!maxDuration) return null
    const remaining = maxDuration * 60 - recordingTime
    return remaining > 0 ? remaining : 0
  }

  const remainingTime = getRemainingTime()

  return (
    <div className="recording-container">
      <div className="recording-header">
        <h1>🎤 録音・要約</h1>
        <p>会議の録音を開始して、自動で文字起こし・要約を行います</p>
      </div>

      <div className="recording-content">
        {!isRecording ? (
          <div className="recording-setup">
            <div className="setup-card">
              <h2>📝 議事録の設定</h2>
              <div className="input-group">
                <label htmlFor="title">議事録のタイトル</label>
                <input
                  type="text"
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="例: 週次ミーティング 2024年1月"
                  className="title-input"
                />
              </div>
              
              <div className="recording-info">
                <div className="info-card">
                  <div className="info-icon">⏱️</div>
                  <div className="info-content">
                    <h3>録音時間</h3>
                    <p>{user?.is_premium ? '最大2時間' : '最大30分'}</p>
                  </div>
                </div>
                
                <div className="info-card">
                  <div className="info-icon">🤖</div>
                  <div className="info-content">
                    <h3>自動処理</h3>
                    <p>文字起こし・要約を自動実行</p>
                  </div>
                </div>
                
                <div className="info-card">
                  <div className="info-icon">📁</div>
                  <div className="info-content">
                    <h3>保存先</h3>
                    <p>履歴ページで確認・ダウンロード</p>
                  </div>
                </div>
              </div>
              
              <button
                onClick={startRecordingHandler}
                className="start-recording-btn"
              >
                🎤 録音開始
              </button>
            </div>
          </div>
        ) : (
          <div className="recording-active">
            <div className="recording-status">
              <div className="status-indicator recording">
                <div className="pulse-dot"></div>
                <span>録音中</span>
              </div>
              
              <div className="recording-time">
                <div className="time-display">
                  <span className="time-label">録音時間</span>
                  <span className="time-value">{formatTime(recordingTime)}</span>
                </div>
                
                {remainingTime !== null && (
                  <div className="remaining-time">
                    <span className="time-label">残り時間</span>
                    <span className="time-value remaining">{formatRemainingTime(remainingTime)}</span>
                  </div>
                )}
              </div>
              
              <div className="recording-info-active">
                <div className="info-item">
                  <span className="info-label">タイトル:</span>
                  <span className="info-value">{title}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">チャンク数:</span>
                  <span className="info-value">{chunkNumber + 1}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">プラン:</span>
                  <span className="info-value">{user?.is_premium ? 'プレミアム' : '無料'}</span>
                </div>
              </div>
            </div>
            
            <div className="recording-controls">
              <button
                onClick={stopRecordingHandler}
                className="stop-recording-btn"
              >
                ⏹️ 録音停止
              </button>
              
              <div className="recording-tips">
                <h3>💡 録音のコツ</h3>
                <ul>
                  <li>マイクに近い位置で話してください</li>
                  <li>背景音を最小限にしてください</li>
                  <li>一人ずつ話すようにしてください</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Recording 