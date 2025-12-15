import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authService } from '../services/auth'
import { MessageSquare, Mail, CheckSquare, Settings, LogOut } from 'lucide-react'

export default function Navbar() {
  const navigate = useNavigate()

  const handleLogout = () => {
    authService.logout()
    navigate('/login')
  }

  return (
    <nav style={styles.nav}>
      <div style={styles.container}>
        <div style={styles.logo}>
          <h2>Unified Dashboard</h2>
        </div>
        <div style={styles.links}>
          <Link to="/" style={styles.link}>
            <MessageSquare size={18} style={{ marginRight: '8px' }} />
            Dashboard
          </Link>
          <Link to="/settings" style={styles.link}>
            <Settings size={18} style={{ marginRight: '8px' }} />
            Settings
          </Link>
          <button onClick={handleLogout} style={styles.logoutButton}>
            <LogOut size={18} style={{ marginRight: '8px' }} />
            Logout
          </button>
        </div>
      </div>
    </nav>
  )
}

const styles = {
  nav: {
    backgroundColor: '#1a1a1a',
    color: 'white',
    padding: '1rem 0',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '0 2rem',
  },
  logo: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
  },
  links: {
    display: 'flex',
    gap: '1.5rem',
    alignItems: 'center',
  },
  link: {
    color: 'white',
    textDecoration: 'none',
    display: 'flex',
    alignItems: 'center',
    padding: '0.5rem 1rem',
    borderRadius: '4px',
    transition: 'background-color 0.2s',
  },
  linkHover: {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
  },
  logoutButton: {
    backgroundColor: '#dc3545',
    color: 'white',
    border: 'none',
    padding: '0.5rem 1rem',
    borderRadius: '4px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    transition: 'background-color 0.2s',
  },
}
