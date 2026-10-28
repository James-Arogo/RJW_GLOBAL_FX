import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AlertCircle, LogIn } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { authAPI } from '../utils/api'

export const Login = () => {
  const [formData, setFormData] = useState(() => ({
    username: sessionStorage.getItem('lastAuthIdentifier') || '',
    password: '',
  }))
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleChange = (e) => {
    const { name, value } = e.target
    setError('')
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const payload = {
        username: formData.username.trim(),
        password: formData.password,
      }
      const { data } = await authAPI.login(payload)
      sessionStorage.setItem('lastAuthIdentifier', payload.username)
      login(data.user, data.access_token)
      navigate('/dashboard')
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(
        detail === 'Invalid username or password'
          ? 'We could not sign you in. Use your username or email and make sure the password matches the account you created.'
          : detail || 'Login failed. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 pt-20">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="flex justify-center mb-4">
            <div className="w-14 h-14 bg-primary-500/10 rounded-full flex items-center justify-center">
              <LogIn className="w-7 h-7 text-primary-400" />
            </div>
          </div>
          <h1 className="text-3xl font-display font-bold text-dark-100 mb-2">Welcome Back</h1>
          <p className="text-dark-400 text-sm">Login to your trading account</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="card space-y-4">
          {error && (
            <div className="flex gap-3 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
              <p className="text-sm text-red-300">{error}</p>
            </div>
          )}

          <div>
            <label className="block text-dark-300 text-sm font-medium mb-2">Username or Email</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Enter your username or email"
              className="input-field"
              required
            />
          </div>

          <div>
            <label className="block text-dark-300 text-sm font-medium mb-2">Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter your password"
              className="input-field"
              required
            />
          </div>

          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        {/* Signup Link */}
        <p className="text-center text-dark-400 text-sm mt-6">
          Don't have an account?{' '}
          <Link to="/register" className="text-primary-400 hover:text-primary-300 font-medium">
            Sign up
          </Link>
        </p>
        <p className="text-center text-dark-500 text-xs mt-3">
          If you already registered, use the same username or email you created the account with.
        </p>
      </div>
    </div>
  )
}
