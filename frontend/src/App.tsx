import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import './App.css'

import Header from './components/Header'
import Footer from './components/Footer'

import Home from './pages/Home'
import Login from './pages/Login'
import Recording from './pages/Recording'
import History from './pages/History'
import Billing from './pages/Billing'
import Settings from './pages/Settings'
import Help from './pages/Help'
import PrivacyPolicy from './pages/PrivacyPolicy'
import TermsOfService from './pages/TermsOfService'
import AuthCallback from './pages/AuthCallback'
import EmailVerification from './pages/EmailVerification'

function ScrollToTop() {
  const { pathname, search } = useLocation()
  useEffect(() => {
    try {
      window.scrollTo({ top: 0, left: 0, behavior: 'auto' })
    } catch {
      window.scrollTo(0, 0)
    }
  }, [pathname, search])
  return null
}

function App() {
  return (
    <div className="App">
      <Header />
      <ScrollToTop />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/recording" element={<Recording />} />
          <Route path="/history" element={<History />} />
          <Route path="/billing" element={<Billing />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/help" element={<Help />} />
          <Route path="/privacy" element={<PrivacyPolicy />} />
          <Route path="/terms" element={<TermsOfService />} />
          <Route path="/auth/callback" element={<AuthCallback />} />
          <Route path="/email-verification" element={<EmailVerification />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}

export default App