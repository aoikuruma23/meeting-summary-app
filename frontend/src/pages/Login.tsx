import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Login.css';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const endpoint = isRegistering ? '/auth/register' : '/auth/login';
      const body = isRegistering 
        ? { email, password, name }
        : { email, password };

      const response = await fetch(`${import.meta.env.VITE_API_URL || 'https://meeting-summary-app-backend.onrender.com'}/api${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (response.ok) {
        await login(data.data.access_token);
        navigate('/');
      } else {
        setError(data.detail || 'ログインに失敗しました');
      }
    } catch (err) {
      setError('ネットワークエラーが発生しました');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setIsLoading(true);
    setError('');

    try {
      // Google OAuth設定が完了していない場合の処理
      if (!import.meta.env.VITE_GOOGLE_CLIENT_ID) {
        setError('Googleログインは現在準備中です。ダミーログインをご利用ください。');
        setIsLoading(false);
        return;
      }

      // Google OAuth2.0の実装
      const googleAuthUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${import.meta.env.VITE_GOOGLE_CLIENT_ID}&redirect_uri=${window.location.origin}/auth/callback&response_type=token&scope=email profile`;
      window.location.href = googleAuthUrl;
    } catch (err) {
      setError('Googleログインに失敗しました');
      setIsLoading(false);
    }
  };

  const handleLineLogin = async () => {
    setIsLoading(true);
    setError('');

    try {
      // LINE OAuth設定が完了していない場合の処理
      if (!import.meta.env.VITE_LINE_CHANNEL_ID) {
        setError('LINEログインは現在準備中です。ダミーログインをご利用ください。');
        setIsLoading(false);
        return;
      }

      // LINE OAuth2.0の実装
      const lineAuthUrl = `https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id=${import.meta.env.VITE_LINE_CHANNEL_ID}&redirect_uri=${window.location.origin}/auth/callback&state=line&scope=profile openid email`;
      window.location.href = lineAuthUrl;
    } catch (err) {
      setError('LINEログインに失敗しました');
      setIsLoading(false);
    }
  };

  const handleDummyLogin = async () => {
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'https://meeting-summary-app-backend.onrender.com'}/api/auth/dummy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (response.ok) {
        await login(data.data.access_token);
        navigate('/');
      } else {
        setError(data.detail || 'ダミーログインに失敗しました');
      }
    } catch (err) {
      setError('ネットワークエラーが発生しました');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>{isRegistering ? 'アカウント作成' : 'ログイン'}</h1>
        
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit} className="login-form">
          {isRegistering && (
            <div className="form-group">
              <label htmlFor="name">お名前</label>
              <input
                type="text"
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                placeholder="お名前を入力"
              />
            </div>
          )}
          
          <div className="form-group">
            <label htmlFor="email">メールアドレス</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="example@email.com"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">パスワード</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="パスワードを入力"
            />
          </div>
          
          <button 
            type="submit" 
            className="login-button"
            disabled={isLoading}
          >
            {isLoading ? '処理中...' : (isRegistering ? 'アカウント作成' : 'ログイン')}
          </button>
        </form>
        
        <div className="social-login">
          <h3>ソーシャルログイン</h3>
          
          <button 
            onClick={handleGoogleLogin}
            className="google-login-button"
            disabled={isLoading}
          >
            🔍 Googleでログイン
          </button>
          
          <button 
            onClick={handleLineLogin}
            className="line-login-button"
            disabled={isLoading}
          >
            💬 LINEでログイン
          </button>
          
          <button 
            onClick={handleDummyLogin}
            className="dummy-login-button"
            disabled={isLoading}
          >
            🧪 テストログイン
          </button>
        </div>
        
        <div className="login-footer">
          <button 
            onClick={() => setIsRegistering(!isRegistering)}
            className="toggle-button"
          >
            {isRegistering ? '既にアカウントをお持ちですか？' : 'アカウントをお持ちでないですか？'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login; 