<!-- src/views/TournamentDetailView.vue -->
<template>
  <v-container fluid>
    <!-- Affichage du chargement -->
    <v-row v-if="loading">
      <v-col cols="12" class="text-center">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
        <div class="mt-2">Chargement du tournoi...</div>
      </v-col>
    </v-row>

    <template v-else-if="tournament">
      <!-- En-tête du tournoi -->
      <v-card class="mb-4">
        <v-card-title class="d-flex align-center">
          <span class="text-h5">{{ tournament.name }}</span>
          <v-chip
            :color="getStatusColor(tournament.status)"
            class="ml-4"
          >
            {{ getStatusLabel(tournament.status) }}
          </v-chip>

          <v-spacer></v-spacer>

          <!-- Actions administrateur -->
          <template v-if="isAdmin">
            <v-btn
              v-if="tournament.status === 'PLANNED'"
              color="primary"
              prepend-icon="mdi-play"
              @click="startTournament"
            >
              Démarrer
            </v-btn>

            <template v-if="tournament.status === 'IN_PROGRESS'">
              <v-btn
                color="warning"
                :prepend-icon="isPaused ? 'mdi-play' : 'mdi-pause'"
                class="mr-2"
                @click="togglePause"
              >
                {{ isPaused ? 'Reprendre' : 'Pause' }}
              </v-btn>
            </template>
          </template>
        </v-card-title>

        <v-card-text>
          <v-row>
            <v-col cols="12" sm="6" md="3">
              <div class="text-caption">Date</div>
              <div class="text-body-1">{{ formatDate(tournament.date) }}</div>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <div class="text-caption">Type</div>
              <div class="text-body-1">{{ tournament.tournament_type }}</div>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <div class="text-caption">Buy-in</div>
              <div class="text-body-1">{{ tournament.buy_in }}€</div>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <div class="text-caption">Prize Pool</div>
              <div class="text-body-1">{{ tournament.prize_pool || 0 }}€</div>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Tables et Timer -->
      <v-row>
        <!-- Tables de jeu -->
        <v-col 
          :cols="12" 
          :md="tournament.status === 'IN_PROGRESS' ? 8 : 12"
        >
          <v-row>
            <v-col 
              v-for="(tableIndex, index) in tables"
              :key="index"
              :cols="12"
              :md="tables.length > 1 ? 6 : 12"
            >
              <tournament-table
                :players="getPlayersAtTable(tableIndex)"
                :table-number="index + 1"
                :dealer-position="dealerPosition"
                :is-active="tournament.status === 'IN_PROGRESS'"
                @position-click="handlePlayerPosition"
              />
            </v-col>
          </v-row>
        </v-col>

        <!-- Timer et structure en cours de partie -->
        <v-col
          v-if="tournament.status === 'IN_PROGRESS' && tournament.configuration"
          cols="12"
          md="4"
        >
          <tournament-timer
            :blinds-structure="tournament.configuration.blinds_structure || []"
            :initial-level="currentLevel"
            :is-admin="isAdmin"
            :is-paused="isPaused"
            @update:level="handleLevelChange"
            @pause="handlePause"
            @resume="handleResume"
            @level-complete="handleLevelComplete"
          />
        </v-col>
      </v-row>

      <!-- Liste des joueurs -->
      <v-card class="mt-4">
        <v-card-title class="d-flex align-center">
          Joueurs
          <v-spacer></v-spacer>
          <v-btn
            v-if="canRebalanceTables"
            color="primary"
            prepend-icon="mdi-table-refresh"
            @click="rebalanceTables"
          >
            Rééquilibrer les tables
          </v-btn>
        </v-card-title>

        <v-card-text>
          <div v-if="activePlayers.length === 0" class="text-center pa-4">
            Aucun joueur actif pour ce tournoi.
          </div>
          <v-table v-else>
            <thead>
              <tr>
                <th>Joueur</th>
                <th>Position</th>
                <th>Stack</th>
                <th>Rebuys</th>
                <th v-if="isAdmin">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="player in activePlayers" :key="player.id">
                <td class="d-flex align-center">
                  <v-avatar size="32" class="mr-2">
                    <v-img
                      v-if="player.profile_image_path"
                      :src="player.profile_image_path"
                    ></v-img>
                    <v-icon v-else>mdi-account</v-icon>
                  </v-avatar>
                  {{ player.username }}
                </td>
                <td>Table {{ (player.table || 0) + 1 }}, Place {{ (player.position || 0) + 1 }}</td>
                <td>{{ formatChips(player.current_chips) }}</td>
                <td>{{ player.num_rebuys || 0 }}</td>
                <td v-if="isAdmin">
                  <v-btn-group>
                    <v-btn
                      icon
                      size="small"
                      color="success"
                      :disabled="!canRebuy"
                      @click="handleRebuy(player)"
                    >
                      <v-icon>mdi-refresh</v-icon>
                    </v-btn>
                    <v-btn
                      icon
                      size="small"
                      color="error"
                      @click="handleElimination(player)"
                    >
                      <v-icon>mdi-close</v-icon>
                    </v-btn>
                  </v-btn-group>
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card-text>
      </v-card>

      <!-- Joueurs éliminés -->
      <v-card v-if="eliminatedPlayers.length > 0" class="mt-4">
        <v-card-title>Joueurs éliminés</v-card-title>
        <v-card-text>
          <v-table>
            <thead>
              <tr>
                <th>Position</th>
                <th>Joueur</th>
                <th>Gain</th>
                <th>Rebuys</th>
                <th>Éliminé à</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="player in eliminatedPlayers" :key="player.id">
                <td>{{ player.final_position || '-' }}</td>
                <td class="d-flex align-center">
                  <v-avatar size="32" class="mr-2">
                    <v-img
                      v-if="player.profile_image_path"
                      :src="player.profile_image_path"
                      alt="Avatar"
                    ></v-img>
                    <v-icon v-else size="32">mdi-account</v-icon>
                  </v-avatar>
                  {{ player.username }}
                </td>
                <td>{{ formatMoney(player.prize_won) }}</td>
                <td>{{ player.num_rebuys || 0 }}</td>
                <td>{{ formatTime(player.elimination_time) }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-card-text>
      </v-card>
    </template>

    <!-- Message si le tournoi n'existe pas -->
    <v-row v-else>
      <v-col cols="12">
        <v-alert
          type="error"
          text="Tournoi non trouvé ou erreur lors du chargement"
        ></v-alert>
      </v-col>
    </v-row>

    <!-- Dialogues pour les actions -->
    <tournament-dialogs
      ref="dialogsRef"
      :max-position="activePlayers.length"
      :prize-pool="tournament?.prize_pool || 0"
      :is-japt="tournament?.tournament_type === 'JAPT'"
      @rebuy-confirmed="confirmRebuy"
      @elimination-confirmed="confirmElimination"
    />
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTournamentStore } from '@/stores/tournament'
import { useAuthStore } from '@/stores/auth'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'

import TournamentTable from '@/components/tournament/TournamentTable.vue'
import TournamentTimer from '@/components/tournament/TournamentTimer.vue'
import TournamentDialogs from '@/components/tournament/TournamentDialogs.vue'

const route = useRoute()
const router = useRouter()
const tournamentStore = useTournamentStore()
const authStore = useAuthStore()

// Refs
const dialogsRef = ref(null)
const currentLevel = ref(1)
const dealerPosition = ref(0)
const isPaused = ref(false)
const updateInterval = ref(null)
const loading = ref(true)

// Computed
const tournament = computed(() => tournamentStore.currentTournament)
const isAdmin = computed(() => {
  if (!tournament.value || !authStore.user) return false
  return tournament.value.admin_id === authStore.user.id
})

const tables = computed(() => {
  if (!tournament.value || !tournament.value.num_tables) return []
  return Array.from({ length: tournament.value.num_tables }, (_, i) => i)
})

const activePlayers = computed(() => {
  // Vérifier si les données existent avant de les retourner
  const players = tournamentStore.getActivePlayers
  return Array.isArray(players) ? players : []
})

const eliminatedPlayers = computed(() => {
  // Vérifier si les données existent avant de les retourner
  const players = tournamentStore.getEliminatedPlayers
  return Array.isArray(players) ? players : []
})

const canRebalanceTables = computed(() => {
  if (!tournament.value || !isAdmin.value) return false
  return (
    tournament.value.status === 'IN_PROGRESS' &&
    tournament.value.num_tables > 1 &&
    activePlayers.value.length > (tournament.value.players_per_table || 0)
  )
})

const canRebuy = computed(() => {
  if (!tournament.value || !tournament.value.configuration) return false
  return currentLevel.value <= (tournament.value.configuration.rebuy_levels || 0)
})

// Méthodes utilitaires
const formatDate = (date) => {
  if (!date) return '-'
  try {
    return format(new Date(date), 'PPP à HH:mm', { locale: fr })
  } catch (e) {
    console.error('Erreur formatDate:', e)
    return '-'
  }
}

const formatTime = (time) => {
  if (!time) return '-'
  try {
    return format(new Date(time), 'HH:mm')
  } catch (e) {
    console.error('Erreur formatTime:', e)
    return '-'
  }
}

const formatChips = (chips) => {
  if (!chips && chips !== 0) return '-'
  return new Intl.NumberFormat('fr-FR').format(chips)
}

const formatMoney = (amount) => {
  if (!amount && amount !== 0) return '-'
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(amount)
}

const getStatusColor = (status) => {
  const colors = {
    PLANNED: 'success',
    IN_PROGRESS: 'primary',
    COMPLETED: 'grey'
  }
  return colors[status] || 'grey'
}

const getStatusLabel = (status) => {
  const labels = {
    PLANNED: 'Planifié',
    IN_PROGRESS: 'En cours',
    COMPLETED: 'Terminé'
  }
  return labels[status] || status
}

const getPlayersAtTable = (tableIndex) => {
  if (!activePlayers.value || activePlayers.value.length === 0) return []
  return activePlayers.value.filter(player => (player.table || 0) === tableIndex)
}

// Actions du tournoi
const startTournament = async () => {
  if (!tournament.value) return
  
  try {
    await tournamentStore.startTournament(tournament.value.id)
    startPeriodicUpdate()
  } catch (error) {
    console.error('Erreur lors du démarrage du tournoi:', error)
  }
}

const togglePause = async () => {
  if (!tournament.value) return
  
  try {
    if (isPaused.value) {
      await tournamentStore.resumeTournament(tournament.value.id)
      isPaused.value = false
    } else {
      await tournamentStore.pauseTournament(tournament.value.id)
      isPaused.value = true
    }
  } catch (error) {
    console.error('Erreur lors de la pause/reprise du tournoi:', error)
  }
}

const handlePause = async () => {
  if (!tournament.value) return
  await tournamentStore.pauseTournament(tournament.value.id)
  isPaused.value = true
}

const handleResume = async () => {
  if (!tournament.value) return
  await tournamentStore.resumeTournament(tournament.value.id)
  isPaused.value = false
}

const handleLevelComplete = (level) => {
  // Gérer la fin du niveau
  console.log(`Fin du niveau ${level}`)
}

const handlePlayerPosition = async ({ position, tableNumber, currentPlayer }) => {
  if (!tournament.value || !isAdmin.value || tournament.value.status !== 'IN_PROGRESS') return

  try {
    await tournamentStore.updatePlayerPosition(tournament.value.id, {
      position,
      tableNumber,
      playerId: currentPlayer?.id
    })
    await refreshTournament()
  } catch (error) {
    console.error('Erreur lors de la mise à jour de la position:', error)
  }
}

const handleLevelChange = async (newLevel) => {
  if (!tournament.value) return
  
  try {
    await tournamentStore.updateTournamentLevel(tournament.value.id, newLevel)
    currentLevel.value = newLevel
  } catch (error) {
    console.error('Erreur lors du changement de niveau:', error)
  }
}

const rebalanceTables = async () => {
  if (!tournament.value) return
  
  try {
    await tournamentStore.rebalanceTables(tournament.value.id)
    await refreshTournament()
  } catch (error) {
    console.error('Erreur lors du rééquilibrage des tables:', error)
  }
}

// Gestion des joueurs
const handleRebuy = (player) => {
  if (!dialogsRef.value) return
  dialogsRef.value.showRebuyDialog(player)
}

const handleElimination = (player) => {
  if (!dialogsRef.value) return
  dialogsRef.value.showEliminationDialog(player)
}

const confirmRebuy = async (data) => {
  if (!tournament.value) return
  
  try {
    await tournamentStore.processRebuy(tournament.value.id, data)
    await refreshTournament()
  } catch (error) {
    console.error('Erreur lors du rebuy:', error)
  }
}

const confirmElimination = async (data) => {
  if (!tournament.value) return
  
  try {
    await tournamentStore.eliminatePlayer(tournament.value.id, data)
    await refreshTournament()
  } catch (error) {
    console.error('Erreur lors de l\'élimination:', error)
  }
}

// Mise à jour périodique
const startPeriodicUpdate = () => {
  stopPeriodicUpdate()
  updateInterval.value = setInterval(refreshTournament, 5000)
}

const stopPeriodicUpdate = () => {
  if (updateInterval.value) {
    clearInterval(updateInterval.value)
    updateInterval.value = null
  }
}

const refreshTournament = async () => {
  const tournamentId = parseInt(route.params.id)
  if (isNaN(tournamentId)) return
  
  try {
    await tournamentStore.fetchTournament(tournamentId)
    
    // Mettre à jour d'autres informations
    if (tournament.value?.status === 'IN_PROGRESS') {
      currentLevel.value = tournament.value.current_level || 1
      isPaused.value = tournament.value.paused || false
    }
  } catch (error) {
    console.error('Erreur lors du rafraîchissement du tournoi:', error)
  }
}

// Lifecycle hooks
onMounted(async () => {
  loading.value = true
  try {
    const tournamentId = parseInt(route.params.id)
    if (isNaN(tournamentId)) {
      console.error('ID de tournoi invalide')
      return
    }
    
    await refreshTournament()
    
    if (tournament.value?.status === 'IN_PROGRESS') {
      currentLevel.value = tournament.value.current_level || 1
      isPaused.value = tournament.value.paused || false
      startPeriodicUpdate()
    }
  } catch (error) {
    console.error('Erreur lors du chargement initial:', error)
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  stopPeriodicUpdate()
})

// Surveiller les changements d'ID de tournoi dans l'URL
watch(() => route.params.id, async (newId) => {
  if (newId) {
    loading.value = true
    try {
      await refreshTournament()
    } finally {
      loading.value = false
    }
  }
})
</script>

<style scoped>
.table-container {
  margin-bottom: 2rem;
}

.player-info {
  display: flex;
  align-items: center;
}

.eliminated {
  opacity: 0.6;
}
</style>