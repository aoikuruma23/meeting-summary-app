import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://meeting-summary-app-backend.jibunkaikaku-lab.com'
console.log('DEBUG: API_BASE_URL:', `${API_BASE_URL}/api`)
console.log('DEBUG: VITE_API_URL:', import.meta.env.VITE_API_URL)

// 使用済みのLINE認証コードを記録
const usedLineCodes = new Set<string>()

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
  // CORSエラー対策
  withCredentials: false,
  timeout: 30000,
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
    access_token?: string
    token_type?: string
    is_new_user?: boolean
    user: {
      id: number
      email: string
      name: string
      profile_picture?: string
      is_premium: string
      is_active?: string
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

export interface EmailVerifyRequest {
  email: string
  verification_code: string
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
      console.log('DEBUG: コード内容（最初の10文字）:', code.substring(0, 10))
      console.log('DEBUG: API URL:', `${API_BASE_URL}/api/auth/line`)
      
      // 既に使用済みのコードかチェック
      if (usedLineCodes.has(code)) {
        console.error('DEBUG: 既に使用済みのLINE認証コードです:', code)
        throw new Error('このLINE認証コードは既に使用済みです。再度LINEログインを実行してください。')
      }
      
      const requestData = { code }
      console.log('DEBUG: リクエストデータ:', requestData)
      
      const response = await apiClient.post('/auth/line', requestData)
      console.log('DEBUG: LINE認証APIレスポンス成功:', response.data)
      console.log('DEBUG: レスポンスステータス:', response.status)
      console.log('DEBUG: レスポンスヘッダー:', response.headers)
      
      // 成功したらコードを使用済みとして記録
      usedLineCodes.add(code)
      
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
      
      // 400エラーの詳細情報を表示
      if (error.response?.status === 400) {
        const errorDetail = error.response?.data?.detail || 'リクエストが無効です'
        console.error('DEBUG: 400エラーの詳細:', errorDetail)
        console.error('DEBUG: 400エラーの完全なレスポンス:', error.response?.data)
        
        // invalid authorization code の場合は特別なメッセージ
        if (errorDetail.includes('invalid authorization code')) {
          throw new Error('LINE認証コードが無効です。再度LINEログインを実行してください。')
        }
        
        throw new Error(`LINE認証エラー: ${errorDetail}`)
      }
      
      // ネットワークエラーの場合
      if (error.message === 'Network Error') {
        throw new Error('ネットワークエラーが発生しました。バックエンドの接続を確認してください。')
      }
      
      // CORSエラーの場合
      if (error.code === 'ERR_NETWORK') {
        throw new Error('CORSエラーが発生しました。バックエンドの設定を確認してください。')
      }
      
      if (error.response?.status === 500) {
        const errorDetail = error.response?.data?.detail || 'サーバー内部エラーが発生しました'
        throw new Error(`LINE認証エラー: ${errorDetail}`)
      }
      
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
        // バックエンドからのエラーメッセージを表示
        const errorMessage = error.response?.data?.detail || '登録に失敗しました'
        throw new Error(errorMessage)
      }
      throw new Error('登録に失敗しました')
    }
  },

  async emailVerify(request: EmailVerifyRequest): Promise<AuthResponse> {
    try {
      console.log('DEBUG: メール認証API呼び出し開始')
      console.log('DEBUG: API URL:', `${API_BASE_URL}/api/auth/email/verify`)
      
      const response = await apiClient.post('/auth/email/verify', request)
      console.log('DEBUG: メール認証APIレスポンス成功:', response.data)
      
      return response.data
    } catch (error: any) {
      console.error('DEBUG: メール認証APIエラー:', error)
      
      if (error.response?.status === 400) {
        const errorMessage = error.response?.data?.detail || '認証に失敗しました'
        throw new Error(errorMessage)
      }
      throw new Error('認証に失敗しました')
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