import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './AuthCallback.css';

const AuthCallback: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const urlParams = new URLSearchParams(location.search);
        const hashParams = new URLSearchParams(location.hash.substring(1));
        
        // Google OAuthの場合（tokenがhashに含まれる）
        const token = hashParams.get('access_token');
        const state = urlParams.get('state');
        
        if (token) {
          // Google OAuth
          const response = await fetch(`${import.meta.env.VITE_API_URL || 'https://meeting-summary-app-backend.onrender.com'}/api/auth/google`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ token }),
          });

          const data = await response.json();

          if (response.ok) {
            await login(data.data.access_token, data.data.user);
            navigate('/');
          } else {
            setError(data.detail || 'Googleログインに失敗しました');
          }
        } else if (state === 'line') {
          // LINE OAuthの場合（codeがqueryに含まれる）
          const code = urlParams.get('code');
          
          if (code) {
            const response = await fetch(`${import.meta.env.VITE_API_URL || 'https://meeting-summary-app-backend.onrender.com'}/api/auth/line`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ code }),
            });

            const data = await response.json();

            if (response.ok) {
              await login(data.data.access_token, data.data.user);
              navigate('/');
            } else {
              setError(data.detail || 'LINEログインに失敗しました');
            }
          } else {
            setError('認証コードが見つかりません');
          }
        } else {
          setError('無効な認証リクエストです');
        }
      } catch (err) {
        setError('認証処理中にエラーが発生しました');
      } finally {
        setIsLoading(false);
      }
    };

    handleCallback();
  }, [location, login, navigate]);

  if (isLoading) {
    return (
      <div className="auth-callback-container">
        <div className="auth-callback-card">
          <div className="loading-spinner"></div>
          <h2>認証処理中...</h2>
          <p>しばらくお待ちください</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="auth-callback-container">
        <div className="auth-callback-card">
          <h2>認証エラー</h2>
          <p className="error-message">{error}</p>
          <button onClick={() => navigate('/login')} className="back-button">
            ログインページに戻る
          </button>
        </div>
      </div>
    );
  }

  return null;
};

export default AuthCallback; 