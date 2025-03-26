// src/stores/configuration.js (corrigé)
import { defineStore } from 'pinia'
import { configurationService } from '@/services/configuration.service'

export const useConfigurationStore = defineStore('configuration', {
  state: () => ({
    tournamentConfigs: [],
    blindsStructures: [], // Ajout de cette propriété manquante
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

    // Structures de blindes
    async fetchBlindsStructures() {
      this.loading = true
      try {
        const structures = await configurationService.getBlindsStructures()
        this.blindsStructures = structures
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors du chargement des structures de blindes'
        throw error
      } finally {
        this.loading = false
      }
    },

    async createBlindsStructure(structureData) {
      this.loading = true
      try {
        const newStructure = await configurationService.createBlindsStructure(structureData)
        this.blindsStructures.push(newStructure)
        return newStructure
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors de la création de la structure de blindes'
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateBlindsStructure(id, structureData) {
      this.loading = true
      try {
        const updatedStructure = await configurationService.updateBlindsStructure(id, structureData)
        const index = this.blindsStructures.findIndex(s => s.id === id)
        if (index !== -1) {
          this.blindsStructures[index] = updatedStructure
        }
        return updatedStructure
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors de la mise à jour de la structure de blindes'
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteBlindsStructure(id) {
      this.loading = true
      try {
        await configurationService.deleteBlindsStructure(id)
        this.blindsStructures = this.blindsStructures.filter(s => s.id !== id)
      } catch (error) {
        this.error = error.response?.data?.detail || 'Erreur lors de la suppression de la structure de blindes'
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