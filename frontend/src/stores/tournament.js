// src/stores/tournament.js
import { defineStore } from 'pinia'
import { tournamentService } from '@/services/tournament.service'

export const useTournamentStore = defineStore('tournament', {
  state: () => ({
    // Liste des tournois - assurez-vous que c'est initialisé comme un tableau vide
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
      // Vérifiez que state.tournaments est bien un tableau avant d'utiliser le spread operator
      let filtered = Array.isArray(state.tournaments) ? [...state.tournaments] : []
      
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
      return Array.isArray(state.tournaments) ? 
        state.tournaments.find(t => t.status === 'IN_PROGRESS') : null
    },

    // Prochain tournoi planifié
    nextTournament: (state) => {
      if (!Array.isArray(state.tournaments) || state.tournaments.length === 0) {
        console.log("Pas de tournois ou format incorrect");
        return null;
      }
      
      // Conversion de la date actuelle en timestamp pour comparaison
      const now = new Date().getTime();
      
      // Filtrer les tournois planifiés dont la date est future
      const plannedTournaments = state.tournaments.filter(t => {
        if (t.status !== 'PLANNED') return false;
        
        // S'assurer que la date est bien parsée
        const tournamentDate = new Date(t.date).getTime();
        const isFuture = tournamentDate > now;
        
        return isFuture;
      });
      
      if (plannedTournaments.length === 0) {
        return null;
      }
      
      // Trier par date (du plus proche au plus éloigné)
      const sorted = plannedTournaments.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
      return sorted[0];
    },
    
    // Vérifier si un utilisateur est inscrit à un tournoi
    isUserRegistered: (state) => (tournamentId, userId) => {
      const tournament = Array.isArray(state.tournaments) ? 
        state.tournaments.find(t => t.id === tournamentId) : null
      
      if (!tournament || !Array.isArray(tournament.participations)) return false
      
      return tournament.participations.some(player => player.id === userId)
    },

    // Active players in the current tournament
    getActivePlayers: (state) => {
      if (!state.currentTournament || !state.currentTournament.participations) {
        return []
      }
      return state.currentTournament.participations.filter(p => p.is_active)
    },
    
    // Eliminated players in the current tournament
    getEliminatedPlayers: (state) => {
      if (!state.currentTournament || !state.currentTournament.participations) {
        return []
      }
      return state.currentTournament.participations.filter(p => !p.is_active)
        .sort((a, b) => (a.current_position || 999) - (b.current_position || 999))
    },
    
    // Nombre total de joueurs dans le tournoi en cours
    getCurrentTournamentPlayersCount: (state) => {
      if (!state.currentTournament || !state.currentTournament.participations) {
        return 0
      }
      return state.currentTournament.participations.length
    },
    
    // Position pour la prochaine élimination
    getNextEliminationPosition: (state) => {
      if (!state.currentTournament || !state.currentTournament.participations) {
        return 1
      }
      
      // Compter les joueurs éliminés
      const eliminatedCount = state.currentTournament.participations.filter(p => !p.is_active).length
      
      // La prochaine position d'élimination est le nombre total de joueurs moins le nombre d'éliminés
      return state.currentTournament.participations.length - eliminatedCount
    },

    // Dernier tournoi terminé
    lastCompletedTournament: (state) => {
      if (!Array.isArray(state.tournaments) || state.tournaments.length === 0) return null
      return state.tournaments
        .filter(t => t.status === 'COMPLETED')
        .sort((a, b) => new Date(b.date) - new Date(a.date))[0]
    }
  },

  actions: {
    // Chargement de la liste des tournois
    async fetchTournaments() {
      this.loading = true;
      try {
        // Réinitialiser les filtres pour s'assurer d'obtenir tous les tournois
        const tempFilters = { ...this.filters };
        this.filters = { status: null, type: null };
        
        const response = await tournamentService.getTournaments(this.filters);
        
        // Restaurer les filtres originaux
        this.filters = tempFilters;
        
        if (Array.isArray(response)) {
          this.tournaments = response;
        } else if (response && Array.isArray(response.data)) {
          this.tournaments = response.data;
        } else {
          console.warn('Format de réponse inattendu:', response);
          this.tournaments = [];
        }
        
        return this.tournaments;
      } catch (error) {
        this.error = 'Erreur lors du chargement des tournois';
        console.error('Erreur chargement tournois:', error);
        this.tournaments = [];
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // Chargement d'un tournoi spécifique
    async fetchTournament(id) {
      this.loading = true
      try {
        this.currentTournament = await tournamentService.getTournament(id)
        return this.currentTournament
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
        if (Array.isArray(this.tournaments)) {
          this.tournaments.push(newTournament)
        } else {
          this.tournaments = [newTournament]
        }
        return newTournament
      } catch (error) {
        this.error = 'Erreur lors de la création du tournoi'
        throw error
      } finally {
        this.saving = false
      }
    },

    // Mise à jour des informations d'un tournoi
    async updateTournament(id, data) {
      this.saving = true
      try {
        const updated = await tournamentService.updateTournament(id, data)
        if (Array.isArray(this.tournaments)) {
          const index = this.tournaments.findIndex(t => t.id === id)
          if (index !== -1) {
            this.tournaments[index] = updated
          }
        }
        if (this.currentTournament?.id === id) {
          this.currentTournament = updated
        }
        return updated
      } catch (error) {
        this.error = 'Erreur lors de la mise à jour du tournoi'
        throw error
      } finally {
        this.saving = false
      }
    },

    // Supprimer un tournoi
    async deleteTournament(id) {
      try {
        await tournamentService.deleteTournament(id)
        if (Array.isArray(this.tournaments)) {
          this.tournaments = this.tournaments.filter(t => t.id !== id)
        }
        return true
      } catch (error) {
        this.error = 'Erreur lors de la suppression du tournoi'
        throw error
      }
    },

    // Démarrer un tournoi
    async startTournament(id) {
      try {
        const result = await tournamentService.startTournament(id)
        await this.fetchTournaments()
        return result
      } catch (error) {
        this.error = 'Erreur lors du démarrage du tournoi'
        throw error
      }
    },

    // Mettre en pause un tournoi
    async pauseTournament(id) {
      try {
        const result = await tournamentService.pauseTournament(id)
        if (this.currentTournament?.id === id) {
          await this.fetchTournament(id)
        }
        return result
      } catch (error) {
        this.error = 'Erreur lors de la mise en pause du tournoi'
        throw error
      }
    },

    // Reprendre un tournoi après une pause
    async resumeTournament(id) {
      try {
        const result = await tournamentService.resumeTournament(id)
        if (this.currentTournament?.id === id) {
          await this.fetchTournament(id)
        }
        return result
      } catch (error) {
        this.error = 'Erreur lors de la reprise du tournoi'
        throw error
      }
    },

    // Terminer un tournoi
    async completeTournament(id) {
      try {
        const result = await tournamentService.completeTournament(id)
        await this.fetchTournaments()
        return result
      } catch (error) {
        this.error = 'Erreur lors de la finalisation du tournoi'
        throw error
      }
    },

    // Gestion du timer et des niveaux
    async updateTournamentTimer(id, secondsRemaining) {
      try {
        const result = await tournamentService.updateTournamentTimer(id, secondsRemaining)
        return result
      } catch (error) {
        this.error = 'Erreur lors de la mise à jour du timer'
        throw error
      }
    },

    async updateTournamentLevel(id, levelNumber) {
      try {
        const result = await tournamentService.updateTournamentLevel(id, levelNumber)
        if (this.currentTournament?.id === id) {
          await this.fetchTournament(id)
        }
        return result
      } catch (error) {
        this.error = 'Erreur lors du changement de niveau'
        throw error
      }
    },

    // Gestion des inscriptions
    async registerPlayer(tournamentId) {
      try {
        await tournamentService.registerPlayer(tournamentId)
        await this.fetchTournament(tournamentId)
        return true
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
        return true
      } catch (error) {
        this.error = 'Erreur lors de la désinscription'
        throw error
      }
    },

    // Gestion des rebuys et éliminations
    async processRebuy(tournamentId, rebuyData) {
      try {
        const result = await tournamentService.processRebuy(tournamentId, rebuyData)
        if (this.currentTournament?.id === tournamentId) {
          await this.fetchTournament(tournamentId)
        }
        return result
      } catch (error) {
        this.error = 'Erreur lors du rebuy'
        throw error
      }
    },

    async eliminatePlayer(tournamentId, eliminationData) {
      try {
        const result = await tournamentService.eliminatePlayer(tournamentId, eliminationData)
        if (this.currentTournament?.id === tournamentId) {
          await this.fetchTournament(tournamentId)
        }
        return result
      } catch (error) {
        this.error = 'Erreur lors de l\'élimination du joueur'
        throw error
      }
    },

    // Gestion des tables
    async rebalanceTables(tournamentId) {
      try {
        const result = await tournamentService.rebalanceTables(tournamentId)
        if (this.currentTournament?.id === tournamentId) {
          await this.fetchTournament(tournamentId)
        }
        return result
      } catch (error) {
        this.error = 'Erreur lors du rééquilibrage des tables'
        throw error
      }
    },

    async redrawTables(tournamentId) {
      try {
        const result = await tournamentService.redrawTables(tournamentId)
        if (this.currentTournament?.id === tournamentId) {
          await this.fetchTournament(tournamentId)
        }
        return result
      } catch (error) {
        this.error = 'Erreur lors du redraw des tables'
        throw error
      }
    },

    async breakTable(tournamentId, tableIndex) {
      try {
        const result = await tournamentService.breakTable(tournamentId, tableIndex)
        if (this.currentTournament?.id === tournamentId) {
          await this.fetchTournament(tournamentId)
        }
        return result
      } catch (error) {
        this.error = 'Erreur lors de la suppression de la table'
        throw error
      }
    },

    // Gestion du jeton d'argile
    async updateClayTokenHolder(tournamentId, playerId) {
      try {
        const result = await tournamentService.updateClayTokenHolder(tournamentId, playerId)
        if (this.currentTournament?.id === tournamentId) {
          await this.fetchTournament(tournamentId)
        }
        return result
      } catch (error) {
        this.error = 'Erreur lors de la mise à jour du détenteur du jeton'
        throw error
      }
    }
  }
});