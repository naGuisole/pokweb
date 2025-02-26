// src/stores/configuration.js
import { defineStore } from 'pinia'
import { configurationService } from '@/services/configuration.service'

export const useConfigurationStore = defineStore('configuration', {
  state: () => ({
    tournamentConfigs: [],
    soundConfigs: [],
    loading: false,
    error: null
  }),

  getters: {
    getDefaultTournamentConfigs: (state) => {
      return state.tournamentConfigs.filter(config => config.is_default)
    },
    getUserTournamentConfigs: (state) => {
      return state.tournamentConfigs.filter(config => !config.is_default)
    },
    getDefaultSoundConfigs: (state) => {
      return state.soundConfigs.filter(config => config.is_default)
    },
    getUserSoundConfigs: (state) => {
      return state.soundConfigs.filter(config => !config.is_default)
    }
  },

  actions: {
    // Configurations de tournoi
    async fetchTournamentConfigs() {
      this.loading = true
      try {
        const configs = await configurationService.getTournamentConfigs()
        this.tournamentConfigs = configs
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors du chargement des configurations'
        throw error
      } finally {
        this.loading = false
      }
    },

    async createTournamentConfig(configData) {
      this.loading = true
      try {
        const newConfig = await configurationService.createTournamentConfig(configData)
        this.tournamentConfigs.push(newConfig)
        return newConfig
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors de la création de la configuration'
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateTournamentConfig(id, configData) {
      this.loading = true
      try {
        const updatedConfig = await configurationService.updateTournamentConfig(id, configData)
        const index = this.tournamentConfigs.findIndex(c => c.id === id)
        if (index !== -1) {
          this.tournamentConfigs[index] = updatedConfig
        }
        return updatedConfig
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors de la mise à jour de la configuration'
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteTournamentConfig(id) {
      this.loading = true
      try {
        await configurationService.deleteTournamentConfig(id)
        this.tournamentConfigs = this.tournamentConfigs.filter(c => c.id !== id)
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors de la suppression de la configuration'
        throw error
      } finally {
        this.loading = false
      }
    },

    // Configurations sonores
    async fetchSoundConfigs() {
      this.loading = true
      try {
        const configs = await configurationService.getSoundConfigs()
        this.soundConfigs = configs
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors du chargement des configurations sonores'
        throw error
      } finally {
        this.loading = false
      }
    },

    async createSoundConfig(formData) {
      this.loading = true
      try {
        const newConfig = await configurationService.createSoundConfig(formData)
        this.soundConfigs.push(newConfig)
        return newConfig
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors de la création de la configuration sonore'
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateSoundConfig(id, formData) {
      this.loading = true
      try {
        const updatedConfig = await configurationService.updateSoundConfig(id, formData)
        const index = this.soundConfigs.findIndex(c => c.id === id)
        if (index !== -1) {
          this.soundConfigs[index] = updatedConfig
        }
        return updatedConfig
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors de la mise à jour de la configuration sonore'
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteSoundConfig(id) {
      this.loading = true
      try {
        await configurationService.deleteSoundConfig(id)
        this.soundConfigs = this.soundConfigs.filter(c => c.id !== id)
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors de la suppression de la configuration sonore'
        throw error
      } finally {
        this.loading = false
      }
    },

    // Nettoyage des erreurs
    clearError() {
      this.error = null
    }
  }
})