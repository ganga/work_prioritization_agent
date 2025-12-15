import api from './api'

export const dashboardService = {
  async sync() {
    const response = await api.post('/sync')
    return response.data
  },

  async getItems(params = {}) {
    const response = await api.get('/items', { params })
    return response.data
  },

  async getItem(itemId) {
    const response = await api.get(`/items/${itemId}`)
    return response.data
  },

  async updateItem(itemId, updates) {
    const response = await api.patch(`/items/${itemId}`, updates)
    return response.data
  },

  async getStats() {
    const response = await api.get('/dashboard/stats')
    return response.data
  },

  async setSlackCredentials(token, workspace) {
    const response = await api.post('/integrations/slack', {
      token,
      workspace,
    })
    return response.data
  },

  async setGmailCredentials(credentialsJson) {
    const response = await api.post('/integrations/gmail', {
      credentials_json: credentialsJson,
    })
    return response.data
  },

  async setJiraCredentials(url, email, apiToken) {
    const response = await api.post('/integrations/jira', {
      url,
      email,
      api_token: apiToken,
    })
    return response.data
  },

  async createReminder(reminder) {
    const response = await api.post('/reminders', reminder)
    return response.data
  },

  async getReminders() {
    const response = await api.get('/reminders')
    return response.data
  },
}
