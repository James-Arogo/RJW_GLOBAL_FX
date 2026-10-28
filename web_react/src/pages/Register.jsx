import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AlertCircle, UserPlus, Check, X } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { authAPI } from '../utils/api'

export const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [passwordChecks, setPasswordChecks] = useState({
    length: false,
    uppercase: false,
    number: false,
    special: false,
  })
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleChange = (e) => {
    const { name, value } = e.target
    setError('')
    setFormData((prev) => ({ ...prev, [name]: value }))

    if (name === 'password') {
      setPasswordChecks({
        length: value.length >= 8,
        uppercase: /[A-Z]/.test(value),
        number: /\d/.test(value),
        special: /[!@#$%^&*]/.test(value),
      })
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (!Object.values(passwordChecks).every(Boolean)) {
      setError('Password does not meet requirements')
      return
    }

    setLoading(true)

    try {
      const payload = {
        username: formData.username.trim(),
        email: formData.email.trim().toLowerCase(),
        password: formData.password,
      }
      const { data } = await authAPI.register({
        username: payload.username,
        email: payload.email,
        password: payload.password,
      })
      sessionStorage.setItem('lastAuthIdentifier', payload.username)
      login(data.user, data.access_token)
      navigate('/dashboard')
    } catch (err) {
      const detail = err.response?.data?.detail
      if (detail === 'Username already registered' || detail === 'Email already registered') {
        sessionStorage.setItem('lastAuthIdentifier', formData.username.trim() || formData.email.trim().toLowerCase())
        setError(`${detail}. Try logging in instead, or choose a different ${detail.includes('Username') ? 'username' : 'email'}.`)
      } else {
        setError(detail || 'Registration failed')
      }
    } finally {
      setLoading(false)
    }
  }

  const allChecksPassed = Object.values(passwordChecks).every(Boolean)

  return (
    <div className="min-h-screen flex items-center justify-center p-4 pt-20">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="flex justify-center mb-4">
            <div className="w-14 h-14 bg-primary-500/10 rounded-full flex items-center justify-center">
              <UserPlus className="w-7 h-7 text-primary-400" />
            </div>
          </div>
          <h1 className="text-3xl font-display font-bold text-dark-100 mb-2">Get Started</h1>
          <p className="text-dark-400 text-sm">Create your trading account</p>
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
            <label className="block text-dark-300 text-sm font-medium mb-2">Username</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Choose a username"
              className="input-field"
              required
            />
          </div>

          <div>
            <label className="block text-dark-300 text-sm font-medium mb-2">Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="student@university.ac.ke"
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
              placeholder="Create a strong password"
              className="input-field"
              required
            />
            
            {/* Password Requirements */}
            <div className="mt-3 space-y-2">
              <div className="flex items-center gap-2 text-xs">
                {passwordChecks.length ? (
                  <Check className="w-4 h-4 text-success-400" />
                ) : (
                  <X className="w-4 h-4 text-dark-500" />
                )}
                <span className={passwordChecks.length ? 'text-dark-300' : 'text-dark-500'}>
                  At least 8 characters
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                {passwordChecks.uppercase ? (
                  <Check className="w-4 h-4 text-success-400" />
                ) : (
                  <X className="w-4 h-4 text-dark-500" />
                )}
                <span className={passwordChecks.uppercase ? 'text-dark-300' : 'text-dark-500'}>
                  One uppercase letter
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                {passwordChecks.number ? (
                  <Check className="w-4 h-4 text-success-400" />
                ) : (
                  <X className="w-4 h-4 text-dark-500" />
                )}
                <span className={passwordChecks.number ? 'text-dark-300' : 'text-dark-500'}>
                  One number
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                {passwordChecks.special ? (
                  <Check className="w-4 h-4 text-success-400" />
                ) : (
                  <X className="w-4 h-4 text-dark-500" />
                )}
                <span className={passwordChecks.special ? 'text-dark-300' : 'text-dark-500'}>
                  One special character (!@#$%^&*)
                </span>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-dark-300 text-sm font-medium mb-2">Confirm Password</label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="Confirm your password"
              className="input-field"
              required
            />
          </div>

          <button type="submit" disabled={loading || !allChecksPassed} className="btn-primary w-full">
            {loading ? 'Creating account...' : 'Sign Up'}
          </button>
        </form>

        {/* Login Link */}
        <p className="text-center text-dark-400 text-sm mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-primary-400 hover:text-primary-300 font-medium">
            Login
          </Link>
        </p>
        {error.includes('already registered') && (
          <p className="text-center text-dark-500 text-xs mt-3">
            Tip: go to Login and use the same username or email you signed up with.
          </p>
        )}
      </div>
    </div>
  )
}
