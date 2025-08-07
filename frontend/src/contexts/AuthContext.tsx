import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authService } from '../services/authService'

interface User {
  id: number
  email: string
  name: string
  profile_picture?: string
  is_premium: string
  is_active?: string
  usage_count?: number
  trial_start_date?: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  isNewUser: boolean
  login: (token: string, userData: User, isNewUser?: boolean) => Promise<void>
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
  const [isNewUser, setIsNewUser] = useState(false)
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
            // 既存ユーザーは新規ユーザーではない
            setIsNewUser(false)
          } else {
            // トークンが無効な場合は削除
            localStorage.removeItem('access_token')
            setToken(null)
            setUser(null)
            setIsNewUser(false)
          }
        } catch (error) {
          console.error('認証エラー:', error)
          // トークンが無効な場合は削除
          localStorage.removeItem('access_token')
          setToken(null)
          setUser(null)
          setIsNewUser(false)
        }
      }
      setIsLoading(false)
    }

    initializeAuth()
  }, [])

  const login = async (newToken: string, userData: User, isNewUserFlag: boolean = false) => {
    console.log('DEBUG: ログイン処理開始 - トークン:', newToken ? newToken.substring(0, 20) + '...' : 'undefined')
    console.log('DEBUG: ユーザーデータ:', userData)
    console.log('DEBUG: 新規ユーザーフラグ:', isNewUserFlag)
    
    if (!newToken) {
      console.error('DEBUG: トークンがundefinedです')
      throw new Error('このメールアドレスでは登録できません。別のメールアドレスをお試しください。')
    }
    
    setToken(newToken)
    localStorage.setItem('access_token', newToken)
    setUser(userData)
    setIsNewUser(isNewUserFlag)
    
    console.log('DEBUG: ログイン処理完了')
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    setIsNewUser(false)
    localStorage.removeItem('access_token')
    authService.logout()
  }

  const value: AuthContextType = {
    user,
    token,
    isNewUser,
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