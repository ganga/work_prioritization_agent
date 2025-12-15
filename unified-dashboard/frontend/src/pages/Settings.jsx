import React, { useState } from 'react'
import { dashboardService } from '../services/dashboard'
import { MessageSquare, Mail, CheckSquare } from 'lucide-react'

export default function Settings() {
  const [slackToken, setSlackToken] = useState('')
  const [slackWorkspace, setSlackWorkspace] = useState('')
  const [gmailCredentials, setGmailCredentials] = useState('')
  const [jiraUrl, setJiraUrl] = useState('')
  const [jiraEmail, setJiraEmail] = useState('')
  const [jiraToken, setJiraToken] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const handleSlackSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    try {
      await dashboardService.setSlackCredentials(slackToken, slackWorkspace)
      setMessage('Slack credentials saved successfully!')
      setSlackToken('')
      setSlackWorkspace('')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save Slack credentials')
    }
  }

  const handleGmailSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    try {
      // In production, this would be done through OAuth flow
      // For now, user needs to paste credentials JSON
      await dashboardService.setGmailCredentials(gmailCredentials)
      setMessage('Gmail credentials saved successfully!')
      setGmailCredentials('')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save Gmail credentials')
    }
  }

  const handleJiraSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    try {
      await dashboardService.setJiraCredentials(jiraUrl, jiraEmail, jiraToken)
      setMessage('Jira credentials saved successfully!')
      setJiraUrl('')
      setJiraEmail('')
      setJiraToken('')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save Jira credentials')
    }
  }

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Integration Settings</h1>
      <p style={styles.subtitle}>
        Connect your Slack, Gmail, and Jira accounts to start syncing items
      </p>

      {message && <div style={styles.success}>{message}</div>}
      {error && <div style={styles.error}>{error}</div>}

      <div style={styles.sections}>
        {/* Slack Integration */}
        <div style={styles.section}>
          <div style={styles.sectionHeader}>
            <MessageSquare size={24} style={{ marginRight: '12px' }} />
            <h2>Slack Integration</h2>
          </div>
          <form onSubmit={handleSlackSubmit} style={styles.form}>
            <div style={styles.formGroup}>
              <label style={styles.label}>
                Slack Bot Token
                <span style={styles.helpText}>
                  (Get from{' '}
                  <a
                    href="https://api.slack.com/apps"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={styles.link}
                  >
                    api.slack.com/apps
                  </a>
                  )
                </span>
              </label>
              <input
                type="password"
                value={slackToken}
                onChange={(e) => setSlackToken(e.target.value)}
                placeholder="xoxb-your-slack-token"
                style={styles.input}
                required
              />
            </div>
            <div style={styles.formGroup}>
              <label style={styles.label}>Workspace Name (optional)</label>
              <input
                type="text"
                value={slackWorkspace}
                onChange={(e) => setSlackWorkspace(e.target.value)}
                placeholder="My Workspace"
                style={styles.input}
              />
            </div>
            <button type="submit" style={styles.button}>
              Save Slack Credentials
            </button>
          </form>
        </div>

        {/* Gmail Integration */}
        <div style={styles.section}>
          <div style={styles.sectionHeader}>
            <Mail size={24} style={{ marginRight: '12px' }} />
            <h2>Gmail Integration</h2>
          </div>
          <form onSubmit={handleGmailSubmit} style={styles.form}>
            <div style={styles.formGroup}>
              <label style={styles.label}>
                OAuth Credentials JSON
                <span style={styles.helpText}>
                  (Get from{' '}
                  <a
                    href="https://console.cloud.google.com/apis/credentials"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={styles.link}
                  >
                    Google Cloud Console
                  </a>
                  )
                </span>
              </label>
              <textarea
                value={gmailCredentials}
                onChange={(e) => setGmailCredentials(e.target.value)}
                placeholder='{"client_id":"...","client_secret":"...","refresh_token":"..."}'
                style={styles.textarea}
                rows={6}
                required
              />
            </div>
            <button type="submit" style={styles.button}>
              Save Gmail Credentials
            </button>
          </form>
        </div>

        {/* Jira Integration */}
        <div style={styles.section}>
          <div style={styles.sectionHeader}>
            <CheckSquare size={24} style={{ marginRight: '12px' }} />
            <h2>Jira Integration</h2>
          </div>
          <form onSubmit={handleJiraSubmit} style={styles.form}>
            <div style={styles.formGroup}>
              <label style={styles.label}>Jira URL</label>
              <input
                type="url"
                value={jiraUrl}
                onChange={(e) => setJiraUrl(e.target.value)}
                placeholder="https://yourcompany.atlassian.net"
                style={styles.input}
                required
              />
            </div>
            <div style={styles.formGroup}>
              <label style={styles.label}>Email</label>
              <input
                type="email"
                value={jiraEmail}
                onChange={(e) => setJiraEmail(e.target.value)}
                placeholder="your@email.com"
                style={styles.input}
                required
              />
            </div>
            <div style={styles.formGroup}>
              <label style={styles.label}>
                API Token
                <span style={styles.helpText}>
                  (Get from{' '}
                  <a
                    href="https://id.atlassian.com/manage-profile/security/api-tokens"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={styles.link}
                  >
                    Atlassian Account Settings
                  </a>
                  )
                </span>
              </label>
              <input
                type="password"
                value={jiraToken}
                onChange={(e) => setJiraToken(e.target.value)}
                placeholder="Your Jira API token"
                style={styles.input}
                required
              />
            </div>
            <button type="submit" style={styles.button}>
              Save Jira Credentials
            </button>
          </form>
        </div>
      </div>

      <div style={styles.infoBox}>
        <h3>How to get credentials:</h3>
        <ul style={styles.infoList}>
          <li>
            <strong>Slack:</strong> Create a Slack app at api.slack.com/apps, install it to your
            workspace, and copy the Bot User OAuth Token
          </li>
          <li>
            <strong>Gmail:</strong> Create OAuth 2.0 credentials in Google Cloud Console, enable
            Gmail API, and complete the OAuth flow to get refresh token
          </li>
          <li>
            <strong>Jira:</strong> Go to your Atlassian account settings, create an API token,
            and use it with your email
          </li>
        </ul>
      </div>
    </div>
  )
}

const styles = {
  container: {
    maxWidth: '900px',
    margin: '0 auto',
    padding: '2rem',
  },
  title: {
    fontSize: '2rem',
    marginBottom: '0.5rem',
  },
  subtitle: {
    color: '#666',
    marginBottom: '2rem',
  },
  sections: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2rem',
  },
  section: {
    backgroundColor: 'white',
    padding: '2rem',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  sectionHeader: {
    display: 'flex',
    alignItems: 'center',
    marginBottom: '1.5rem',
    fontSize: '1.5rem',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
  },
  label: {
    fontWeight: '500',
    color: '#333',
  },
  helpText: {
    fontSize: '0.875rem',
    color: '#666',
    fontWeight: 'normal',
  },
  link: {
    color: '#007bff',
    textDecoration: 'none',
  },
  input: {
    padding: '0.75rem',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '1rem',
  },
  textarea: {
    padding: '0.75rem',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '1rem',
    fontFamily: 'monospace',
    resize: 'vertical',
  },
  button: {
    padding: '0.75rem 1.5rem',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '1rem',
    cursor: 'pointer',
    alignSelf: 'flex-start',
  },
  success: {
    backgroundColor: '#d4edda',
    color: '#155724',
    padding: '1rem',
    borderRadius: '4px',
    marginBottom: '1rem',
  },
  error: {
    backgroundColor: '#f8d7da',
    color: '#721c24',
    padding: '1rem',
    borderRadius: '4px',
    marginBottom: '1rem',
  },
  infoBox: {
    backgroundColor: '#e7f3ff',
    padding: '1.5rem',
    borderRadius: '8px',
    marginTop: '2rem',
  },
  infoList: {
    marginTop: '1rem',
    paddingLeft: '1.5rem',
    lineHeight: '1.8',
  },
}
