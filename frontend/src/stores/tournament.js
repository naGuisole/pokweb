// src/stores/tournament.js
import { defineStore } from 'pinia'
import { tournamentService } from '@/services/tournament.service'

export const useTournamentStore = defineStore('tournament', {
  state: () => ({
    // Liste des tournois
    tournaments: [],
    // Tournoi actuellement sélectionné/en cours
    currentTournament: null,
    // États de chargement
    loading: false,
    saving: false,
    // Messages d'erreur
    error: null,
    // Filtres actifs
    filters: {
      status: null,
      type: null
    },
    // Pagination
    pagination: {
      page: 1,
      itemsPerPage: 10,
      totalItems: 0
    }
  }),

  getters: {
    // Tournois filtrés et triés
    getFilteredTournaments: (state) => {
      let filtered = [...state.tournaments]
      
      if (state.filters.status) {
        filtered = filtered.filter(t => t.status === state.filters.status)
      }
      
      if (state.filters.type) {
        filtered = filtered.filter(t => t.tournament_type === state.filters.type)
      }
      
      return filtered.sort((a, b) => new Date(b.date) - new Date(a.date))
    },

    // Tournoi en cours actif
    activeTournament: (state) => {
      return state.tournaments.find(t => t.status === 'IN_PROGRESS')
    },

    // Prochain tournoi planifié
    nextTournament: (state) => {
      if (!state.tournaments || state.tournaments.length === 0) return null
      const now = new Date()
      return state.tournaments
        .filter(t => t.status === 'PLANNED' && new Date(t.date) > now)
        .sort((a, b) => new Date(a.date) - new Date(b.date))[0]
    }
  },

  actions: {
    // Chargement de la liste des tournois
    async fetchTournaments() {
      this.loading = true
      try {
        const response = await tournamentService.getTournaments(
          this.filters,
          this.pagination.page,
          this.pagination.itemsPerPage
        )
        this.tournaments = response.data
        this.pagination.totalItems = response.total
      } catch (error) {
        this.error = 'Erreur lors du chargement des tournois'
        throw error
      } finally {
        this.loading = false
      }
    },

    // Chargement d'un tournoi spécifique
    async fetchTournament(id) {
      this.loading = true
      try {
        this.currentTournament = await tournamentService.getTournament(id)
      } catch (error) {
        this.error = 'Erreur lors du chargement du tournoi'
        throw error
      } finally {
        this.loading = false
      }
    },

    // Création d'un nouveau tournoi
    async createTournament(tournamentData) {
      this.saving = true
      try {
        const newTournament = await tournamentService.createTournament(tournamentData)
        this.tournaments.push(newTournament)
        return newTournament
      } catch (error) {
        this.error = 'Erreur lors de la création du tournoi'
        throw error
      } finally {
        this.saving = false
      }
    },

    // Mise à jour des informations d'un tournoi
    async updateTournamentStatus(tournamentId, newStatus) {
      try {
        const updated = await tournamentService.updateStatus(tournamentId, newStatus)
        const index = this.tournaments.findIndex(t => t.id === tournamentId)
        if (index !== -1) {
          this.tournaments[index] = updated
        }
        if (this.currentTournament?.id === tournamentId) {
          this.currentTournament = updated
        }
      } catch (error) {
        this.error = 'Erreur lors de la mise à jour du statut'
        throw error
      }
    },

    // Gestion des inscriptions
    async registerPlayer(tournamentId) {
      try {
        await tournamentService.registerPlayer(tournamentId)
        await this.fetchTournament(tournamentId)
      } catch (error) {
        this.error = 'Erreur lors de l\'inscription'
        throw error
      }
    },

    // Gestion des désistements
    async unregisterPlayer(tournamentId) {
      try {
        await tournamentService.unregisterPlayer(tournamentId)
        await this.fetchTournament(tournamentId)
      } catch (error) {
        this.error = 'Erreur lors de la désinscription'
        throw error
      }
    },

    // Gestion des places aux tables
    async updateTableState(tournamentId, tableState) {
      try {
        await tournamentService.updateTableState(tournamentId, tableState)
        await this.fetchTournament(tournamentId)
      } catch (error) {
        this.error = 'Erreur lors de la mise à jour des tables'
        throw error
      }
    }
  }
})
