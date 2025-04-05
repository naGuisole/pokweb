<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { websocketService } from '@/services/websocket.service'

const props = defineProps({
  blindsStructure: {
    type: Array,
    required: true
  },
  initialLevel: {
    type: Number,
    default: 1
  },
  isAdmin: {
    type: Boolean,
    default: false
  },
  isPaused: {
    type: Boolean,
    default: false
  },
  tournamentId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['update:level', 'pause', 'resume', 'level-complete'])

// État du timer
const currentLevel = ref(props.initialLevel)
const timeRemaining = ref(0)
const totalDuration = ref(0)
const showConfirmation = ref(false)
const wsEventListeners = ref([])
const timerIsSynced = ref(false)
let timerInterval = null

// Computed properties
const formattedTime = computed(() => {
  const minutes = Math.floor(timeRemaining.value / 60)
  const seconds = Math.floor(timeRemaining.value % 60)
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

const currentBlinds = computed(() => {
  const level = props.blindsStructure.find(l => l.level === currentLevel.value)
  if (!level) return '-'
  return `${level.small_blind} / ${level.big_blind}`
})

const nextBlinds = computed(() => {
  const nextLevel = props.blindsStructure.find(l => l.level === currentLevel.value + 1)
  if (!nextLevel) return 'Fin du tournoi'
  return `${nextLevel.small_blind} / ${nextLevel.big_blind}`
})

const progressPercentage = computed(() => {
  if (totalDuration.value <= 0) return 0
  return ((totalDuration.value - timeRemaining.value) / totalDuration.value) * 100
})

const progressColor = computed(() => {
  if (timeRemaining.value <= 30) return 'error'
  if (timeRemaining.value <= 60) return 'warning'
  return 'primary'
})

// Setup des écouteurs WebSocket
const setupWebSocketListeners = () => {
  const removeListeners = []
  
  // État initial du tournoi
  removeListeners.push(
    websocketService.on('initial_state', (data) => {
      console.log('Timer: Initial state received', data);
      
      // Mettre à jour le niveau
      if (data.current_level !== undefined) {
        currentLevel.value = data.current_level || 1; // Utiliser 1 par défaut si 0
        console.log('Setting current level to:', currentLevel.value);
      }
      
      // Configurer le timer avec le temps restant
      if (data.seconds_remaining !== undefined && data.level_duration !== undefined) {
        timeRemaining.value = data.seconds_remaining;
        levelDuration.value = data.level_duration;
        timerIsSynced.value = true;
        
        // Démarrer ou arrêter le timer selon l'état de pause
        if (!data.paused && !props.isPaused) {
          startTimer();
        } else {
          stopTimer();
        }
      } else {
        // Si nous n'avons pas de données de timer, initialiser avec la durée du niveau actuel
        try {
          // S'assurer que blindsStructure.value est un tableau avant d'utiliser find
          if (Array.isArray(blindsStructure.value)) {
            const level = blindsStructure.value.find(l => l.level === currentLevel.value);
            if (level) {
              timeRemaining.value = level.duration * 60; // Convertir minutes en secondes
              levelDuration.value = level.duration * 60;
              console.log('Initializing timer with level duration:', level.duration, 'minutes');
            } else {
              // Fallback avec des valeurs par défaut
              timeRemaining.value = 20 * 60; // 20 minutes par défaut
              levelDuration.value = 20 * 60;
              console.log('No matching level found, using default 20 minutes');
            }
          } else {
            // Fallback si blindsStructure n'est pas un tableau
            timeRemaining.value = 20 * 60; // 20 minutes par défaut
            levelDuration.value = 20 * 60;
            console.log('blindsStructure is not an array, using default 20 minutes');
            console.log('blindsStructure:', blindsStructure.value);
          }
        } catch (error) {
          console.error('Error initializing timer from blinds structure:', error);
          timeRemaining.value = 20 * 60; // 20 minutes par défaut
          levelDuration.value = 20 * 60;
        }
        
        lastUpdateTime.value = Date.now();
        isPaused.value = data.paused || false;

        // Démarrer le timer si non en pause
        if (!isPaused.value) {
          startTimer();
          console.log('Timer started');
        } else {
          console.log('Tournament is paused, timer not started');
        }
      }
    })
  );
  
  // Changements de niveau
  removeListeners.push(
    websocketService.on('level_changed', (data) => {
      console.log('Timer: Level changed event', data)
      currentLevel.value = data.level
      
      if (data.seconds_remaining !== undefined && data.level_duration !== undefined) {
        timeRemaining.value = data.seconds_remaining
        totalDuration.value = data.level_duration
        timerIsSynced.value = true
        
        // Redémarrer le timer sauf si en pause
        if (!props.isPaused) {
          startTimer()
        }
      }
    })
  )
  
  // Changements d'état de pause
  removeListeners.push(
    websocketService.on('pause_status_changed', (data) => {
      console.log('Timer: Pause status changed event', data)
      
      if (data.seconds_remaining !== undefined) {
        timeRemaining.value = data.seconds_remaining
        timerIsSynced.value = true
      }
      
      if (data.paused) {
        stopTimer()
      } else if (!props.isPaused) {
        startTimer()
      }
    })
  )
  
  // Mises à jour périodiques du timer
  removeListeners.push(
    websocketService.on('timer_tick', (data) => {
      // Synchronisation précise du timer
      if (data.seconds_remaining !== undefined) {
        // Synchroniser seulement si l'écart est significatif (>2s) ou si pas encore synchronisé
        const diff = Math.abs(timeRemaining.value - data.seconds_remaining)
        if (!timerIsSynced.value || diff > 2) {
          timeRemaining.value = data.seconds_remaining
          timerIsSynced.value = true
          
          if (data.level_duration !== undefined) {
            totalDuration.value = data.level_duration
          }
        }
      }
    })
  )
  
  wsEventListeners.value = removeListeners
}

// Timer control
const startTimer = () => {
  stopTimer()
  
  if (props.isPaused) return
  
  timerInterval = setInterval(() => {
    if (timeRemaining.value > 0) {
      timeRemaining.value -= 1
      
      // Avertissement à 30 secondes
      if (timeRemaining.value === 30) {
        playWarningSound()
      }
      
      // Fin du niveau
      if (timeRemaining.value === 0) {
        emit('level-complete', currentLevel.value)
        playLevelEndSound()
        stopTimer() // Arrêter le timer à la fin du niveau
      }
    }
  }, 1000)
}

const stopTimer = () => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

const resetLevel = () => {
  if (!props.isAdmin) return
  
  const level = props.blindsStructure.find(l => l.level === currentLevel.value)
  if (level) {
    // Pour l'admin, envoyer une requête pour réinitialiser le timer côté serveur
    updateTimerOnServer(level.duration * 60)
  }
}

const togglePause = () => {
  emit(props.isPaused ? 'resume' : 'pause')
}

const confirmNextLevel = () => {
  showConfirmation.value = true
}

const nextLevel = () => {
  showConfirmation.value = false
  const nextLevelNumber = currentLevel.value + 1
  
  if (props.blindsStructure.some(l => l.level === nextLevelNumber)) {
    emit('update:level', nextLevelNumber)
  }
}

// API calls
const updateTimerOnServer = async (seconds) => {
  try {
    const response = await fetch(`/api/tournaments/${props.tournamentId}/timer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ seconds_remaining: seconds })
    })
    
    if (!response.ok) {
      throw new Error('Failed to update timer')
    }
  } catch (error) {
    console.error('Error updating timer:', error)
  }
}

// Sounds
const playWarningSound = () => {
  // À implémenter
}

const playLevelEndSound = () => {
  // À implémenter
}

// Lifecycle hooks
onMounted(() => {
  // Configurer les écouteurs WebSocket
  setupWebSocketListeners()
  
  // Configuration initiale du timer basée sur le niveau actuel
  const level = props.blindsStructure.find(l => l.level === currentLevel.value)
  if (level) {
    timeRemaining.value = level.duration * 60
    totalDuration.value = level.duration * 60
  }
  
  // Démarrer le timer si pas en pause
  if (!props.isPaused) {
    startTimer()
  }
})

onUnmounted(() => {
  stopTimer()
  
  // Nettoyer les écouteurs WebSocket
  wsEventListeners.value.forEach(removeListener => removeListener())
})

// Réagir aux changements de props
watch(() => props.initialLevel, (newLevel) => {
  if (newLevel !== currentLevel.value) {
    currentLevel.value = newLevel
  }
})

watch(() => props.isPaused, (isPaused) => {
  if (isPaused) {
    stopTimer()
  } else {
    startTimer()
  }
})
</script>

<template>
  <v-card>
    <v-card-title>Structure & Timer</v-card-title>
    
    <v-card-text>
      <div class="timer-container">
        <!-- Affichage du temps -->
        <div class="time-display">
          <div :class="['current-time', 'text-h2', { 'timer-warning': timeRemaining <= 60 }]">
            {{ formattedTime }}
          </div>
          <div class="text-h5">Niveau {{ currentLevel }}</div>
        </div>

        <!-- Blindes actuelles -->
        <div class="blinds-info">
          <div class="text-h6">Blindes actuelles</div>
          <div class="text-h4">{{ currentBlinds }}</div>
        </div>

        <!-- Prochaines blindes -->
        <div class="next-level-info">
          <div class="text-subtitle-1">Prochain niveau</div>
          <div class="text-h6">{{ nextBlinds }}</div>
        </div>

        <!-- Contrôles (visibles uniquement pour les admins) -->
        <div v-if="isAdmin" class="timer-controls">
          <v-btn
            icon="mdi-refresh"
            color="warning"
            variant="tonal"
            class="mx-2"
            @click="resetLevel"
          ></v-btn>

          <v-btn
            :icon="isPaused ? 'mdi-play' : 'mdi-pause'"
            color="primary"
            size="large"
            class="mx-2"
            @click="togglePause"
          ></v-btn>

          <v-btn
            icon="mdi-skip-next"
            color="warning"
            variant="tonal"
            class="mx-2"
            @click="confirmNextLevel"
          ></v-btn>
        </div>
      </div>

      <!-- Structure des blindes -->
      <v-table class="mt-4 blinds-table">
        <thead>
          <tr>
            <th>Niveau</th>
            <th>Small Blind</th>
            <th>Big Blind</th>
            <th>Durée</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="level in blindsStructure" 
            :key="level.level"
            :class="{ 'current-level': level.level === currentLevel }"
          >
            <td>{{ level.level }}</td>
            <td>{{ level.small_blind }}</td>
            <td>{{ level.big_blind }}</td>
            <td>{{ level.duration }}min</td>
          </tr>
        </tbody>
      </v-table>

      <!-- Barre de progression -->
      <v-progress-linear
        v-model="progressPercentage"
        :color="progressColor"
        height="8"
        class="mt-4"
      ></v-progress-linear>
    </v-card-text>

    <!-- Dialogue de confirmation de changement de niveau -->
    <v-dialog v-model="showConfirmation" max-width="300">
      <v-card>
        <v-card-title>Confirmer le changement</v-card-title>
        <v-card-text>
          Voulez-vous vraiment passer au niveau suivant ?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey-lighten-1"
            variant="text"
            @click="showConfirmation = false"
          >
            Annuler
          </v-btn>
          <v-btn
            color="primary"
            @click="nextLevel"
          >
            Confirmer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<style scoped>
.timer-container {
  text-align: center;
  padding: 20px;
}

.time-display {
  margin-bottom: 20px;
}

.current-time {
  font-family: monospace;
  font-weight: bold;
}

.blinds-info {
  margin-bottom: 16px;
}

.next-level-info {
  margin-bottom: 24px;
  opacity: 0.8;
}

.timer-controls {
  margin-bottom: 20px;
}

.blinds-table {
  margin-top: 20px;
}

.current-level {
  background-color: rgba(var(--v-theme-primary), 0.1);
}

.timer-warning {
  animation: pulse 1s infinite;
  color: #FF5252;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
</style>