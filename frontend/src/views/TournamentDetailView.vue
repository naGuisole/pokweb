<!-- src/views/TournamentDetailView.vue -->
<template>
  <v-container fluid>
    <!-- En-tête du tournoi -->
    <v-card class="mb-4">
      <v-card-title class="d-flex align-center">
        <span class="text-h5">{{ tournament?.name }}</span>
        <v-chip
          :color="getStatusColor(tournament?.status)"
          class="ml-4"
        >
          {{ getStatusLabel(tournament?.status) }}
        </v-chip>

        <v-spacer></v-spacer>

        <!-- Actions administrateur -->
        <template v-if="isAdmin">
          <v-btn
            v-if="tournament?.status === 'PLANNED'"
            color="primary"
            prepend-icon="mdi-play"
            @click="startTournament"
          >
            Démarrer
          </v-btn>

          <template v-if="tournament?.status === 'IN_PROGRESS'">
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
            <div class="text-body-1">{{ formatDate(tournament?.date) }}</div>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <div class="text-caption">Type</div>
            <div class="text-body-1">{{ tournament?.tournament_type }}</div>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <div class="text-caption">Buy-in</div>
            <div class="text-body-1">{{ tournament?.buy_in }}€</div>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <div class="text-caption">Prize Pool</div>
            <div class="text-body-1">{{ tournament?.prize_pool }}€</div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Tables et Timer -->
    <v-row>
      <!-- Tables de jeu -->
      <v-col 
        :cols="12" 
        :md="tournament?.status === 'IN_PROGRESS' ? 8 : 12"
      >
        <v-row>
          <v-col 
            v-for="(table, index) in tables"
            :key="index"
            :cols="12"
            :md="tournament?.num_tables > 1 ? 6 : 12"
          >
            <tournament-table
              :players="getPlayersAtTable(index)"
              :table-number="index + 1"
              :dealer-position="dealerPosition"
              :is-active="tournament?.status === 'IN_PROGRESS'"
              @position-click="handlePlayerPosition"
            />
          </v-col>
        </v-row>
      </v-col>

      <!-- Timer et structure en cours de partie -->
      <v-col
        v-if="tournament?.status === 'IN_PROGRESS'"
        cols="12"
        md="4"
      >
        <tournament-timer
          :blinds-structure="tournament?.configuration?.blinds_structure"
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
        <v-table>
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
              <td>Table {{ player.table + 1 }}, Place {{ player.position + 1 }}</td>
              <td>{{ formatChips(player.current_chips) }}</td>
              <td>{{ player.num_rebuys }}</td>
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
              <td>{{ player.final_position }}</td>
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
              <td>{{ formatMoney(player.prize_won) }}</td>
              <td>{{ player.num_rebuys }}</td>
              <td>{{ formatTime(player.elimination_time) }}</td>
            </tr>
          </tbody>
        </v-table>
      </v-card-text>
    </v-card>

    <!-- Dialogues pour les actions -->
    <tournament-dialogs
      ref="dialogsRef"
      :max-position="activePlayers.length"
      :prize-pool="tournament?.prize_pool"
      :is-japt="tournament?.tournament_type === 'JAPT'"
      @rebuy-confirmed="confirmRebuy"
      @elimination-confirmed="confirmElimination"
    />
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
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

// Computed
const tournament = computed(() => tournamentStore.currentTournament)
const isAdmin = computed(() => tournament.value?.admin_id === authStore.user?.id)

const tables = computed(() => {
  if (!tournament.value) return []
  return Array.from({ length: tournament.value.num_tables }, (_, i) => i)
})

const activePlayers = computed(() => tournamentStore.getActivePlayers)
const eliminatedPlayers = computed(() => tournamentStore.getEliminatedPlayers)

const canRebalanceTables = computed(() => {
  return isAdmin.value &&
         tournament.value?.status === 'IN_PROGRESS' &&
         tournament.value?.num_tables > 1 &&
         activePlayers.value.length > tournament.value?.players_per_table
})

const canRebuy = computed(() => {
  if (!tournament.value?.configuration) return false
  return currentLevel.value <= tournament.value.configuration.rebuy_levels
})

// Méthodes utilitaires
const formatDate = (date) => {
  if (!date) return ''
  return format(new Date(date), 'PPP à HH:mm', { locale: fr })
}

const formatTime = (time) => {
  if (!time) return ''
  return format(new Date(time), 'HH:mm')
}

const formatChips = (chips) => {
  if (!chips && chips !== 0) return ''
  return new Intl.NumberFormat('fr-FR').format(chips)
}

const formatMoney = (amount) => {
  if (!amount && amount !== 0) return ''
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
  return activePlayers.value.filter(player => player.table === tableIndex)
}

// Actions du tournoi
const startTournament = async () => {
  try {
    await tournamentStore.startTournament(tournament.value.id)
    startPeriodicUpdate()
  } catch (error) {
    console.error('Erreur lors du démarrage du tournoi:', error)
  }
}

const togglePause = async () => {
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

const handlePlayerPosition = async ({ position, tableNumber, currentPlayer }) => {
  if (!isAdmin.value || tournament.value?.status !== 'IN_PROGRESS') return

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
  try {
    await tournamentStore.updateTournamentLevel(tournament.value.id, newLevel)
    currentLevel.value = newLevel
  } catch (error) {
    console.error('Erreur lors du changement de niveau:', error)
  }
}

const rebalanceTables = async () => {
  try {
    await tournamentStore.rebalanceTables(tournament.value.id)
    await refreshTournament()
  } catch (error) {
    console.error('Erreur lors du rééquilibrage des tables:', error)
  }
}

// Gestion des joueurs
const handleRebuy = (player) => {
  dialogsRef.value?.showRebuyDialog(player)
}

const handleElimination = (player) => {
  dialogsRef.value?.showEliminationDialog(player)
}

const confirmRebuy = async (data) => {
  try {
    await tournamentStore.processRebuy(tournament.value.id, data)
    await refreshTournament()
  } catch (error) {
    console.error('Erreur lors du rebuy:', error)
  }
}

const confirmElimination = async (data) => {
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
  await tournamentStore.fetchTournament(tournamentId)
}

// Lifecycle hooks
onMounted(async () => {
  const tournamentId = parseInt(route.params.id)
  await refreshTournament()
  
  if (tournament.value?.status === 'IN_PROGRESS') {
    currentLevel.value = tournament.value.current_level
    isPaused.value = tournament.value.paused
    startPeriodicUpdate()
  }
})

onUnmounted(() => {
  stopPeriodicUpdate()
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