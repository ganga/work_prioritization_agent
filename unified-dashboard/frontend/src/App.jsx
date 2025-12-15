import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { authService } from './services/auth'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Settings from './pages/Settings'
import Navbar from './components/Navbar'

function PrivateRoute({ children }) {
  return authService.isAuthenticated() ? children : <Navigate to="/login" />
}

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Navbar />
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <PrivateRoute>
                <Navbar />
                <Settings />
              </PrivateRoute>
            }
          />
        </Routes>
      </div>
    </Router>
  )
}

export default App
