import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authService } from '../services/authService'

interface User {
  id: number
  email: string
  name: string
  is_premium: string  // booleanからstringに変更
  usage_count: number
  trial_start_date: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (token: string, userData?: any) => Promise<void>
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
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const initializeAuth = async () => {
      if (token) {
        try {
          const userData = await authService.getCurrentUser(token)
          setUser(userData)
        } catch (error) {
          console.error('認証エラー:', error)
          // トークンが無効な場合は削除
          localStorage.removeItem('token')
          setToken(null)
          setUser(null)
        }
      }
      setIsLoading(false)
    }

    initializeAuth()
  }, [token])

  const login = async (newToken: string, userData?: any) => {
    setToken(newToken)
    localStorage.setItem('token', newToken)
    
    // ユーザー情報が提供された場合は設定
    if (userData) {
      setUser(userData)
    } else {
      // ユーザー情報が提供されていない場合は取得
      try {
        const userData = await authService.getCurrentUser(newToken)
        setUser(userData)
      } catch (error) {
        console.error('ユーザー情報取得エラー:', error)
      }
    }
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('token')
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