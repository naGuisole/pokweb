// src/stores/auth.js
import { defineStore } from 'pinia'
import { authService } from '@/services/auth.service'
import { jwtDecode } from 'jwt-decode'
import router from '@/router'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    // État de l'utilisateur
    user: null,
    token: null,
    // État de chargement global
    loading: false,
    // Gestion des erreurs
    error: null,

    // Etat du jeton d'argile
    clayTokenHolder: null,

    // Etat des chasseurs de primes
    bountyHunters: [],
    clayTokenHistory: []
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.is_admin || false,
    userProfile: (state) => state.user,
    getError: (state) => state.error,
    clayTokenHolderData: (state) => state.clayTokenHolder,
    bountyHuntersList: (state) => state.bountyHunters
  },

  actions: {
    // Connexion
    async login(email, password) {
      this.loading = true
      this.error = null
      try {
        const response = await authService.login(email, password)
        this.token = response.access_token
        localStorage.setItem('token', response.access_token)
        
        // Décodage du token pour les infos de base
        const decoded = jwtDecode(response.access_token)
        
        // Récupération du profil complet
        await this.fetchUserProfile()
        
        return response
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors de la connexion'
        throw error
      } finally {
        this.loading = false
      }
    },

    // Inscription
    async register(userData) {
      this.loading = true
      this.error = null
      try {
        console.log("Register dans store:", userData);
        
        // Inscription par l'API
        const user = await authService.register(userData)
        
        return user
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors de l\'inscription'
        throw error
      } finally {
        this.loading = false
      }
    },

    // Récupération du profil
    async fetchUserProfile() {
      if (!this.token) return

      try {
        const user = await authService.getProfile()
        this.user = user
        return user
      } catch (error) {
        this.error = 'Erreur lors de la récupération du profil'
        // Si erreur d'authentification, on déconnecte
        if (error.response?.status === 401) {
          this.logout()
        }
        throw error
      }
    },

    // Mise à jour du profil
    async updateProfile(profileData) {
      this.loading = true
      this.error = null
      try {
        console.log('Données envoyées:', profileData)

        const updatedUser = await authService.updateProfile(profileData)
        this.user = updatedUser
        return updatedUser
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors de la mise à jour du profil'
        throw error
      } finally {
        this.loading = false
      }
    },

    // Upload d'image de profil
    async uploadProfileImage(file) {
      this.loading = true
      this.error = null
      try {
        console.log('uploadProfileImage in store with file:', file);
        
        const response = await authService.uploadProfileImage(file)
        this.user = {
          ...this.user,
          profile_image_path: response.path
        }
        return response
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors du téléchargement de l\'image'
        throw error
      } finally {
        this.loading = false
      }
    },

    async getCurrentClayTokenHolder() {
      try {
        const holder = await authService.getCurrentClayTokenHolder()
        this.clayTokenHolder = holder
        return holder
      } catch (error) {
        console.error('Erreur lors de la récupération du détenteur du jeton:', error)
        throw error
      }
    },

    async getBountyHuntersRanking(limit = 10) {
      try {
        const hunters = await authService.getBountyHuntersRanking(limit)
        this.bountyHunters = hunters
        return hunters
      } catch (error) {
        console.error('Erreur lors de la récupération du classement des chasseurs:', error)
        throw error
      }
    },

    async getClayTokenHistory(skip = 0, limit = 50) {
      try {
        const history = await authService.getClayTokenHistory(skip, limit)
        this.clayTokenHistory = history
        return history
      } catch (error) {
        console.error('Erreur lors de la récupération de l\'historique du jeton:', error)
        throw error
      }
    },

    async fetchUserStats() {
      if (!this.user?.id) return null
    
      try {
        const stats = await authService.fetchUserStats(this.user.id)
        return {
          totalGames: stats.total_games || 0,
          victories: stats.victories || 0,
          bountyCount: stats.bounties || 0,
          roi: parseFloat(stats.roi || 0).toFixed(2)
        }
      } catch (error) {
        console.error('Erreur lors de la récupération des statistiques:', error)
        throw error
      }
    },

    // Déconnexion
    logout() {
      this.user = null
      this.token = null
      this.error = null
      localStorage.removeItem('token')
      router.push('/login')
    },

    // Initialisation du store au démarrage de l'application
    async init() {
      const token = localStorage.getItem('token')
      if (token) {
        try {
          this.token = token
          await this.fetchUserProfile()
        } catch (error) {
          // En cas d'erreur (token expiré par exemple), on nettoie
          this.logout()
        }
      }
    },

    // Nettoyage des erreurs
    clearError() {
      this.error = null
    }
  }
})