import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import { DisclaimerBanner } from './components/DisclaimerBanner'
import { Navbar } from './components/Navbar'
import { Footer } from './components/Footer'

// Pages
import { Home } from './pages/Home'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { Dashboard } from './pages/Dashboard'
import { Trade } from './pages/Trade'
import { Market } from './pages/Market'
import { Profile } from './pages/Profile'
import { Deposit } from './pages/Deposit'
import { LearningHub } from './pages/LearningHub'

// Protected Route Wrapper
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin-slow">
          <div className="w-12 h-12 border-4 border-dark-700 border-t-primary-500 rounded-full"></div>
        </div>
      </div>
    )
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />
}

function AppContent() {
  const { isAuthenticated } = useAuth()

  return (
    <div className="min-h-screen bg-dark-950 flex flex-col">
      <DisclaimerBanner />
      <Navbar />
      <main className="flex-1">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Home />} />
          <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />} />
          <Route path="/register" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Register />} />
          <Route path="/learning" element={<LearningHub />} />

          {/* Protected Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/trade"
            element={
              <ProtectedRoute>
                <Trade />
              </ProtectedRoute>
            }
          />
          <Route
            path="/market"
            element={
              <ProtectedRoute>
                <Market />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />
          <Route
            path="/deposit"
            element={
              <ProtectedRoute>
                <Deposit />
              </ProtectedRoute>
            }
          />

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  )
}

export default App
