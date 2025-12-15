import api from './api'

export const authService = {
  async register(email, fullName, password) {
    const response = await api.post('/register', {
      email,
      full_name: fullName,
      password,
    })
    return response.data
  },

  async login(email, password) {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)
    
    const response = await api.post('/token', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token)
    }
    
    return response.data
  },

  logout() {
    localStorage.removeItem('token')
  },

  isAuthenticated() {
    return !!localStorage.getItem('token')
  },
}
