import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.tsx'
import { AuthProvider } from './contexts/AuthContext.tsx'
import { RecordingProvider } from './contexts/RecordingContext.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <RecordingProvider>
          <App />
        </RecordingProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
)

// PWA: Service Worker 登録（本番時のみ）
if (import.meta.env.PROD && 'serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        // 新バージョン検知時: すぐに有効化を促し、制御交代でリロード
        const listenForWaiting = (reg: ServiceWorkerRegistration) => {
          if (reg.waiting) {
            try { reg.waiting.postMessage({ type: 'SKIP_WAITING' }) } catch {}
          }
        }

        listenForWaiting(registration)
        registration.addEventListener('updatefound', () => {
          const installing = registration.installing
          if (!installing) return
          installing.addEventListener('statechange', () => {
            if (installing.state === 'installed' && navigator.serviceWorker.controller) {
              try { installing.postMessage({ type: 'SKIP_WAITING' }) } catch {}
            }
          })
        })

        // 定期的に更新チェック（30分ごと）
        setInterval(() => {
          try { registration.update() } catch {}
        }, 30 * 60 * 1000)
      })
      .catch(() => {})

    // 新しいSWに制御が切り替わったら一度だけリロード
    let refreshing = false
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      if (refreshing) return
      refreshing = true
      window.location.reload()
    })
  })
}