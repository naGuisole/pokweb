// src/services/configuration.service.js
import api from './api'

export const configurationService = {
  // Configurations de tournoi
  async getTournamentConfigs() {
    const response = await api.get('/configurations/tournament')
    return response.data
  },

  async getTournamentConfig(id) {
    const response = await api.get(`/configurations/tournament/${id}`)
    return response.data
  },

  async createTournamentConfig(configData) {
    const response = await api.post('/configurations/tournament', configData)
    return response.data
  },

  async updateTournamentConfig(id, configData) {
    const response = await api.put(`/configurations/tournament/${id}`, configData)
    return response.data
  },

  async deleteTournamentConfig(id) {
    const response = await api.delete(`/configurations/tournament/${id}`)
    return response.data
  },

  // Configurations sonores
  async getSoundConfigs() {
    const response = await api.get('/configurations/sound')
    return response.data
  },

  async getSoundConfig(id) {
    const response = await api.get(`/configurations/sound/${id}`)
    return response.data
  },

  async createSoundConfig(formData) {
    const response = await api.post('/configurations/sound', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  async updateSoundConfig(id, formData) {
    const response = await api.put(`/configurations/sound/${id}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  async deleteSoundConfig(id) {
    const response = await api.delete(`/configurations/sound/${id}`)
    return response.data
  }
}