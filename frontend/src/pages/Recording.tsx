import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useRecording } from '../contexts/RecordingContext'
import { authService } from '../services/authService'
import { recordingService } from '../services/recordingService'
import './Recording.css'

const Recording: React.FC = () => {
  const { user, updateUser } = useAuth()
  const { recordingState: _, startRecording, stopRecording, uploadChunk: __, resetRecording } = useRecording()
  const navigate = useNavigate()
  
  const [title, setTitle] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null)
  const [chunkInterval, setChunkInterval] = useState<NodeJS.Timeout | null>(null)
  const [chunkNumber, setChunkNumber] = useState(0)
  const [currentMeetingId, setCurrentMeetingId] = useState<number | null>(null)
  const currentMeetingIdRef = useRef<number | null>(null)
  const [captureMode, setCaptureMode] = useState<'mic' | 'tab' | 'tabmix'>('mic')
  
  // 録音時間関連
  const [recordingTime, setRecordingTime] = useState(0)
  const [maxDuration, setMaxDuration] = useState<number | null>(null)
  const [timeInterval, setTimeInterval] = useState<NodeJS.Timeout | null>(null)
  
  const audioChunks = useRef<Blob[]>([])
  const stream = useRef<MediaStream | null>(null)
  const displayStreamRef = useRef<MediaStream | null>(null)
  const micStreamRef = useRef<MediaStream | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const finalUploadPromiseRef = useRef<Promise<void> | null>(null)

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
      let mediaStream: MediaStream
      if (captureMode === 'tab' || captureMode === 'tabmix') {
        if (String(user?.is_premium) !== 'true') {
          const goUpgrade = confirm('タブ音声録音はプレミアム限定機能です。プラン画面に移動しますか？')
          if (goUpgrade) navigate('/billing')
          return
        }
        if (!navigator.mediaDevices || !(navigator.mediaDevices as any).getDisplayMedia) {
          alert('このブラウザはタブ音声録音に対応していません。Chromeの最新バージョンをお試しください。')
          return
        }
        console.log('タブ音声権限を確認中...')
        const displayStream = await (navigator.mediaDevices as any).getDisplayMedia({ video: true, audio: true })
        const audioTracks = displayStream.getAudioTracks()
        if (!audioTracks || audioTracks.length === 0) {
          displayStream.getTracks().forEach((t: MediaStreamTrack) => t.stop())
          alert('音声が取得できませんでした。共有ダイアログで「タブの音声を共有」を有効にしてください。')
          return
        }
        displayStreamRef.current = displayStream
        if (captureMode === 'tabmix') {
          // 追加でマイクも取得し、AudioContextで合成
          console.log('マイク権限を確認中（タブ＋マイク）...')
          const micStream = await navigator.mediaDevices.getUserMedia({
            audio: {
              echoCancellation: true,
              noiseSuppression: true,
              autoGainControl: true
            }
          })
          micStreamRef.current = micStream
          const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
          audioContextRef.current = audioContext
          const destination = audioContext.createMediaStreamDestination()
          const tabSource = audioContext.createMediaStreamSource(displayStream)
          const micSource = audioContext.createMediaStreamSource(micStream)
          tabSource.connect(destination)
          micSource.connect(destination)
          mediaStream = destination.stream
          console.log('タブ＋マイクの合成ストリームを作成')
        } else {
          mediaStream = new MediaStream(audioTracks)
          console.log('タブ音声取得成功')
        }
      } else {
        // マイクの権限を事前チェック
        console.log('マイク権限を確認中...')
        mediaStream = await navigator.mediaDevices.getUserMedia({ 
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true
          } 
        })
        console.log('マイク権限取得成功')
      }
      stream.current = mediaStream
      
      // MediaRecorderを初期化（タブ系は96kbpsでサイズ抑制）
      const recorderOptions: MediaRecorderOptions =
        (captureMode === 'tab' || captureMode === 'tabmix')
          ? { mimeType: 'audio/webm;codecs=opus', audioBitsPerSecond: 96000 }
          : { mimeType: 'audio/webm;codecs=opus' }
      const recorder = new MediaRecorder(mediaStream, recorderOptions)
      
      // データが利用可能になったときのイベントハンドラーを設定
      recorder.ondataavailable = async (event) => {
        if (event.data.size > 0) {
          console.log('音声データ受信:', event.data.size, 'bytes')
          // すべてのモードで到着都度アップロード（Whisperの25MB制限対策）
          await handleChunkUpload(event.data)
        }
      }

      // 停止時の処理（データはondataavailableで都度アップロード済み）
      recorder.onstop = async () => {
        try {
          // no-op
        } catch (e) {
          console.error('最終アップロードエラー:', e)
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
        console.log('フロントエンドユーザー情報全体:', user)
        console.log('フロントエンドプレミアム状態:', user?.is_premium, '型:', typeof user?.is_premium, '判定結果:', isPremium, '最大時間:', maxDuration)
        setMaxDuration(maxDuration)
        setRecordingTime(0)
        
        // 録音開始を少し遅らせて、meetingIdが確実に設定されるようにする
        setTimeout(() => {
          if (captureMode === 'mic') {
            recorder.start(600000) // 10分ごとにデータを取得
            // 10分ごとのチャンク化
            const interval = setInterval(() => {
              if (recorder.state === 'recording') {
                setChunkNumber(prev => prev + 1)
              }
            }, 600000)
            setChunkInterval(interval)
          } else {
            // タブ/タブ＋マイクも10分ごとに分割アップロード（25MB制限回避）
            audioChunks.current = []
            recorder.start(600000)
            const interval = setInterval(() => {
              if (recorder.state === 'recording') {
                setChunkNumber(prev => prev + 1)
              }
            }, 600000)
            setChunkInterval(interval)
          }
          setIsRecording(true)
          setChunkNumber(0)
          
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
      
      // エラーの種類に応じて適切なメッセージを表示
      if (error instanceof Error) {
        if (error.name === 'NotAllowedError') {
          alert('マイクの権限が拒否されました。ブラウザの設定でマイクを許可してください。')
        } else if (error.name === 'NotFoundError') {
          alert('マイクが見つかりません。マイクが接続されているか確認してください。')
        } else if (error.name === 'NotSupportedError') {
          alert('このブラウザは録音機能をサポートしていません。')
        } else {
          alert(`録音を開始できませんでした: ${error.message}`)
        }
      } else {
        alert('録音を開始できませんでした。マイクの権限を確認してください。')
      }
    }
  }

  const stopRecordingHandler = async () => {
    try {
      if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop()
      }

      // タブ系は停止時の一括アップロード完了を待つ
      if (captureMode === 'tab' || captureMode === 'tabmix') {
        await new Promise((r) => setTimeout(r, 50))
        if (finalUploadPromiseRef.current) {
          try { await finalUploadPromiseRef.current } catch {}
          finalUploadPromiseRef.current = null
        }
      }
      
      if (stream.current) {
        stream.current.getTracks().forEach(track => track.stop())
      }
      if (displayStreamRef.current) {
        displayStreamRef.current.getTracks().forEach(track => track.stop())
        displayStreamRef.current = null
      }
      if (micStreamRef.current) {
        micStreamRef.current.getTracks().forEach(track => track.stop())
        micStreamRef.current = null
      }
      if (audioContextRef.current) {
        try { audioContextRef.current.close() } catch {}
        audioContextRef.current = null
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
      
      // ユーザー情報を更新
      try {
        const response = await authService.getCurrentUser()
        if (response.success && response.data?.user) {
          updateUser(response.data.user)
          console.log('ユーザー情報更新完了:', response.data.user)
        }
      } catch (error) {
        console.error('ユーザー情報更新エラー:', error)
      }
      
      // 履歴ページに遷移
      navigate('/history')
      
    } catch (error) {
      console.error('録音停止エラー:', error)
      alert('録音の停止中にエラーが発生しました。')
    }
  }

  // 停止時の一括アップロードは廃止（ondataavailableで逐次アップロード）

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
              
              <div className="input-group">
                <label>入力ソース</label>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  <button
                    type="button"
                    className={`start-recording-btn ${captureMode === 'mic' ? 'active' : ''}`}
                    onClick={() => setCaptureMode('mic')}
                  >
                    🎙️ マイク
                  </button>
                  <button
                    type="button"
                    className={`start-recording-btn ${captureMode === 'tab' ? 'active' : ''}`}
                    onClick={() => {
                      if (String(user?.is_premium) !== 'true') {
                        const go = confirm('タブ音声録音はプレミアム限定機能です。プラン画面に移動しますか？')
                        if (go) navigate('/billing')
                        return
                      }
                      setCaptureMode('tab')
                    }}
                    title={String(user?.is_premium) === 'true' ? 'ブラウザのタブ音声を録音（Chrome推奨）' : 'プレミアム限定'}
                  >
                    🧩 タブ音声（プレミアム）
                  </button>
                  <button
                    type="button"
                    className={`start-recording-btn ${captureMode === 'tabmix' ? 'active' : ''}`}
                    onClick={() => {
                      if (String(user?.is_premium) !== 'true') {
                        const go = confirm('タブ＋マイク同時録音はプレミアム限定機能です。プラン画面に移動しますか？')
                        if (go) navigate('/billing')
                        return
                      }
                      setCaptureMode('tabmix')
                    }}
                    title={String(user?.is_premium) === 'true' ? 'タブ音声とマイクを同時に録音（Chrome推奨）' : 'プレミアム限定'}
                  >
                    🎚️ タブ＋マイク（プレミアム）
                  </button>
                </div>
                {captureMode === 'tab' && (
                  <p style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
                    Chromeでのご利用を推奨します。共有ダイアログで録りたいタブを選び、「タブの音声を共有」を有効にしてください。
                  </p>
                )}
                {captureMode === 'tabmix' && (
                  <p style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
                    タブの共有ダイアログで「タブの音声を共有」を有効にし、マイク権限も許可してください（エコーキャンセリング有効）。
                  </p>
                )}
              </div>
              
              <div className="recording-info">
                <div className="info-card">
                  <div className="info-icon">⏱️</div>
                  <div className="info-content">
                    <h3>録音時間</h3>
                    <p>{user?.is_premium === "true" ? '最大2時間' : '最大30分'}</p>
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
                    <p>{user?.is_premium === "true" ? '履歴ページで確認・ダウンロード' : '履歴ページで確認'}</p>
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