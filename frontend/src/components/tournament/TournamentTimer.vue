<!-- src/components/tournament/TournamentTimer.vue -->
<template>
    <v-card>
      <v-card-title>Structure & Timer</v-card-title>
      
      <v-card-text>
        <div class="timer-container">
          <!-- Affichage du temps -->
          <div class="time-display">
            <div class="current-time text-h2">{{ formattedTime }}</div>
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
  
          <!-- Contrôles -->
          <div class="timer-controls">
            <v-btn
              icon="mdi-refresh"
              color="warning"
              variant="tonal"
              class="mx-2"
              @click="resetLevel"
              :disabled="!isAdmin"
            ></v-btn>
  
            <v-btn
              :icon="isPaused ? 'mdi-play' : 'mdi-pause'"
              color="primary"
              size="large"
              class="mx-2"
              @click="togglePause"
              :disabled="!isAdmin"
            ></v-btn>
  
            <v-btn
              icon="mdi-skip-next"
              color="warning"
              variant="tonal"
              class="mx-2"
              @click="confirmNextLevel"
              :disabled="!isAdmin"
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
  
      <!-- Dialogue de confirmation -->
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
  
  <script setup>
  import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
  
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
    }
  })
  
  const emit = defineEmits(['update:level', 'pause', 'resume', 'level-complete'])
  
  // État du timer
  const currentLevel = ref(props.initialLevel)
  const timeRemaining = ref(0)
  const showConfirmation = ref(false)
  let timerInterval = null
  
  // Calcul du temps restant initial pour le niveau en cours
  const initializeLevel = () => {
    const level = props.blindsStructure.find(l => l.level === currentLevel.value)
    if (level) {
      timeRemaining.value = level.duration * 60
    }
  }
  
  // Computed properties
  const formattedTime = computed(() => {
    const minutes = Math.floor(timeRemaining.value / 60)
    const seconds = timeRemaining.value % 60
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
    const level = props.blindsStructure.find(l => l.level === currentLevel.value)
    if (!level) return 0
    const totalSeconds = level.duration * 60
    return ((totalSeconds - timeRemaining.value) / totalSeconds) * 100
  })
  
  const progressColor = computed(() => {
    if (timeRemaining.value <= 30) return 'error'
    if (timeRemaining.value <= 60) return 'warning'
    return 'primary'
  })
  
  // Timer control
  const startTimer = () => {
    stopTimer()
    timerInterval = setInterval(() => {
      if (!props.isPaused && timeRemaining.value > 0) {
        timeRemaining.value--
        
        // Son d'avertissement à 30 secondes
        if (timeRemaining.value === 30) {
          playWarningSound()
        }
        
        // Fin du niveau
        if (timeRemaining.value === 0) {
          emit('level-complete', currentLevel.value)
          playLevelEndSound()
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
    initializeLevel()
  }
  
  const togglePause = () => {
    emit(props.isPaused ? 'resume' : 'pause')
  }
  
  const confirmNextLevel = () => {
    showConfirmation.value = true
  }
  
  const nextLevel = () => {
    showConfirmation.value = false
    const nextLevel = currentLevel.value + 1
    if (props.blindsStructure.some(l => l.level === nextLevel)) {
      currentLevel.value = nextLevel
      emit('update:level', nextLevel)
      initializeLevel()
      playLevelChangeSound()
    }
  }
  
  // Sons du tournoi
  const playWarningSound = () => {
    // Implémentation du son d'avertissement
  }
  
  const playLevelEndSound = () => {
    // Implémentation du son de fin de niveau
  }
  
  const playLevelChangeSound = () => {
    // Implémentation du son de changement de niveau
  }
  
  // Lifecycle hooks
  onMounted(() => {
    initializeLevel()
    startTimer()
  })
  
  onUnmounted(() => {
    stopTimer()
  })
  
  // Watch
  watch(() => props.initialLevel, (newLevel) => {
    currentLevel.value = newLevel
    initializeLevel()
  })
  </script>
  
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
  
  .time-warning {
    animation: pulse 1s infinite;
  }
  
  @keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
  }
  </style>