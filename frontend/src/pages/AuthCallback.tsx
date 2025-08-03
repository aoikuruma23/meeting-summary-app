import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services/authService';
import './AuthCallback.css';

const AuthCallback: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        console.log('DEBUG: 認証コールバック開始');
        console.log('DEBUG: 現在のURL:', window.location.href);
        console.log('DEBUG: URL hash:', window.location.hash);
        
        // URLパラメータからトークンを取得
        const params = new URLSearchParams(location.hash.substring(1));
        const idToken = params.get('id_token');
        const accessToken = params.get('access_token');
        const error = params.get('error');
        const errorDescription = params.get('error_description');

        console.log('DEBUG: パラメータ解析結果:', {
          idToken: idToken ? `${idToken.substring(0, 20)}...` : null,
          accessToken: accessToken ? `${accessToken.substring(0, 20)}...` : null,
          error,
          errorDescription
        });

        if (error) {
          console.error('DEBUG: Google OAuthエラー:', error, errorDescription);
          setError(`認証に失敗しました: ${errorDescription || error}`);
          setIsLoading(false);
          return;
        }

        // IDトークンまたはアクセストークンのいずれかを使用
        const token = idToken || accessToken;
        
        if (!token) {
          console.error('DEBUG: トークンが見つかりません');
          setError('認証トークンが見つかりません。再度ログインしてください。');
          setIsLoading(false);
          return;
        }

        console.log('DEBUG: Google認証APIを呼び出し');
        
        // Google認証APIを呼び出し
        const response = await authService.googleAuth(token);
        
        console.log('DEBUG: 認証APIレスポンス:', response);
        
        if (response.success) {
          await login(response.data.access_token, response.data.user);
          navigate('/');
        } else {
          setError('認証に失敗しました。再度ログインしてください。');
        }
      } catch (err: any) {
        console.error('DEBUG: 認証コールバックエラー:', err);
        console.error('DEBUG: エラー詳細:', {
          message: err.message,
          response: err.response?.data,
          status: err.response?.status
        });
        setError(err.message || '認証に失敗しました。再度ログインしてください。');
      } finally {
        setIsLoading(false);
      }
    };

    handleAuthCallback();
  }, [location, login, navigate]);

  if (isLoading) {
    return (
      <div className="auth-callback-container">
        <div className="auth-callback-card">
          <div className="loading-spinner"></div>
          <h2>認証中...</h2>
          <p>Googleアカウントでログインしています</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="auth-callback-container">
        <div className="auth-callback-card">
          <div className="error-icon">❌</div>
          <h2>認証エラー</h2>
          <p>{error}</p>
          <button 
            onClick={() => navigate('/login')}
            className="back-to-login-button"
          >
            ログインページに戻る
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-callback-container">
      <div className="auth-callback-card">
        <div className="success-icon">✅</div>
        <h2>認証成功</h2>
        <p>ログインに成功しました。リダイレクト中...</p>
      </div>
    </div>
  );
};

export default AuthCallback; 