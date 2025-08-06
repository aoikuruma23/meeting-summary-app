import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
console.log('DEBUG: API_BASE_URL:', `${API_BASE_URL}/api`)
console.log('DEBUG: VITE_API_URL:', import.meta.env.VITE_API_URL)

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// リクエストインターセプターでトークンを追加
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export interface AuthResponse {
  success: boolean
  message: string
  data?: {
    access_token: string
    token_type: string
    is_new_user?: boolean
    user: {
      id: number
      email: string
      name: string
      profile_picture?: string
      is_premium: string
    }
  }
}

export interface EmailLoginRequest {
  email: string
  password: string
}

export interface EmailRegisterRequest {
  email: string
  password: string
  name: string
}

const authService = {
  async googleAuth(idToken: string): Promise<AuthResponse> {
    try {
      console.log('DEBUG: Google認証API呼び出し開始')
      console.log('DEBUG: トークン長さ:', idToken.length)
      console.log('DEBUG: API URL:', `${API_BASE_URL}/api/auth/google`)
      
      const response = await apiClient.post('/auth/google', { id_token: idToken })
      console.log('DEBUG: Google認証APIレスポンス成功:', response.data)
      console.log('DEBUG: レスポンスステータス:', response.status)
      console.log('DEBUG: レスポンスヘッダー:', response.headers)
      
      if (!response.data || Object.keys(response.data).length === 0) {
        console.error('DEBUG: レスポンスデータが空です')
        throw new Error('バックエンドからのレスポンスが空です')
      }
      
      return response.data
    } catch (error: any) {
      console.error('DEBUG: Google認証APIエラー:', error)
      console.error('DEBUG: エラー詳細:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
        url: error.config?.url,
        headers: error.response?.headers
      })
      
      if (error.response?.status === 503) {
        throw new Error('Google OAuth設定が完了していません。ダミーログインをご利用ください。')
      }
      if (error.response?.status === 401) {
        throw new Error('Google認証に失敗しました。再度ログインしてください。')
      }
      throw new Error('Google認証中にエラーが発生しました。')
    }
  },

  async lineAuth(code: string): Promise<AuthResponse> {
    try {
      console.log('DEBUG: LINE認証API呼び出し開始')
      console.log('DEBUG: コード長さ:', code.length)
      console.log('DEBUG: API URL:', `${API_BASE_URL}/api/auth/line`)
      
      const response = await apiClient.post('/auth/line', { code })
      console.log('DEBUG: LINE認証APIレスポンス成功:', response.data)
      console.log('DEBUG: レスポンスステータス:', response.status)
      console.log('DEBUG: レスポンスヘッダー:', response.headers)
      
      if (!response.data || Object.keys(response.data).length === 0) {
        console.error('DEBUG: レスポンスデータが空です')
        throw new Error('バックエンドからのレスポンスが空です')
      }
      
      return response.data
    } catch (error: any) {
      console.error('DEBUG: LINE認証APIエラー:', error)
      console.error('DEBUG: エラー詳細:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
        url: error.config?.url,
        headers: error.response?.headers
      })
      
      if (error.response?.status === 503) {
        throw new Error('LINE OAuth設定が完了していません。ダミーログインをご利用ください。')
      }
      if (error.response?.status === 401) {
        throw new Error('LINE認証に失敗しました。再度ログインしてください。')
      }
      throw new Error('LINE認証中にエラーが発生しました。')
    }
  },

  async emailLogin(request: EmailLoginRequest): Promise<AuthResponse> {
    try {
      console.log('DEBUG: メールログインAPI呼び出し開始')
      console.log('DEBUG: API URL:', `${API_BASE_URL}/api/auth/email/login`)
      
      const response = await apiClient.post('/auth/email/login', request)
      console.log('DEBUG: メールログインAPIレスポンス成功:', response.data)
      
      return response.data
    } catch (error: any) {
      console.error('DEBUG: メールログインAPIエラー:', error)
      
      if (error.response?.status === 401) {
        throw new Error('メールアドレスまたはパスワードが正しくありません')
      }
      throw new Error('ログインに失敗しました')
    }
  },

  async emailRegister(request: EmailRegisterRequest): Promise<AuthResponse> {
    try {
      console.log('DEBUG: メール登録API呼び出し開始')
      console.log('DEBUG: API URL:', `${API_BASE_URL}/api/auth/email/register`)
      
      const response = await apiClient.post('/auth/email/register', request)
      console.log('DEBUG: メール登録APIレスポンス成功:', response.data)
      
      return response.data
    } catch (error: any) {
      console.error('DEBUG: メール登録APIエラー:', error)
      
      if (error.response?.status === 400) {
        throw new Error('このメールアドレスは既に登録されています')
      }
      throw new Error('登録に失敗しました')
    }
  },

  async getCurrentUser(): Promise<AuthResponse> {
    try {
      const response = await apiClient.get('/auth/me')
      console.log('getCurrentUser response:', response.data)
      return response.data
    } catch (error: any) {
      console.error('getCurrentUser error:', error)
      throw new Error('ユーザー情報の取得に失敗しました')
    }
  },

  logout(): void {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  }
}

export { authService } 