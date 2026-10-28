import React, { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

const normalizeUser = (user) => {
  if (!user) return null

  return {
    ...user,
    balance: user.balance ?? user.balance_kes ?? 0,
  }
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(true)

  // Load from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      setToken(storedToken)
      setUser(normalizeUser(JSON.parse(storedUser)))
    }

    setLoading(false)
  }, [])

  const login = (user, token) => {
    const normalizedUser = normalizeUser(user)
    setUser(normalizedUser)
    setToken(token)
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(normalizedUser))
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  const updateUser = (updatedUser) => {
    const normalizedUser = normalizeUser(updatedUser)
    setUser(normalizedUser)
    localStorage.setItem('user', JSON.stringify(normalizedUser))
  }

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!token,
    login,
    logout,
    updateUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
