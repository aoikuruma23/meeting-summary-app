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

// ServiceWorkerを無効化
// if ('serviceWorker' in navigator) {
//   window.addEventListener('load', () => {
//     navigator.serviceWorker.register('/sw.js')
//   })
// } 