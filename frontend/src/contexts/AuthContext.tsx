import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authService } from '../services/authService'

interface User {
  id: number
  email: string
  name: string
  profile_picture?: string
  is_premium: string
  usage_count?: number
  trial_start_date?: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (token: string, userData: User) => Promise<void>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem('access_token')
      if (storedToken) {
        setToken(storedToken)
        try {
          const response = await authService.getCurrentUser()
          if (response.success && response.data?.user) {
            setUser(response.data.user)
          } else {
            // トークンが無効な場合は削除
            localStorage.removeItem('access_token')
            setToken(null)
            setUser(null)
          }
        } catch (error) {
          console.error('認証エラー:', error)
          // トークンが無効な場合は削除
          localStorage.removeItem('access_token')
          setToken(null)
          setUser(null)
        }
      }
      setIsLoading(false)
    }

    initializeAuth()
  }, [])

  const login = async (newToken: string, userData: User) => {
    console.log('DEBUG: ログイン処理開始 - トークン:', newToken.substring(0, 20) + '...')
    console.log('DEBUG: ユーザーデータ:', userData)
    
    setToken(newToken)
    localStorage.setItem('access_token', newToken)
    setUser(userData)
    
    console.log('DEBUG: ログイン処理完了')
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('access_token')
    authService.logout()
  }

  const value: AuthContextType = {
    user,
    token,
    login,
    logout,
    isLoading
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
} 