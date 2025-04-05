// src/services/tournament.service.js
import api from './api'

export const tournamentService = {
  // Récupération des tournois
  async getTournaments(filters = {}) {
    const response = await api.get('/tournaments/', { params: filters })
    console.log("Tournois récupérés avec configurations:", response.data);
    return response.data
  },

  async getTournament(id) {
    const response = await api.get(`/tournaments/${id}`)
    console.log("Tournoi détaillé récupéré avec configurations:", response.data);
    return response.data
  },

  // Gestion des tournois
  async createTournament(tournamentData) {
    console.log("Création du tournoi avec données:", tournamentData);
    const response = await api.post('/tournaments/', tournamentData)
    return response.data
  },

  async updateTournament(id, tournamentData) {
    console.log("Mise à jour du tournoi avec données:", tournamentData);
    const response = await api.put(`/tournaments/${id}`, tournamentData)
    return response.data
  },

  async deleteTournament(id) {
    const response = await api.delete(`/tournaments/${id}`)
    return response.data
  },

  // Gestion des états du tournoi
  async startTournament(id) {
    const response = await api.post(`/tournaments/${id}/start`)
    return response.data
  },

  async pauseTournament(id) {
    const response = await api.post(`/tournaments/${id}/pause`)
    return response.data
  },

  async resumeTournament(id) {
    const response = await api.post(`/tournaments/${id}/resume`)
    return response.data
  },
  
  async completeTournament(id) {
    const response = await api.post(`/tournaments/${id}/complete`)
    return response.data
  },
  
  // Gestion du timer et des niveaux
  async updateTournamentTimer(id, secondsRemaining) {
    const response = await api.post(`/tournaments/${id}/timer`, {
      seconds_remaining: secondsRemaining
    })
    return response.data
  },
  
  async updateTournamentLevel(id, levelNumber) {
    const response = await api.post(`/tournaments/${id}/levels/${levelNumber}`)
    return response.data
  },

  // Gestion des joueurs
  async registerPlayer(tournamentId) {
    const response = await api.post(`/tournaments/${tournamentId}/register`)
    return response.data
  },

  async unregisterPlayer(tournamentId) {
    const response = await api.post(`/tournaments/${tournamentId}/unregister`)
    return response.data
  },
  
  async processRebuy(tournamentId, rebuyData) {
    const response = await api.post(`/tournaments/${tournamentId}/rebuy`, rebuyData)
    return response.data
  },
  
  async eliminatePlayer(tournamentId, eliminationData) {
    const response = await api.post(`/tournaments/${tournamentId}/eliminate`, eliminationData)
    return response.data
  },

  // Gestion des tables
  async rebalanceTables(tournamentId) {
    const response = await api.post(`/tournaments/${tournamentId}/tables`)
    return response.data
  },
  
  async redrawTables(tournamentId) {
    const response = await api.post(`/tournaments/${tournamentId}/tables/redraw`)
    return response.data
  },
  
  async breakTable(tournamentId, tableIndex) {
    const response = await api.post(`/tournaments/${tournamentId}/tables/break`, {
      table_index: tableIndex
    })
    return response.data
  },

  // Gestion du Jeton d'Argile
  async updateClayTokenHolder(tournamentId, playerId) {
    const response = await api.post(`/tournaments/${tournamentId}/clay-token`, {
      player_id: playerId
    })
    return response.data
  },

  // Statistiques
  async getTournamentStatistics(tournamentId) {
    const response = await api.get(`/tournaments/${tournamentId}/statistics`)
    return response.data
  }
}