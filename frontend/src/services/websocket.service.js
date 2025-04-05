// src/services/websocket.service.js
class WebSocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10; // Augmenté pour plus de résilience
    this.reconnectInterval = 3000; // 3 secondes
    this.baseReconnectInterval = 1000; // Intervalle de base pour le backoff exponentiel
    this.listeners = {};
    this.pingInterval = null;
    this.connectionStatusListeners = []; // Nouveaux listeners pour l'état de connexion
  }

  /**
   * Connecte au serveur WebSocket pour un tournoi spécifique
   * @param {Number} tournamentId - ID du tournoi à suivre
   * @returns {Promise} - Résout quand la connexion est établie
   */
  connect(tournamentId) {
    return new Promise((resolve, reject) => {
      if (this.socket && this.isConnected) {
        this.disconnect();
      }

      const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
      const wsUrl = `${protocol}://${window.location.host}/ws/tournaments/${tournamentId}`;

      console.log(`Connecting to WebSocket: ${wsUrl}`);
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        console.log('WebSocket connection established');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.startPingInterval();
        this.notifyConnectionStatusChange(true);
        resolve();
      };

      this.socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.socket.onclose = (event) => {
        this.isConnected = false;
        this.stopPingInterval();
        this.notifyConnectionStatusChange(false);
        console.log(`WebSocket connection closed: ${event.code} - ${event.reason}`);
        
        // Nouvelle logique de backoff exponentiel avec jitter
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          
          // Calculer l'intervalle avec backoff exponentiel et jitter
          const backoffMs = Math.min(
            this.baseReconnectInterval * Math.pow(1.5, this.reconnectAttempts),
            30000 // Max 30 secondes
          );
          const jitter = Math.random() * 0.3 + 0.85; // 0.85-1.15
          const reconnectDelay = Math.floor(backoffMs * jitter);
          
          console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${reconnectDelay}ms...`);
          setTimeout(() => this.connect(tournamentId), reconnectDelay);
        } else {
          console.log('Max reconnect attempts reached');
          reject(new Error('Failed to connect to tournament updates'));
        }
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    });
  }

  /**
   * S'abonne aux changements d'état de connexion
   * @param {Function} callback - Fonction appelée lors des changements
   */
  onConnectionStatusChange(callback) {
    this.connectionStatusListeners.push(callback);
    // Notifier immédiatement de l'état actuel
    callback(this.isConnected);
    
    // Retourner une fonction pour se désabonner
    return () => {
      this.connectionStatusListeners = this.connectionStatusListeners.filter(
        listener => listener !== callback
      );
    };
  }

  /**
   * Notifie les listeners des changements d'état de connexion
   * @param {Boolean} connected - État de connexion
   */
  notifyConnectionStatusChange(connected) {
    this.connectionStatusListeners.forEach(callback => {
      try {
        callback(connected);
      } catch (error) {
        console.error('Error in connection status listener:', error);
      }
    });
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
      console.log('WebSocket disconnected manually')
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