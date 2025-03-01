// src/services/websocket.service.js
class WebSocketService {
    constructor() {
      this.socket = null
      this.isConnected = false
      this.reconnectAttempts = 0
      this.maxReconnectAttempts = 5
      this.reconnectInterval = 3000 // 3 secondes
      this.listeners = {}
      this.pingInterval = null
    }
  
    /**
     * Connecte au serveur WebSocket pour un tournoi spécifique
     * @param {Number} tournamentId - ID du tournoi à suivre
     * @returns {Promise} - Résout quand la connexion est établie
     */
    connect(tournamentId) {
      return new Promise((resolve, reject) => {
        if (this.socket && this.isConnected) {
          this.disconnect()
        }
  
        const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
        const wsUrl = `${protocol}://${window.location.host}/api/ws/tournaments/${tournamentId}`
        
        console.log(`Connecting to WebSocket: ${wsUrl}`)
        this.socket = new WebSocket(wsUrl)
  
        this.socket.onopen = () => {
          console.log('WebSocket connection established')
          this.isConnected = true
          this.reconnectAttempts = 0
          this.startPingInterval()
          resolve()
        }
  
        this.socket.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('Error parsing WebSocket message:', error)
          }
        }
  
        this.socket.onclose = (event) => {
          this.isConnected = false
          this.stopPingInterval()
          console.log(`WebSocket connection closed: ${event.code} - ${event.reason}`)
          
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
            setTimeout(() => this.connect(tournamentId), this.reconnectInterval)
          } else {
            console.log('Max reconnect attempts reached')
            reject(new Error('Failed to connect to tournament updates'))
          }
        }
  
        this.socket.onerror = (error) => {
          console.error('WebSocket error:', error)
        }
      })
    }
  
    /**
     * Déconnecte du serveur WebSocket
     */
    disconnect() {
      if (this.socket) {
        this.socket.close()
        this.socket = null
        this.isConnected = false
        this.stopPingInterval()
      }
    }
  
    /**
     * Envoie un message au serveur WebSocket
     * @param {Object} message - Message à envoyer
     */
    send(message) {
      if (this.socket && this.isConnected) {
        this.socket.send(JSON.stringify(message))
      } else {
        console.error('Cannot send message: WebSocket not connected')
      }
    }
  
    /**
     * Démarre l'envoi périodique de pings pour maintenir la connexion active
     */
    startPingInterval() {
      this.stopPingInterval() // S'assurer qu'il n'y a pas d'intervalle existant
      this.pingInterval = setInterval(() => {
        if (this.isConnected) {
          this.send({ type: 'ping' })
        }
      }, 30000) // Ping toutes les 30 secondes
    }
  
    /**
     * Arrête l'envoi périodique de pings
     */
    stopPingInterval() {
      if (this.pingInterval) {
        clearInterval(this.pingInterval)
        this.pingInterval = null
      }
    }
  
    /**
     * Gère les messages reçus du serveur WebSocket
     * @param {Object} message - Message reçu
     */
    handleMessage(message) {
      const { type, data } = message
      
      // Notifier tous les écouteurs pour ce type d'événement
      const eventListeners = this.listeners[type] || []
      eventListeners.forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`Error in WebSocket listener for '${type}':`, error)
        }
      })
    }
  
    /**
     * Ajoute un écouteur pour un type d'événement spécifique
     * @param {String} eventType - Type d'événement à écouter
     * @param {Function} callback - Fonction à appeler quand l'événement est reçu
     * @returns {Function} - Fonction pour supprimer l'écouteur
     */
    on(eventType, callback) {
      if (!this.listeners[eventType]) {
        this.listeners[eventType] = []
      }
      
      this.listeners[eventType].push(callback)
      
      // Retourner une fonction pour supprimer l'écouteur
      return () => {
        this.off(eventType, callback)
      }
    }
  
    /**
     * Supprime un écouteur pour un type d'événement spécifique
     * @param {String} eventType - Type d'événement
     * @param {Function} callback - Fonction à supprimer
     */
    off(eventType, callback) {
      if (!this.listeners[eventType]) return
      
      this.listeners[eventType] = this.listeners[eventType].filter(
        listener => listener !== callback
      )
    }
  }
  
  // Exporter une instance unique du service
  export const websocketService = new WebSocketService()