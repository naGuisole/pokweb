// src/services/auth.service.js
import api from './api'

export const authService = {
  async login(email, password) {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)

    const response = await api.post('/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    return response.data
  },

  async register(userData) {
    // Séparation des données utilisateur et de l'image
    const { profile_image, ...userInfo } = userData

    // Première requête : création de l'utilisateur
    const response = await api.post('/auth/register', userInfo)

    // Si une image est fournie, on l'envoie dans une seconde requête
    if (profile_image) {
      const formData = new FormData()
      formData.append('profile_image', profile_image)

      await api.post('/users/profile/image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    }

    return response.data
  },

  async getProfile() {
    const response = await api.get('/users/profile')
    // Ajouter la gestion du cache pour l'image de profil
    if (response.data?.profile_image_path) {
      response.data.profile_image_path = `${response.data.profile_image_path}`
    }
    return response.data
  },

  async updateProfile(profileData) {
    // Séparation des données utilisateur et de l'image
    console.log('Données profileData:', profileData)

    //const { profile_image, ...userInfo } = userData
    //console.log('Données envoyées:', userInfo)

    const response = await api.put('/users/profile', profileData)

    return response.data
  },

  async uploadProfileImage(file) {
    const formData = new FormData()
    formData.append('image', file)
    
    const response = await api.post('/users/profile/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  // Détenteur actuel du jeton d'argile
  async getCurrentClayTokenHolder() {
    console.log('calling API:','/api/users/current-clay-token-holder')
    const response = await api.get('/users/current-clay-token-holder')
    console.log(response.data)
    return response.data
  },

  // Classement des chasseurs de prime
  async getBountyHuntersRanking(limit = 10) {
    const response = await api.get('/users/bounty-hunters', {
      params: { limit }
    })
    return response.data
  },

  async fetchUserStats(userId) {
    const response = await api.get(`/users/statistics/${userId}`)
    return response.data
  },

  // Historique du jeton d'argile
  async getClayTokenHistory(skip = 0, limit = 50) {
    const response = await api.get('/users/clay-token/history', {
      params: { skip, limit }
    })
    return response.data
  }
}
