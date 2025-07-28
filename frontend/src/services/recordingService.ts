import axios from 'axios'

const API_BASE_URL = '/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export interface RecordingStartResponse {
  success: boolean
  message: string
  data: {
    meeting: {
      id: number
      title: string
      status: string
      drive_file_url: string | null
      created_at: string
      whisper_tokens: number | null
      gpt_tokens: number | null
    }
  }
}

export interface ChunkUploadResponse {
  success: boolean
  message: string
  data: {
    chunk_id: number
    filename: string
    status: string
    meeting_id: number
  }
}

export interface RecordingEndResponse {
  success: boolean
  message: string
  data: {
    meeting_id: number
    status: string
  }
}

export interface RecordingStatus {
  success: boolean
  message: string
  data: {
    meeting: {
      id: number
      title: string
      status: string
      drive_file_url: string | null
      created_at: string
      whisper_tokens: number | null
      gpt_tokens: number | null
    }
  }
}

class RecordingService {
  async startRecording(title: string): Promise<RecordingStartResponse> {
    const response = await apiClient.post('/recording/start', { 
      title
    })
    return response.data
  }

  async uploadChunk(meetingId: number, chunkNumber: number, audioFile: File): Promise<ChunkUploadResponse> {
    console.log('recordingService.uploadChunk開始 - meetingId:', meetingId, 'chunkNumber:', chunkNumber)
    
    const formData = new FormData()
    formData.append('audio_file', audioFile)
    formData.append('meeting_id', meetingId.toString())
    formData.append('chunk_number', chunkNumber.toString())
    
    console.log('FormData作成完了 - ファイルサイズ:', audioFile.size)

    const response = await apiClient.post('/recording/chunk', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    console.log('APIリクエスト完了 - ステータス:', response.status)
    return response.data
  }

  async endRecording(meetingId: number): Promise<RecordingEndResponse> {
    const response = await apiClient.post('/recording/end', { meeting_id: meetingId })
    return response.data
  }

  async getRecordingStatus(meetingId: number): Promise<RecordingStatus> {
    const response = await apiClient.get(`/recording/status/${meetingId}`)
    return response.data
  }

  async getRecordingList(): Promise<any> {
    const response = await apiClient.get('/recording/list')
    return response.data
  }

  async getSummary(meetingId: number): Promise<any> {
    const response = await apiClient.get(`/recording/summary/${meetingId}`)
    return response.data
  }

  async exportSummary(meetingId: number, format: 'pdf' | 'docx'): Promise<any> {
    const response = await apiClient.post('/recording/export', {
      meeting_id: meetingId,
      format: format
    })
    return response.data
  }

  async downloadExport(filename: string): Promise<Blob> {
    const response = await apiClient.get(`/recording/download-export/${filename}`, {
      responseType: 'blob'
    })
    return response.data
  }
}

export const recordingService = new RecordingService() 