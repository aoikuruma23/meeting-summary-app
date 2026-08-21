import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useRecording } from '../contexts/RecordingContext'
import { authService } from '../services/authService'
import { recordingService } from '../services/recordingService'
import './Recording.css'

// チャンク分割間隔（ミリ秒）。本番は10分固定。
// 検証時のみ ?chunkSec=60 のようなクエリで短縮できる（分割の挙動を短時間で確認するため）
const DEFAULT_CHUNK_INTERVAL_MS = 600000

const getChunkIntervalMs = (): number => {
  const fromQuery = new URLSearchParams(window.location.search).get('chunkSec')

  // ?chunkSec=0 で通常設定に戻す
  if (fromQuery === '0') {
    window.localStorage.removeItem('chunkSec')
    return DEFAULT_CHUNK_INTERVAL_MS
  }

  // クエリは画面遷移で失われるため、一度指定されたら保持する
  const raw = fromQuery ?? window.localStorage.getItem('chunkSec')
  const sec = raw ? parseInt(raw, 10) : NaN

  // 下限を60秒にしてチャンクの過剰分割（＝アップロード回数の増大）を防ぐ
  if (!Number.isNaN(sec) && sec >= 60 && sec <= 3600) {
    if (fromQuery) {
      window.localStorage.setItem('chunkSec', String(sec))
    }
    return sec * 1000
  }

  return DEFAULT_CHUNK_INTERVAL_MS
}

// タブ音声のキャプチャは Chromium 系のみ対応。
// Firefox は getDisplayMedia を持つが音声トラックを返さず、Safari も画面共有の音声取得に非対応。
// API の有無だけで判定すると、これらのブラウザが「対応」として通ってしまう
const isTabAudioSupported = (): boolean => {
  if (!navigator.mediaDevices || !(navigator.mediaDevices as any).getDisplayMedia) {
    return false
  }
  const ua = navigator.userAgent
  const isFirefox = /Firefox\//.test(ua)
  const isSafari = /Safari\//.test(ua) && !/Chrome|Chromium|Edg|OPR/.test(ua)
  return !isFirefox && !isSafari
}

// 画面を消しても録音を続けるための keep-alive 音源。
// ブラウザは「音を再生しているページ」を凍結対象から外すが、完全な無音（全ゼロ）は
// 音量メーターの閾値（おおよそ -72dBFS）を下回り「再生していない」と判定される。
// そのため、人間には聞こえないが閾値は超える極小振幅（-66dBFS 相当）の正弦波を使う。
// この音量は静かな室内の暗騒音より低く、録音内容に影響しない
const createKeepAliveAudioUrl = (): string => {
  const sampleRate = 8000
  const frames = sampleRate // 1秒ぶんをループ再生する
  const buffer = new ArrayBuffer(44 + frames * 2)
  const view = new DataView(buffer)

  const writeString = (offset: number, text: string) => {
    for (let i = 0; i < text.length; i++) {
      view.setUint8(offset + i, text.charCodeAt(i))
    }
  }

  // WAVヘッダ（16bit PCM モノラル）
  writeString(0, 'RIFF')
  view.setUint32(4, 36 + frames * 2, true)
  writeString(8, 'WAVE')
  writeString(12, 'fmt ')
  view.setUint32(16, 16, true)
  view.setUint16(20, 1, true)
  view.setUint16(22, 1, true)
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, sampleRate * 2, true)
  view.setUint16(32, 2, true)
  view.setUint16(34, 16, true)
  writeString(36, 'data')
  view.setUint32(40, frames * 2, true)

  // 100Hz・振幅16/32768（≒ -66dBFS）。ループの継ぎ目で不連続にならない周波数を選ぶ
  for (let i = 0; i < frames; i++) {
    view.setInt16(44 + i * 2, Math.round(Math.sin((2 * Math.PI * 100 * i) / sampleRate) * 16), true)
  }

  return URL.createObjectURL(new Blob([buffer], { type: 'audio/wav' }))
}

const Recording: React.FC = () => {
  const { user, updateUser } = useAuth()
  const { recordingState: _, startRecording, stopRecording, uploadChunk: __, resetRecording } = useRecording()
  const navigate = useNavigate()
  
  const [title, setTitle] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [chunkInterval, setChunkInterval] = useState<NodeJS.Timeout | null>(null)
  const [chunkNumber, setChunkNumber] = useState(0)
  const [currentMeetingId, setCurrentMeetingId] = useState<number | null>(null)
  const currentMeetingIdRef = useRef<number | null>(null)
  const [captureMode, setCaptureMode] = useState<'mic' | 'tab' | 'tabmix'>('mic')
  const [chunkIntervalSec, setChunkIntervalSec] = useState(DEFAULT_CHUNK_INTERVAL_MS / 1000)
  // 端末側で録音が止まっていることを利用者に伝えるための警告
  const [captureWarning, setCaptureWarning] = useState<string | null>(null)
  // 実際に音声が録れていた秒数（録音時間と乖離したら端末側で中断されている）
  const [capturedSec, setCapturedSec] = useState(0)
  
  // 録音時間関連
  const [recordingTime, setRecordingTime] = useState(0)
  const [maxDuration, setMaxDuration] = useState<number | null>(null)
  const [timeInterval, setTimeInterval] = useState<NodeJS.Timeout | null>(null)
  
  const audioChunks = useRef<Blob[]>([])
  const stream = useRef<MediaStream | null>(null)
  const displayStreamRef = useRef<MediaStream | null>(null)
  const micStreamRef = useRef<MediaStream | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  // 録音中に差し替わるため ref で保持する（state では最新の recorder を掴めない）
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const recorderOptionsRef = useRef<MediaRecorderOptions>({})
  const chunkIndexRef = useRef(0)
  const lastRotateAtRef = useRef(0)
  // 停止時に完了を待つため、進行中のアップロードを保持する
  const pendingUploadsRef = useRef<Promise<void>[]>([])
  // 「録音していたつもりの時間」と「実際に音声が録れていた時間」を突き合わせるための計測値
  const recordingStartedAtRef = useRef(0)
  const capturedMsRef = useRef(0)
  const lastTickAtRef = useRef(0)
  const uploadFailuresRef = useRef(0)
  // 端末側で作られたチャンクの総数（サーバ受信数と突き合わせて欠損を検知する）
  const producedChunksRef = useRef(0)
  // 送信に失敗した音声を捨てずに保持し、停止時に送り直す。
  // 画面ロック中は通信が制限されることがあり、その場では何度再送しても通らない
  const failedChunksRef = useRef<{ index: number; file: File }[]>([])
  // 画面が消えていた累計時間。Android は画面消灯中にマイク取得を止めるため、
  // これが長いほど録音が欠けている
  const hiddenMsRef = useRef(0)
  const hiddenSinceRef = useRef(0)
  // 実際に MediaRecorder から出てきた音声の総バイト数。
  // マイクが止まっていてもタイマーは動くため、時間の計測だけでは欠損を検知できない
  const capturedBytesRef = useRef(0)
  const isStoppingRef = useRef(false)
  // 画面消灯によるページ凍結を防ぐための Screen Wake Lock
  const wakeLockRef = useRef<any>(null)
  // 電源ボタンで画面を消された場合の保険。WakeLock は手動ロックでは効かない
  const keepAliveAudioRef = useRef<HTMLAudioElement | null>(null)
  const keepAliveUrlRef = useRef<string | null>(null)
  // タイマーIDは ref でも保持する。state だけだと、録音開始時に作った
  // クロージャが掴む stopRecordingHandler はタイマー登録前のレンダーのもの（＝null）で、
  // 自動停止時に clearInterval が空振りしてタイマーが動き続ける
  const chunkIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const timeIntervalRef = useRef<NodeJS.Timeout | null>(null)

  const clearTimers = () => {
    if (chunkIntervalRef.current) {
      clearInterval(chunkIntervalRef.current)
      chunkIntervalRef.current = null
    }
    if (timeIntervalRef.current) {
      clearInterval(timeIntervalRef.current)
      timeIntervalRef.current = null
    }
  }

  useEffect(() => {
    if (!user) {
      navigate('/login')
    }
  }, [user, navigate])

  // 検証用の分割間隔設定を画面に反映する
  useEffect(() => {
    setChunkIntervalSec(getChunkIntervalMs() / 1000)
  }, [])

  // スマホの画面が消えるとブラウザがページを凍結し、分割タイマーもマイク取得も止まる。
  // Screen Wake Lock で画面を保持することでこれを防ぐ（Android Chrome で有効）
  const requestWakeLock = async () => {
    try {
      if (!('wakeLock' in navigator)) {
        console.log('WakeLock 非対応のブラウザです')
        return
      }
      wakeLockRef.current = await (navigator as any).wakeLock.request('screen')
      console.log('WakeLock を取得しました')
    } catch (error) {
      console.warn('WakeLock の取得に失敗:', error)
    }
  }

  const releaseWakeLock = async () => {
    try {
      await wakeLockRef.current?.release()
    } catch {}
    wakeLockRef.current = null
  }

  // WakeLock は「自動で画面が消えるのを防ぐ」だけで、電源ボタンによる手動ロックでは解除される。
  // その場合の保険として、極小音量のループ再生と MediaSession でページを
  // 「メディア再生中」の状態に保ち、ブラウザ/OS に凍結させない
  const startKeepAlive = async () => {
    try {
      if (keepAliveAudioRef.current) return

      const url = createKeepAliveAudioUrl()
      keepAliveUrlRef.current = url

      const audio = new Audio(url)
      audio.loop = true
      // volume を 0 にすると「音を出していない」と判定されるため下げすぎない
      audio.volume = 1
      // OS 側から一時停止されても録音中は鳴らし直す
      audio.onpause = () => {
        if (keepAliveAudioRef.current === audio) {
          audio.play().catch(() => {})
        }
      }

      await audio.play()
      keepAliveAudioRef.current = audio
      console.log('keep-alive 音声の再生を開始しました')

      if ('mediaSession' in navigator) {
        navigator.mediaSession.metadata = new MediaMetadata({
          title: '録音中',
          artist: '会議要約アプリ'
        })
        navigator.mediaSession.playbackState = 'playing'
        // 通知の再生/停止ボタンで録音が止まらないようにする
        navigator.mediaSession.setActionHandler('pause', () => {})
        navigator.mediaSession.setActionHandler('play', () => {})
      }
    } catch (error) {
      console.warn('keep-alive 音声の再生に失敗:', error)
    }
  }

  const stopKeepAlive = () => {
    // 先に ref を外す。onpause が再生し直してしまうため
    const audio = keepAliveAudioRef.current
    keepAliveAudioRef.current = null
    try {
      audio?.pause()
    } catch {}

    if (keepAliveUrlRef.current) {
      URL.revokeObjectURL(keepAliveUrlRef.current)
      keepAliveUrlRef.current = null
    }

    if ('mediaSession' in navigator) {
      navigator.mediaSession.playbackState = 'none'
    }
  }

  // WakeLock はタブが非表示になると OS 側で解除されるため、表示に戻るたびに取り直す
  useEffect(() => {
    if (!isRecording) return

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        if (hiddenSinceRef.current) {
          const hiddenMs = Date.now() - hiddenSinceRef.current
          hiddenMsRef.current += hiddenMs
          hiddenSinceRef.current = 0
          if (hiddenMs > 10000) {
            setCaptureWarning('画面が消えていた間、録音が止まっていた可能性があります。録音中は画面を点けたままにしてください。')
          }
        }
        requestWakeLock()
        startKeepAlive()
      } else {
        // 画面消灯・他アプリへの切り替え。この間はマイク取得が止まる恐れがある
        hiddenSinceRef.current = Date.now()
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange)
  }, [isRecording])

  // 録音画面から離れたときに画面ロックとタイマーを残さない
  useEffect(() => {
    return () => {
      releaseWakeLock()
      stopKeepAlive()
      clearTimers()
    }
  }, [])

  // チャンクごとに MediaRecorder を作り直す。
  // timeslice による分割は2個目以降のBlobにwebmヘッダが付かず、Whisperが
  // 「Invalid file format」で拒否するため、各チャンクを独立した完全なwebmにする。
  const createRecorder = (source: MediaStream, chunkIndex: number): MediaRecorder => {
    const recorder = new MediaRecorder(source, recorderOptionsRef.current)

    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        capturedBytesRef.current += event.data.size
        console.log(`音声データ受信 - chunk ${chunkIndex}:`, event.data.size, 'bytes')
        pendingUploadsRef.current.push(handleChunkUpload(event.data, chunkIndex))
      }
    }

    return recorder
  }

  // 現在の recorder を止めて次の recorder に切り替える（stopで1チャンク確定）
  const rotateRecorder = () => {
    const current = mediaRecorderRef.current
    if (!current || current.state !== 'recording' || !stream.current) {
      // ここに来る＝端末側で録音が止まっている。無言で捨てると原因が追えない
      console.warn('分割をスキップしました - recorder.state:', current?.state, ' stream:', !!stream.current)
      setCaptureWarning('端末側で録音が中断されています。画面を点けたまま、この画面を前面に置いてください。')
      return
    }

    current.stop()
    chunkIndexRef.current += 1
    lastRotateAtRef.current = Date.now()

    const next = createRecorder(stream.current, chunkIndexRef.current)
    next.start()
    mediaRecorderRef.current = next
    setChunkNumber(chunkIndexRef.current)
    console.log('チャンクを切り替えました - 次の番号:', chunkIndexRef.current)
  }

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
        if (!isTabAudioSupported()) {
          alert('タブ音声録音は Chrome または Edge でのみご利用いただけます。\n\nFirefox / Safari は画面共有時の音声取得に対応していないため、共有ダイアログに「タブの音声も共有する」の項目自体が表示されません。')
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
      
      // MediaRecorderのオプション（タブ系は96kbpsでサイズ抑制）
      recorderOptionsRef.current =
        (captureMode === 'tab' || captureMode === 'tabmix')
          ? { mimeType: 'audio/webm;codecs=opus', audioBitsPerSecond: 96000 }
          : { mimeType: 'audio/webm;codecs=opus' }

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
        const chunkIntervalMs = getChunkIntervalMs()
        console.log('チャンク分割間隔:', chunkIntervalMs / 1000, '秒')

        setTimeout(() => {
          // マイク/タブ系ともに一定間隔で分割アップロード（Whisperの25MB制限回避）
          audioChunks.current = []
          chunkIndexRef.current = 0
          pendingUploadsRef.current = []

          // timeslice は渡さない。stop() のたびに完全なwebmが1つ確定する
          const firstRecorder = createRecorder(mediaStream, 0)
          firstRecorder.start()
          mediaRecorderRef.current = firstRecorder
          const startedAt = Date.now()
          lastRotateAtRef.current = startedAt
          recordingStartedAtRef.current = startedAt
          lastTickAtRef.current = startedAt
          capturedMsRef.current = 0
          uploadFailuresRef.current = 0
          producedChunksRef.current = 0
          failedChunksRef.current = []
          hiddenMsRef.current = 0
          hiddenSinceRef.current = 0
          capturedBytesRef.current = 0
          isStoppingRef.current = false
          setCapturedSec(0)
          setCaptureWarning(null)
          requestWakeLock()
          startKeepAlive()

          // 1秒ごとに経過時間で判定する。
          // 録音中はアプリのタブが非アクティブになるためタイマーが間引かれる。
          // setInterval(rotate, 間隔) だと発火自体が飛ばされて分割されない
          const interval = setInterval(() => {
            const now = Date.now()

            // 実際に音声が録れていた時間を積み上げる。
            // ページが凍結されると tick 自体が飛ぶため、1回で加算できる上限を tick間隔の2倍に制限する。
            // こうすると「凍結されていた時間」は加算されず、後から欠損を検知できる
            const sinceLastTick = now - lastTickAtRef.current
            lastTickAtRef.current = now
            const recorderActive = mediaRecorderRef.current?.state === 'recording'
            const trackLive = stream.current
              ? stream.current.getAudioTracks().some(t => t.readyState === 'live' && !t.muted)
              : false
            if (recorderActive && trackLive) {
              capturedMsRef.current += Math.min(sinceLastTick, 2000)
            }
            if (sinceLastTick > 5000) {
              console.warn('タイマーが', Math.round(sinceLastTick / 1000), '秒間停止していました（バックグラウンド凍結の可能性）')
              setCaptureWarning('画面が消えている間、録音が中断された可能性があります。画面を点けたままにしてください。')
            }

            const elapsed = now - lastRotateAtRef.current
            if (elapsed >= chunkIntervalMs) {
              console.log('分割タイミング到達:', Math.round(elapsed / 1000), '秒経過')
              rotateRecorder()
            }
          }, 1000)
          setChunkInterval(interval)
          chunkIntervalRef.current = interval
          setIsRecording(true)
          setChunkNumber(0)
          
          // 経過時間は Date.now() から算出する。
          // prev+1 方式はバックグラウンドで tick が間引かれた分だけ実時間から遅れ、
          // 表示がずれるうえに録音時間制限の自動停止も効かなくなる
          const timeInterval = setInterval(() => {
            const elapsedSec = Math.floor((Date.now() - recordingStartedAtRef.current) / 1000)
            setRecordingTime(elapsedSec)
            setCapturedSec(Math.floor(capturedMsRef.current / 1000))

            // 制限時間に達した場合、録音を自動停止（多重呼び出しを防ぐ）
            if (maxDuration && elapsedSec >= maxDuration * 60 && !isStoppingRef.current) {
              isStoppingRef.current = true
              stopRecordingHandler()
            }
          }, 1000) // 1秒ごと
          
          setTimeInterval(timeInterval)
          timeIntervalRef.current = timeInterval
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

  // 欠損の警告文で使う。1分未満は秒で出さないと「約0分」になって意味が伝わらない
  const formatDurationJa = (ms: number) => {
    return ms < 60000 ? `${Math.round(ms / 1000)}秒` : `${Math.round(ms / 60000)}分`
  }

  const stopRecordingHandler = async () => {
    try {
      isStoppingRef.current = true

      // 停止処理中にチャンクが切り替わらないよう、先にタイマーを止める
      clearTimers()

      // 経過時間はここで確定させる。この後のアップロード完了待ち（数十秒になり得る）を
      // 含めてしまうと「取得できた音声」との比較がずれ、正常な録音でも警告が出る
      const elapsedMs = recordingStartedAtRef.current ? Date.now() - recordingStartedAtRef.current : 0
      if (chunkInterval) {
        clearInterval(chunkInterval)
      }
      setChunkInterval(null)

      // 最後のチャンクを確定させる。onstop は ondataavailable の後に発火する
      const recorder = mediaRecorderRef.current
      if (recorder && recorder.state === 'recording') {
        await new Promise<void>((resolve) => {
          const finish = () => resolve()
          recorder.onstop = finish
          // onstop が来ない環境でも停止処理を進めるための保険
          setTimeout(finish, 3000)
          recorder.stop()
        })
      }

      // 全チャンクのアップロード完了を待ってから /end を投げる。
      // 待たずに投げると、サーバ側がチャンク未着のまま要約処理を始めてしまう
      if (pendingUploadsRef.current.length > 0) {
        console.log('アップロード完了を待機中:', pendingUploadsRef.current.length, '件')
        await Promise.allSettled(pendingUploadsRef.current)
        pendingUploadsRef.current = []
        console.log('アップロード完了')
      }

      // 録音中に送れなかった音声を、画面が点いて通信が戻ったこの時点で送り直す。
      // 画面ロック中はOS側で通信が制限されることがあり、その場での再送は通らない
      if (failedChunksRef.current.length > 0 && currentMeetingIdRef.current) {
        const queued = failedChunksRef.current
        failedChunksRef.current = []
        console.log('未送信チャンクの再送を開始:', queued.length, '件')
        setCaptureWarning(`送信できていない音声を再送しています…（${queued.length}件）`)

        for (const item of queued) {
          try {
            await recordingService.uploadChunk(currentMeetingIdRef.current, item.index, item.file)
            uploadFailuresRef.current = Math.max(0, uploadFailuresRef.current - 1)
            console.log('再送成功 - chunk', item.index)
          } catch (error) {
            console.error('再送に失敗 - chunk', item.index, error)
          }
        }
        setCaptureWarning(null)
      }

      mediaRecorderRef.current = null

      // 実際に録れた音声が録音時間より大幅に短い場合、端末側で録音が中断されている。
      // 黙って「完了」にすると、欠けた議事録を正しいものとして渡してしまう
      const capturedMs = capturedMsRef.current
      const capturedBytes = capturedBytesRef.current
      const failures = uploadFailuresRef.current

      // 画面が消えたまま停止された場合に備えて、最後の非表示時間も足す
      if (hiddenSinceRef.current) {
        hiddenMsRef.current += Date.now() - hiddenSinceRef.current
        hiddenSinceRef.current = 0
      }
      const hiddenMs = hiddenMsRef.current

      // バイト数から実際の音声の長さを見積もる。マイクが止まっていても
      // タイマーは動き続けるため、時間の計測だけでは欠損を検知できない。
      // 実測ではマイク録音が毎秒およそ14.5KB、静かな会話でもこの数分の1には収まる
      const BYTES_PER_SEC = 14500
      const estimatedAudioMs = (capturedBytes / BYTES_PER_SEC) * 1000

      console.log(
        '録音時間:', Math.round(elapsedMs / 1000), '秒',
        '/ 音声データ:', Math.round(capturedBytes / 1024), 'KB (推定', Math.round(estimatedAudioMs / 1000), '秒)',
        '/ 画面消灯:', Math.round(hiddenMs / 1000), '秒',
        '/ 送信失敗:', failures, '件'
      )

      // 3つのどれかに引っかかれば録音は欠けている。
      // 時間の計測(凍結の検知)・バイト数(マイク停止の検知)・画面消灯時間(原因の特定)
      const timerStalled = capturedMs < elapsedMs * 0.8
      const tooLittleAudio = estimatedAudioMs < elapsedMs * 0.5
      const longHidden = hiddenMs > elapsedMs * 0.2

      if (elapsedMs > 60000 && (timerStalled || tooLittleAudio || longHidden)) {
        const message = [
          '⚠️ 録音が途中で止まっていた可能性があります。',
          '',
          `録音時間: 約${formatDurationJa(elapsedMs)}`,
          `取得できた音声: 約${formatDurationJa(estimatedAudioMs)}ぶん`
        ]
        if (hiddenMs > 10000) {
          message.push(`画面が消えていた時間: 約${formatDurationJa(hiddenMs)}`)
        }
        message.push(
          '',
          'スマートフォンの画面を消すと、Android がマイクの取得を止めてしまいます。',
          '録音中は画面を点けたまま、この画面を前面に置いたままにしてください。'
        )
        alert(message.join('\n'))
      } else if (failures > 0) {
        alert(
          [
            `⚠️ 音声の送信に${failures}件失敗しました。`,
            '通信状況の良い場所で録音し直すことをおすすめします。'
          ].join('\n')
        )
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
      
      if (timeInterval) {
        clearInterval(timeInterval)
      }
      setTimeInterval(null)
      
      setIsRecording(false)
      releaseWakeLock()
      stopKeepAlive()
      
      // 録音終了APIを呼び出し
      if (currentMeetingId) {
        await stopRecording(producedChunksRef.current)
      }
      
      // 状態をリセット
      setRecordingTime(0)
      setMaxDuration(null)
      setCurrentMeetingId(null)
      currentMeetingIdRef.current = null
      setChunkNumber(0)
      recordingStartedAtRef.current = 0
      capturedMsRef.current = 0
      uploadFailuresRef.current = 0
      producedChunksRef.current = 0
      failedChunksRef.current = []
      hiddenMsRef.current = 0
      hiddenSinceRef.current = 0
      capturedBytesRef.current = 0
      setCapturedSec(0)
      
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
      isStoppingRef.current = false
      releaseWakeLock()
      stopKeepAlive()
      alert('録音の停止中にエラーが発生しました。')
    }
  }

  // 停止時の一括アップロードは廃止（ondataavailableで逐次アップロード）

  // chunkIndex は呼び出し元から受け取る。state を参照すると
  // ondataavailable のクロージャが初期値(0)を掴み、全チャンクが同じ番号になる
  // 再送しても無駄なエラー（リクエスト内容そのものが不正）かどうか。
  // 認証切れ・サイズ超過・時間制限などは何度送っても同じ結果になる
  const isPermanentUploadError = (error: any): boolean => {
    const status = error?.response?.status
    return typeof status === 'number' && status >= 400 && status < 500
  }

  const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

  // 1回の失敗で10分ぶんの音声を失わないよう再送する。
  // サーバの再起動や一時的な電波の途切れは数十秒で復帰するため、
  // 段階的に間隔を空けながら合計1分ほど粘る
  const UPLOAD_RETRY_DELAYS_MS = [3000, 8000, 20000, 30000]
  // 保持する未送信チャンクの上限。10分間隔なので12個＝プレミアムの最大録音時間ぶん
  const MAX_RETAINED_CHUNKS = 12

  const handleChunkUpload = async (audioBlob: Blob, chunkIndex: number) => {
    if (!currentMeetingIdRef.current) {
      console.log('meetingIdが設定されていません')
      return
    }

    producedChunksRef.current += 1

    console.log('handleChunkUpload開始 - meetingId:', currentMeetingIdRef.current, 'chunkNumber:', chunkIndex)
    console.log('音声データサイズ:', audioBlob.size, 'bytes')

    const file = new File([audioBlob], `chunk_${chunkIndex}.webm`, { type: 'audio/webm' })

    for (let attempt = 0; attempt <= UPLOAD_RETRY_DELAYS_MS.length; attempt++) {
      try {
        await recordingService.uploadChunk(currentMeetingIdRef.current, chunkIndex, file)
        console.log('チャンクアップロード成功 - chunk', chunkIndex, attempt > 0 ? `(${attempt}回目の再送)` : '')
        if (attempt > 0) {
          setCaptureWarning(null)
        }
        return
      } catch (error: any) {
        console.error(`チャンクアップロードエラー - chunk ${chunkIndex} (試行${attempt + 1}回目):`, error)
        console.error('エラー詳細:', error.response?.data || error.message)

        if (isPermanentUploadError(error)) {
          console.error('再送しても解決しないエラーのため中止します')
          break
        }
        if (attempt >= UPLOAD_RETRY_DELAYS_MS.length) {
          break
        }

        setCaptureWarning('音声の送信に失敗しました。再送しています…')
        await sleep(UPLOAD_RETRY_DELAYS_MS[attempt])
      }
    }

    // 音声そのものは捨てない。画面が点いて通信が戻る停止時に送り直す
    uploadFailuresRef.current += 1
    if (failedChunksRef.current.length < MAX_RETAINED_CHUNKS) {
      failedChunksRef.current.push({ index: chunkIndex, file })
    } else {
      console.warn('保持上限を超えたため破棄します - chunk', chunkIndex)
    }
    setCaptureWarning('音声の送信に失敗した区間があります。停止時に送り直します。')
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
                {(captureMode === 'tab' || captureMode === 'tabmix') && !isTabAudioSupported() && (
                  <p style={{ marginTop: 8, fontSize: 12, color: '#c0392b', fontWeight: 600 }}>
                    ⚠️ ご利用中のブラウザはタブ音声録音に対応していません。Chrome または Edge で開き直してください。
                  </p>
                )}
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
                {chunkIntervalSec !== DEFAULT_CHUNK_INTERVAL_MS / 1000 && (
                  <p style={{ marginTop: 8, fontSize: 12, color: '#b26a00', fontWeight: 600 }}>
                    🧪 検証モード: {chunkIntervalSec}秒ごとに分割します（解除は ?chunkSec=0）
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
            {captureWarning && (
              <div style={{ background: '#fdecea', border: '1px solid #e74c3c', color: '#a93226', borderRadius: 8, padding: '12px 14px', marginBottom: 16, fontSize: 14, fontWeight: 600, lineHeight: 1.6 }}>
                ⚠️ {captureWarning}
              </div>
            )}
            <div style={{ background: '#fff8e1', border: '1px solid #f0c419', color: '#7d6608', borderRadius: 8, padding: '10px 14px', marginBottom: 16, fontSize: 13, lineHeight: 1.6 }}>
              📱 録音中は<strong>画面を消さず</strong>、この画面を前面に置いたままにしてください。画面が消えるとブラウザが録音を止めることがあります。
            </div>
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
                  <span className="info-label">取得できた音声:</span>
                  <span className="info-value" style={{ color: recordingTime > 60 && capturedSec < recordingTime * 0.8 ? '#c0392b' : undefined }}>
                    {formatTime(capturedSec)}
                  </span>
                </div>
                {chunkIntervalSec !== DEFAULT_CHUNK_INTERVAL_MS / 1000 && (
                  <div className="info-item">
                    <span className="info-label">分割間隔:</span>
                    <span className="info-value">{chunkIntervalSec}秒（検証モード）</span>
                  </div>
                )}
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