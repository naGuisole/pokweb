// src/services/league.service.js
import api from './api'

export const leagueService = {
  // Récupérer toutes les ligues
  async getLeagues() {
    const response = await api.get('/leagues/')
    return response.data
  },

  // Récupérer une ligue spécifique
  async getLeague(id) {
    const response = await api.get(`/leagues/${id}`)
    return response.data
  },

  // Créer une nouvelle ligue
  async createLeague(leagueData) {
    const response = await api.post('/leagues/', leagueData)
    return response.data
  },

  // Demander à rejoindre une ligue
  async joinLeague(leagueId) {
    const response = await api.post(`/leagues/${leagueId}/join`)
    return response.data
  },

  // Approuver un membre (admin)
  async approveMember(leagueId, userId) {
    const response = await api.post(`/leagues/${leagueId}/approve/${userId}`)
    return response.data
  },

  // Refuser un membre (admin)
  async rejectMember(leagueId, userId) {
    const response = await api.post(`/leagues/${leagueId}/reject/${userId}`)
    return response.data
  },

  // Ajouter un admin (admin)
  async addAdmin(leagueId, userId) {
    const response = await api.post(`/leagues/${leagueId}/admins`, {
      user_id: userId
    })
    return response.data
  },

  // Obtenir les membres d'une ligue
  async getLeagueMembers(leagueId) {
    const response = await api.get(`/leagues/${leagueId}/members`)
    return response.data
  },

  // Obtenir les admins d'une ligue
  async getLeagueAdmins(leagueId) {
    const response = await api.get(`/leagues/${leagueId}/admins`)
    return response.data
  }
}