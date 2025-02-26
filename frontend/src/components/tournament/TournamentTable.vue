<!-- src/components/tournament/TournamentTable.vue -->
<template>
    <div class="table-container">
      <!-- Table de poker -->
      <div class="poker-table">
        <!-- Bouton dealer -->
        <div 
          v-if="showDealer"
          class="dealer-button"
          :style="getDealerPosition()"
        >
          D
        </div>
  
        <!-- Positions des joueurs -->
        <div
          v-for="position in maxPlayers"
          :key="position"
          :class="[
            'player-position',
            `position-${position - 1}`,
            { 
              'occupied': isPositionOccupied(position - 1),
              'active': isPlayerActive(position - 1)
            }
          ]"
          @click="handlePositionClick(position - 1)"
        >
          <template v-if="getPlayerAtPosition(position - 1)">
            <v-avatar size="48" class="player-avatar">
              <v-img
                v-if="getPlayerAtPosition(position - 1).profile_image_path"
                :src="getPlayerAtPosition(position - 1).profile_image_path"
                alt="Avatar"
              ></v-img>
              <v-icon v-else size="32">mdi-account</v-icon>
            </v-avatar>
            <div class="player-info">
              <div class="player-name">
                {{ getPlayerAtPosition(position - 1).username }}
              </div>
              <div class="player-stack" v-if="showStacks">
                {{ formatChips(getPlayerAtPosition(position - 1).current_chips) }}
              </div>
            </div>
          </template>
          <template v-else>
            <div class="empty-position">
              Siège {{ position }}
            </div>
          </template>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue'
  
  const props = defineProps({
    players: {
      type: Array,
      required: true
    },
    maxPlayers: {
      type: Number,
      default: 10
    },
    dealerPosition: {
      type: Number,
      default: null
    },
    showDealer: {
      type: Boolean,
      default: true
    },
    showStacks: {
      type: Boolean,
      default: true
    },
    tableNumber: {
      type: Number,
      required: true
    },
    isActive: {
      type: Boolean,
      default: true
    }
  })
  
  const emit = defineEmits(['position-click'])
  
  // Méthodes utilitaires
  const getPlayerAtPosition = (position) => {
    return props.players.find(player => player.position === position)
  }
  
  const isPositionOccupied = (position) => {
    return !!getPlayerAtPosition(position)
  }
  
  const isPlayerActive = (position) => {
    const player = getPlayerAtPosition(position)
    return player && player.is_active
  }
  
  const formatChips = (chips) => {
    if (!chips && chips !== 0) return ''
    return new Intl.NumberFormat('fr-FR').format(chips)
  }
  
  // Position du bouton dealer
  const getDealerPosition = () => {
    if (props.dealerPosition === null) return {}
    
    const angle = (360 / props.maxPlayers) * props.dealerPosition
    const radius = 160 // Rayon du cercle en pixels
    const centerX = 200 // Centre X de la table
    const centerY = 200 // Centre Y de la table
    
    const x = centerX + radius * Math.cos((angle - 90) * Math.PI / 180)
    const y = centerY + radius * Math.sin((angle - 90) * Math.PI / 180)
    
    return {
      left: `${x}px`,
      top: `${y}px`
    }
  }
  
  // Gestion des clics
  const handlePositionClick = (position) => {
    emit('position-click', {
      position,
      tableNumber: props.tableNumber,
      currentPlayer: getPlayerAtPosition(position)
    })
  }
  </script>
  
  <style scoped>
  .table-container {
    position: relative;
    width: 100%;
    padding-top: 100%; /* Aspect ratio 1:1 */
  }
  
  .poker-table {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 50%;
    background: #0f5c2e;
    border: 15px solid #8B4513;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  }
  
  .player-position {
    position: absolute;
    width: 80px;
    height: 80px;
    transform: translate(-50%, -50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .player-position:hover {
    transform: translate(-50%, -50%) scale(1.1);
  }
  
  .dealer-button {
    position: absolute;
    width: 24px;
    height: 24px;
    background: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 14px;
    transform: translate(-50%, -50%);
    border: 2px solid #333;
    z-index: 2;
  }
  
  .player-info {
    text-align: center;
    color: white;
    margin-top: 4px;
  }
  
  .player-name {
    font-size: 0.9rem;
    font-weight: bold;
    max-width: 100px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .player-stack {
    font-size: 0.8rem;
    color: #90EE90;
  }
  
  .empty-position {
    color: rgba(255, 255, 255, 0.5);
    font-size: 0.8rem;
  }
  
  .occupied {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 50%;
    padding: 8px;
  }
  
  .active {
    box-shadow: 0 0 15px rgba(144, 238, 144, 0.5);
  }
  
  /* Positions autour de la table */
  .position-0 { top: 10%; left: 50%; }
  .position-1 { top: 20%; left: 80%; }
  .position-2 { top: 50%; left: 90%; }
  .position-3 { top: 80%; left: 80%; }
  .position-4 { top: 90%; left: 50%; }
  .position-5 { top: 80%; left: 20%; }
  .position-6 { top: 50%; left: 10%; }
  .position-7 { top: 20%; left: 20%; }
  .position-8 { top: 15%; left: 35%; }
  .position-9 { top: 15%; left: 65%; }
  </style>