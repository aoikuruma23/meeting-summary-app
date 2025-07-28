import React, { createContext, useContext, useState, ReactNode } from 'react'
import { recordingService } from '../services/recordingService'

interface RecordingState {
  isRecording: boolean
  meetingId: number | null
  title: string
  chunks: number
  status: 'idle' | 'recording' | 'processing' | 'completed' | 'error'
  driveFileUrl: string | null
}

interface RecordingContextType {
  recordingState: RecordingState
  startRecording: (title: string, scheduledDuration?: number, participants?: string) => Promise<any>
  stopRecording: () => Promise<void>
  uploadChunk: (audioBlob: Blob, chunkNumber: number) => Promise<void>
  resetRecording: () => void
}

const RecordingContext = createContext<RecordingContextType | undefined>(undefined)

export const useRecording = () => {
  const context = useContext(RecordingContext)
  if (context === undefined) {
    throw new Error('useRecording must be used within a RecordingProvider')
  }
  return context
}

interface RecordingProviderProps {
  children: ReactNode
}

export const RecordingProvider: React.FC<RecordingProviderProps> = ({ children }) => {
  const [recordingState, setRecordingState] = useState<RecordingState>({
    isRecording: false,
    meetingId: null,
    title: '',
    chunks: 0,
    status: 'idle',
    driveFileUrl: null
  })

  const startRecording = async (title: string) => {
    try {
      // API呼び出しで録音開始
      const response = await recordingService.startRecording(title)
      
      const newMeetingId = response.data.meeting.id
      setRecordingState(prev => ({
        ...prev,
        isRecording: true,
        title,
        status: 'recording',
        meetingId: newMeetingId
      }))
      
      console.log('録音開始:', title)
      console.log('meetingId設定:', newMeetingId)
      console.log('recordingState更新後:', { isRecording: true, meetingId: newMeetingId })
      
      return response
    } catch (error) {
      console.error('録音開始エラー:', error)
      setRecordingState(prev => ({
        ...prev,
        status: 'error'
      }))
      throw error
    }
  }

  const stopRecording = async () => {
    try {
      setRecordingState(prev => ({
        ...prev,
        isRecording: false,
        status: 'processing'
      }))
      
      // API呼び出しで録音終了
      if (recordingState.meetingId) {
        await recordingService.endRecording(recordingState.meetingId)
      }
      console.log('録音終了')
    } catch (error) {
      console.error('録音終了エラー:', error)
      setRecordingState(prev => ({
        ...prev,
        status: 'error'
      }))
    }
  }

  const uploadChunk = async (audioBlob: Blob, chunkNumber: number) => {
    try {
      console.log('uploadChunk開始 - meetingId:', recordingState.meetingId, 'chunkNumber:', chunkNumber)
      
      // チャンクアップロードの実装
      if (recordingState.meetingId) {
        const file = new File([audioBlob], `chunk_${chunkNumber}.webm`, { type: 'audio/webm' })
        console.log('ファイル作成完了 - サイズ:', file.size, 'bytes')
        
        const response = await recordingService.uploadChunk(recordingState.meetingId, chunkNumber, file)
        console.log('APIレスポンス:', response)
      } else {
        console.error('meetingIdが設定されていません')
      }
      
      console.log('チャンクアップロード:', chunkNumber)
      
      setRecordingState(prev => ({
        ...prev,
        chunks: prev.chunks + 1
      }))
    } catch (error: any) {
      console.error('チャンクアップロードエラー:', error)
      console.error('エラー詳細:', error.response?.data || error.message)
    }
  }

  const resetRecording = () => {
    setRecordingState({
      isRecording: false,
      meetingId: null,
      title: '',
      chunks: 0,
      status: 'idle',
      driveFileUrl: null
    })
  }

  const value: RecordingContextType = {
    recordingState,
    startRecording,
    stopRecording,
    uploadChunk,
    resetRecording
  }

  return (
    <RecordingContext.Provider value={value}>
      {children}
    </RecordingContext.Provider>
  )
} 