import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL}/api` : 'http://localhost:8000/api'

// axiosのインスタンスを作成
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// リクエストインターセプターでトークンを自動追加
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export interface User {
  id: number
  email: string
  name: string
  is_premium: string  // booleanからstringに変更
  usage_count: number
  trial_start_date: string
}

export interface AuthResponse {
  success: boolean
  message: string
  data?: {
    access_token: string
    token_type: string
    user: User
  }
}

class AuthService {
  async googleAuth(token: string): Promise<AuthResponse> {
    try {
      console.log('DEBUG: Google認証API呼び出し開始');
      console.log('DEBUG: トークン長さ:', token.length);
      
      const response = await apiClient.post('/auth/google', { token })
      console.log('DEBUG: Google認証APIレスポンス成功:', response.data);
      return response.data
    } catch (error: any) {
      console.error('DEBUG: Google認証APIエラー:', error);
      console.error('DEBUG: エラー詳細:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      });
      
      if (error.response?.status === 503) {
        throw new Error('Google OAuth設定が完了していません。ダミーログインをご利用ください。')
      }
      if (error.response?.status === 401) {
        throw new Error('Google認証に失敗しました。再度ログインしてください。')
      }
      throw new Error('Google認証中にエラーが発生しました。')
    }
  }

  async lineAuth(code: string): Promise<AuthResponse> {
    try {
      const response = await apiClient.post('/auth/line', { code })
      return response.data
    } catch (error: any) {
      if (error.response?.status === 503) {
        throw new Error('LINE OAuth設定が完了していません。ダミーログインをご利用ください。')
      }
      if (error.response?.status === 401) {
        throw new Error('LINE認証に失敗しました。再度ログインしてください。')
      }
      throw new Error('LINE認証中にエラーが発生しました。')
    }
  }

  async getCurrentUser(token: string): Promise<User> {
    try {
      const response = await apiClient.get('/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      })
      console.log('getCurrentUser response:', response.data)
      return response.data.data.user
    } catch (error: any) {
      if (error.response?.status === 401) {
        throw new Error('認証トークンが無効です。再度ログインしてください。')
      }
      throw new Error('ユーザー情報の取得に失敗しました。')
    }
  }

  async logout(): Promise<void> {
    localStorage.removeItem('token')
  }
}

export const authService = new AuthService() 