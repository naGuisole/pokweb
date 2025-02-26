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
      console.log("Calcul nextTournament, tournaments:", state.tournaments);
      if (!Array.isArray(state.tournaments) || state.tournaments.length === 0) {
        console.log("Pas de tournois ou format incorrect");
        return null;
      }
      
      const now = new Date();
      const plannedTournaments = state.tournaments
        .filter(t => t.status === 'PLANNED' && new Date(t.date) > now);
      
      console.log("Tournois planifiés:", plannedTournaments);
      
      if (plannedTournaments.length === 0) {
        console.log("Pas de tournois planifiés à venir");
        return null;
      }
      
      // Trier par date (du plus proche au plus éloigné)
      const sorted = plannedTournaments.sort((a, b) => new Date(a.date) - new Date(b.date));
      console.log("Tournoi le plus proche:", sorted[0]);
      return sorted[0];
    },
    
    // Vérifier si un utilisateur est inscrit à un tournoi
    isUserRegistered: (state) => (tournamentId, userId) => {
      const tournament = Array.isArray(state.tournaments) ? 
        state.tournaments.find(t => t.id === tournamentId) : null
      
      if (!tournament || !Array.isArray(tournament.registered_players)) return false
      
      return tournament.registered_players.some(player => player.id === userId)
    },

    // Joueurs actifs du tournoi en cours
    getActivePlayers: (state) => {
      if (!state.currentTournament || !state.currentTournament.players) {
        return []
      }
      return state.currentTournament.players.filter(p => !p.is_eliminated)
    },
    
    // Joueurs éliminés du tournoi en cours
    getEliminatedPlayers: (state) => {
      if (!state.currentTournament || !state.currentTournament.players) {
        return []
      }
      return state.currentTournament.players.filter(p => p.is_eliminated)
        .sort((a, b) => (a.final_position || 999) - (b.final_position || 999))
    },
    
    // Nombre total de joueurs dans le tournoi en cours
    getCurrentTournamentPlayersCount: (state) => {
      if (!state.currentTournament || !state.currentTournament.players) {
        return 0
      }
      return state.currentTournament.players.length
    },
    
    // Position pour la prochaine élimination
    getNextEliminationPosition: (state) => {
      if (!state.currentTournament || !state.currentTournament.players) {
        return 1
      }
      const eliminatedPlayers = state.currentTournament.players.filter(p => p.is_eliminated)
      return eliminatedPlayers.length + 1
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
        
        console.log("API Response:", response);
        
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
    async updateTournamentStatus(tournamentId, newStatus) {
      try {
        const updated = await tournamentService.updateStatus(tournamentId, newStatus)
        if (Array.isArray(this.tournaments)) {
          const index = this.tournaments.findIndex(t => t.id === tournamentId)
          if (index !== -1) {
            this.tournaments[index] = updated
          }
        }
        if (this.currentTournament?.id === tournamentId) {
          this.currentTournament = updated
        }
        return updated
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
        await this.fetchTournaments() // Rafraîchir la liste des tournois
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
        await this.fetchTournaments() // Rafraîchir la liste des tournois
        return true
      } catch (error) {
        this.error = 'Erreur lors de la désinscription'
        throw error
      }
    },

    // Actions supplémentaires qui pourraient être manquantes 
    // Par rapport à la vue TournamentsView.vue

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
        await this.fetchTournaments()
        return result
      } catch (error) {
        this.error = 'Erreur lors de la mise en pause du tournoi'
        throw error
      }
    },

    // Mettre à jour un tournoi
    async updateTournament(id, data) {
      try {
        const updated = await tournamentService.updateTournament(id, data)
        if (Array.isArray(this.tournaments)) {
          const index = this.tournaments.findIndex(t => t.id === id)
          if (index !== -1) {
            this.tournaments[index] = updated
          }
        }
        return updated
      } catch (error) {
        this.error = 'Erreur lors de la mise à jour du tournoi'
        throw error
      }
    }
  }
})