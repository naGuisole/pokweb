// src/stores/league.js
import { defineStore } from 'pinia'
import { leagueService } from '@/services/league.service'

export const useLeagueStore = defineStore('league', {
  state: () => ({
    // Liste des ligues
    leagues: [],
    // Ligue actuellement sélectionnée/en cours
    currentLeague: null,
    // États de chargement
    loading: false,
    saving: false,
    // Gestion des erreurs
    error: null
  }),

  getters: {
    // Toutes les ligues disponibles
    getAvailableLeagues: (state) => state.leagues,

    // Ligue actuelle
    getCurrentLeague: (state) => state.currentLeague,

    // Vérifier si l'utilisateur est admin de sa ligue
    isLeagueAdmin: (state) => {
      if (!state.currentLeague) return false
      return state.currentLeague.admins.includes(state.currentUser?.id)
    }
  },

  actions: {
    // Récupérer toutes les ligues
    async fetchLeagues() {
      this.loading = true
      try {
        const leagues = await leagueService.getLeagues()
        this.leagues = leagues
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors du chargement des ligues'
        throw error
      } finally {
        this.loading = false
      }
    },

    // Récupérer une ligue spécifique
    async fetchLeague(leagueId) {
      this.loading = true
      try {
        const league = await leagueService.getLeague(leagueId)
        this.currentLeague = league
        return league
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors du chargement de la ligue'
        throw error
      } finally {
        this.loading = false
      }
    },

    // Créer une nouvelle ligue
    async createLeague(leagueData) {
      this.saving = true
      try {
        const newLeague = await leagueService.createLeague(leagueData)
        this.leagues.push(newLeague)
        return newLeague
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors de la création de la ligue'
        throw error
      } finally {
        this.saving = false
      }
    },

    // Rejoindre une ligue
    async joinLeague(leagueId) {
      this.saving = true
      try {
        await leagueService.joinLeague(leagueId)
        await this.fetchLeague(leagueId)
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors de la demande d\'adhésion'
        throw error
      } finally {
        this.saving = false
      }
    },

    // Approuver un membre (admin seulement)
    async approveMember(leagueId, userId) {
      try {
        await leagueService.approveMember(leagueId, userId)
        // Rafraîchir les données de la ligue
        if (this.currentLeague?.id === leagueId) {
          await this.fetchLeague(leagueId)
        }
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors de l\'approbation du membre'
        throw error
      }
    },

    // Ajouter un admin (admin seulement)
    async addAdmin(leagueId, userId) {
      try {
        await leagueService.addAdmin(leagueId, userId)
        // Rafraîchir les données de la ligue
        if (this.currentLeague?.id === leagueId) {
          await this.fetchLeague(leagueId)
        }
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors de l\'ajout de l\'administrateur'
        throw error
      }
    },

    // Réinitialiser les erreurs
    clearError() {
      this.error = null
    }
  }
})