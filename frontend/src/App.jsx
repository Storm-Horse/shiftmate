import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import HomePage from './pages/HomePage'
import ShiftsPage from './pages/ShiftsPage'
import SettingsPage from './pages/SettingsPage'
import Navbar from './components/Navbar'

function ProtectedLayout() {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  return (
    <div className="flex flex-col h-full max-w-lg mx-auto">
      <div className="flex-1 overflow-y-auto pb-20">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/shifts" element={<ShiftsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
      <Navbar />
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/*" element={<ProtectedLayout />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
