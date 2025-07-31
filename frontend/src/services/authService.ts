import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL}/api` : 'https://meeting-summary-app-backend.onrender.com/api'

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
  is_premium: boolean
  usage_count: number
  trial_start_date: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

class AuthService {
  async googleAuth(token: string): Promise<AuthResponse> {
    const response = await apiClient.post('/auth/google', { token })
    return response.data
  }

  async lineAuth(code: string): Promise<AuthResponse> {
    const response = await apiClient.post('/auth/line', { code })
    return response.data
  }

  async getCurrentUser(token: string): Promise<User> {
    const response = await apiClient.get('/auth/me', {
      headers: { Authorization: `Bearer ${token}` }
    })
    console.log('getCurrentUser response:', response.data)
    return response.data.data.user
  }

  async logout(): Promise<void> {
    localStorage.removeItem('token')
  }
}

export const authService = new AuthService() 