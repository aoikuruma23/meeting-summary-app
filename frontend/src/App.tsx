import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { RecordingProvider } from './contexts/RecordingContext'
import Header from './components/Header'
import Footer from './components/Footer'
import Home from './pages/Home'
import Recording from './pages/Recording'
import History from './pages/History'
import Settings from './pages/Settings'
import Billing from './pages/Billing'
import Login from './pages/Login'
import Help from './pages/Help'
import AuthCallback from './pages/AuthCallback'
import EmailVerification from './pages/EmailVerification'
import PrivacyPolicy from './pages/PrivacyPolicy'
import TermsOfService from './pages/TermsOfService'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <RecordingProvider>
          <div className="App">
            <Header />
            <main className="main-content">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/recording" element={<Recording />} />
                <Route path="/history" element={<History />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/billing" element={<Billing />} />
                <Route path="/login" element={<Login />} />
                <Route path="/help" element={<Help />} />
                <Route path="/auth/callback" element={<AuthCallback />} />
                <Route path="/email-verification" element={<EmailVerification />} />
                <Route path="/privacy" element={<PrivacyPolicy />} />
                <Route path="/terms" element={<TermsOfService />} />
              </Routes>
            </main>
            <Footer />
          </div>
        </RecordingProvider>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App