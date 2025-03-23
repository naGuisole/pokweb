<!-- src/views/TournamentDetailView.vue -->
<template>
  <v-container fluid class="tournament-detail-container pa-0">
    <!-- Affichage du chargement -->
    <v-overlay :model-value="loading" class="align-center justify-center">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
    </v-overlay>

    <template v-if="tournament">
      <!-- En-tête du tournoi - Toujours visible -->
      <v-card class="mb-4 header-card">
        <v-card-text class="pa-4">
          <v-row align="center">
            <v-col cols="12" md="6">
              <h1 class="text-h4 font-weight-bold mb-1">{{ tournament.name }}</h1>
              <div class="d-flex align-center flex-wrap mb-1">
                <v-icon size="small" class="mr-2">mdi-calendar</v-icon>
                <span class="mr-4">{{ formatDate(tournament.date) }}</span>
                <v-chip
                  :color="getStatusColor(tournament.status)"
                  class="mr-2"
                  size="small"
                >
                  {{ getStatusLabel(tournament.status) }}
                </v-chip>
                <v-chip
                  size="small"
                  color="blue"
                >
                  {{ tournament.tournament_type }}
                </v-chip>
              </div>
            </v-col>
            <v-col cols="12" md="6">
              <v-row>
                <v-col cols="6" md="3">
                  <div class="text-subtitle-2">Joueurs</div>
                  <div class="text-h6">{{ activePlayers.length }} / {{ tournament.max_players }}</div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-subtitle-2">Rebuys</div>
                  <div class="text-h6">{{ tournament.total_rebuys || 0 }}</div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-subtitle-2">Buy-in</div>
                  <div class="text-h6">{{ formatMoney(tournament.buy_in) }}</div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-subtitle-2">Prize Pool</div>
                  <div class="text-h6">{{ formatMoney(tournament.prize_pool || 0) }}</div>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Navigation par onglets -->
      <v-card>
        <v-tabs
          v-model="activeTab"
          bg-color="primary"
          dark
          centered
          show-arrows
        >
          <v-tab value="players">
            <v-icon start>mdi-account-group</v-icon>
            Joueurs
          </v-tab>
          <v-tab value="progress" :disabled="tournament.status === 'PLANNED'">
            <v-icon start>mdi-timer</v-icon>
            Déroulement
          </v-tab>
          <v-tab value="tables" :disabled="tournament.status === 'PLANNED'">
            <v-icon start>mdi-poker-chip</v-icon>
            Tables
          </v-tab>
        </v-tabs>

        <v-card-text class="pa-0">
          <v-window v-model="activeTab">
            <!-- Onglet Joueurs -->
            <v-window-item value="players">
              <div class="pa-4">
                <v-data-table
                  :headers="playerHeaders"
                  :items="sortedPlayers"
                  :loading="loading"
                  :items-per-page="10"
                  item-value="id"
                  class="elevation-1"
                >
                  <!-- Nom du joueur et badges -->
                  <template v-slot:item.player="{ item }">
                    <div class="d-flex align-center">
                      <v-avatar size="32" class="mr-2">
                        <v-img
                          v-if="item.raw && item.raw.user && item.raw.user.profile_image_path"
                          :src="item.raw.user.profile_image_path"
                          alt="Avatar"
                        ></v-img>
                        <v-icon v-else size="small">mdi-account</v-icon>
                      </v-avatar>
                      <span>{{ item.raw && item.raw.user ? item.raw.user.username : 'Unknown' }}</span>
                      
                      <!-- Add null checks to all badge conditions -->
                      <v-tooltip v-if="item.raw && isWinner(item.raw)" location="bottom">
                        <!-- tooltip content -->
                      </v-tooltip>
                      
                      <!-- Badge de victoire -->
                      <v-tooltip v-if="isWinner(item.raw)" location="bottom">
                        <template v-slot:activator="{ props }">
                          <v-icon 
                            v-bind="props"
                            color="amber" 
                            class="ml-2"
                          >
                            {{ tournament.tournament_type === 'JAPT' ? 'mdi-poker-chip' : 'mdi-trophy' }}
                          </v-icon>
                        </template>
                        <span>{{ tournament.tournament_type === 'JAPT' ? 'Détenteur du Jeton d\'Argile' : 'Vainqueur' }}</span>
                      </v-tooltip>
                      
                      <!-- Badge bubble -->
                      <v-tooltip v-if="isBubbleBoy(item.raw)" location="bottom">
                        <template v-slot:activator="{ props }">
                          <v-icon 
                            v-bind="props" 
                            color="blue" 
                            class="ml-2"
                          >
                            mdi-water
                          </v-icon>
                        </template>
                        <span>Bubble Boy</span>
                      </v-tooltip>
                      
                      <!-- Badges spécifiques JAPT -->
                      <template v-if="tournament.tournament_type === 'JAPT'">
                        <!-- Badge Bounty Hunter -->
                        <v-tooltip v-if="isBountyHunter(item.raw)" location="bottom">
                          <template v-slot:activator="{ props }">
                            <v-icon 
                              v-bind="props"
                              color="red" 
                              class="ml-2"
                            >
                              mdi-target
                            </v-icon>
                          </template>
                          <span>Bounty Hunter</span>
                        </v-tooltip>
                        
                        <!-- Badge Jeton d'Argile brisé -->
                        <v-tooltip v-if="hadClayToken(item.raw) && !isWinner(item.raw)" location="bottom">
                          <template v-slot:activator="{ props }">
                            <v-icon 
                              v-bind="props" 
                              color="grey" 
                              class="ml-2"
                            >
                              mdi-poker-chip-off
                            </v-icon>
                          </template>
                          <span>Jeton d'Argile perdu</span>
                        </v-tooltip>
                        
                        <!-- Badge double victoire -->
                        <v-tooltip v-if="hasDoubleWin(item.raw)" location="bottom">
                          <template v-slot:activator="{ props }">
                            <v-icon 
                              v-bind="props"
                              color="amber" 
                              class="ml-2"
                            >
                              mdi-numeric-2-circle
                            </v-icon>
                          </template>
                          <span>Double victoire</span>
                        </v-tooltip>
                        
                        <!-- Badge double victoire perdue -->
                        <v-tooltip v-if="hadDoubleWin(item.raw) && !isWinner(item.raw)" location="bottom">
                          <template v-slot:activator="{ props }">
                            <v-icon 
                              v-bind="props"
                              color="grey" 
                              class="ml-2"
                            >
                              mdi-numeric-2-circle-outline
                            </v-icon>
                          </template>
                          <span>Double victoire perdue</span>
                        </v-tooltip>
                        
                        <!-- Badge triplé -->
                        <v-tooltip v-if="hasTripleWin(item.raw)" location="bottom">
                          <template v-slot:activator="{ props }">
                            <v-icon 
                              v-bind="props"
                              color="gold" 
                              class="ml-2"
                            >
                              mdi-numeric-3-circle
                            </v-icon>
                          </template>
                          <span>Triplé !</span>
                        </v-tooltip>
                      </template>
                    </div>
                  </template>
                  
                  <!-- Heure d'inscription -->
                  <template v-slot:item.registration_time="{ item }">
                    {{ formatTime(item.raw.registration_time) }}
                  </template>
                  
                  <!-- Buy-in total -->
                  <template v-slot:item.total_buyin="{ item }">
                    {{ formatMoney(item.raw.total_buyin) }}
                  </template>
                  
                  <!-- Position finale -->
                  <template v-slot:item.final_position="{ item }">
                    <span v-if="item.raw.is_active">En jeu</span>
                    <span v-else>{{ item.raw.current_position || '-' }}</span>
                  </template>
                  
                  <!-- Prix -->
                  <template v-slot:item.prize_won="{ item }">
                    {{ formatMoney(item.raw.prize_won) }}
                  </template>
                  
                  <!-- Actions pour admin -->
                  <template v-slot:item.actions="{ item }">
                    <div v-if="isAdmin && tournament.status === 'IN_PROGRESS'">
                      <v-btn
                        v-if="item.raw.is_active"
                        icon="mdi-account-remove"
                        size="small"
                        color="error"
                        @click="handleElimination(item.raw)"
                      ></v-btn>
                      <v-btn
                        v-if="item.raw.is_active && canRebuy"
                        icon="mdi-refresh"
                        size="small"
                        color="success"
                        class="ml-2"
                        @click="handleRebuy(item.raw)"
                      ></v-btn>
                    </div>
                  </template>
                </v-data-table>
              </div>
            </v-window-item>

            <!-- Onglet Déroulement du tournoi -->
            <v-window-item value="progress">
              <div class="pa-4">
                <v-row>
                  <!-- Timer principal et infos blindes -->
                  <v-col cols="12" md="8">
                    <v-card class="timer-card elevation-3">
                      <v-card-text class="text-center pa-6">
                        <!-- Affichage du timer -->
                        <div class="text-h1 timer-display" :class="{ 'timer-warning': timeRemaining <= 60 }">
                          {{ formattedTimeRemaining }}
                        </div>
                        
                        <!-- Niveau actuel et blindes -->
                        <div class="text-h5 mb-4">
                          Niveau {{ currentLevel }} - Blindes: {{ currentBlinds }}
                        </div>
                        
                        <!-- Barre de progression -->
                        <v-progress-linear
                          v-model="timerProgress"
                          height="10"
                          :color="timerProgressColor"
                          rounded
                          class="mb-4"
                        ></v-progress-linear>
                        
                        <!-- Prochaines blindes -->
                        <div class="text-subtitle-1">
                          Prochain niveau: {{ nextBlinds }}
                        </div>
                        
                        <!-- Contrôles admin -->
                        <div v-if="isAdmin" class="mt-6 d-flex justify-center">
                          <v-btn
                            color="primary"
                            :prepend-icon="isPaused ? 'mdi-play' : 'mdi-pause'"
                            class="mx-2"
                            @click="togglePause"
                          >
                            {{ isPaused ? 'Reprendre' : 'Pause' }}
                          </v-btn>
                          <v-btn
                            color="warning"
                            prepend-icon="mdi-skip-next"
                            class="mx-2"
                            @click="confirmNextLevel"
                          >
                            Niveau suivant
                          </v-btn>
                          <v-btn
                            color="success"
                            prepend-icon="mdi-refresh"
                            class="mx-2"
                            @click="resetTimer"
                          >
                            Réinitialiser
                          </v-btn>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  
                  <!-- Statistiques du tournoi -->
                  <v-col cols="12" md="4">
                    <v-card class="elevation-1">
                      <v-list lines="two">
                        <v-list-item>
                          <template v-slot:prepend>
                            <v-icon icon="mdi-account-group"></v-icon>
                          </template>
                          <v-list-item-title>Joueurs restants</v-list-item-title>
                          <v-list-item-subtitle class="text-right">{{ activePlayers.length }}</v-list-item-subtitle>
                        </v-list-item>
                        
                        <v-list-item>
                          <template v-slot:prepend>
                            <v-icon icon="mdi-poker-chip"></v-icon>
                          </template>
                          <v-list-item-title>Stack moyen</v-list-item-title>
                          <v-list-item-subtitle class="text-right">{{ averageStack }}</v-list-item-subtitle>
                        </v-list-item>
                        
                        <v-list-item>
                          <template v-slot:prepend>
                            <v-icon icon="mdi-clock-outline"></v-icon>
                          </template>
                          <v-list-item-title>Temps écoulé</v-list-item-title>
                          <v-list-item-subtitle class="text-right">{{ elapsedTime }}</v-list-item-subtitle>
                        </v-list-item>
                        
                        <v-list-item>
                          <template v-slot:prepend>
                            <v-icon icon="mdi-clock"></v-icon>
                          </template>
                          <v-list-item-title>Heure actuelle</v-list-item-title>
                          <v-list-item-subtitle class="text-right">{{ currentTime }}</v-list-item-subtitle>
                        </v-list-item>
                      </v-list>
                    </v-card>
                    
                    <!-- Distribution des gains -->
                    <v-card class="mt-4 elevation-1">
                      <v-card-title>Distribution des gains</v-card-title>
                      <v-card-text>
                        <v-list density="compact">
                          <v-list-item v-for="(prize, index) in prizeDistribution" :key="index">
                            <v-list-item-title>{{ prize.position }}</v-list-item-title>
                            <v-list-item-subtitle class="text-right">{{ formatMoney(prize.amount) }}</v-list-item-subtitle>
                          </v-list-item>
                        </v-list>
                      </v-card-text>
                    </v-card>
                    
                    <!-- Structure des blindes -->
                    <v-card class="mt-4 elevation-1">
                      <v-card-title class="d-flex justify-space-between align-center">
                        <span>Structure des blindes</span>
                        <v-btn
                          v-if="isAdmin"
                          icon
                          size="small"
                          @click="showBlindsStructure = !showBlindsStructure"
                        >
                          <v-icon>{{ showBlindsStructure ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
                        </v-btn>
                      </v-card-title>
                      <v-expand-transition>
                        <div v-if="showBlindsStructure">
                          <v-data-table
                            :headers="blindsHeaders"
                            :items="blindsStructure"
                            hide-default-footer
                            density="compact"
                            class="blinds-table"
                          >
                            <template v-slot:item.duration="{ item }">
                              {{ item.raw.duration }} min
                            </template>
                            <template v-slot:item.current="{ item }">
                              <v-icon v-if="item.raw.level === currentLevel" color="primary">mdi-check</v-icon>
                            </template>
                          </v-data-table>
                        </div>
                      </v-expand-transition>
                    </v-card>
                  </v-col>
                </v-row>
              </div>
            </v-window-item>

            <!-- Onglet Tables -->
            <v-window-item value="tables">
              <div class="pa-4">
                <v-row>
                  <!-- Contrôles des tables pour admin -->
                  <v-col v-if="isAdmin" cols="12" class="d-flex justify-end mb-4">
                    <v-btn
                      color="primary"
                      prepend-icon="mdi-refresh"
                      class="mx-2"
                      @click="redrawTables"
                      :disabled="!canRedraw"
                    >
                      Redraw
                    </v-btn>
                    <v-btn
                      v-if="tables.length > 1"
                      color="warning"
                      prepend-icon="mdi-table-remove"
                      class="mx-2"
                      @click="breakTable"
                    >
                      Casser une table
                    </v-btn>
                  </v-col>
                  
                  <!-- Affichage des tables -->
                  <v-col 
                    v-for="(tableIndex, index) in tables"
                    :key="index"
                    cols="12"
                    :md="tables.length > 1 ? 6 : 12"
                    :lg="tables.length > 2 ? 4 : (tables.length > 1 ? 6 : 12)"
                    class="mb-4"
                  >
                    <v-card class="elevation-3">
                      <v-card-title class="d-flex justify-space-between">
                        <span>Table {{ index + 1 }}</span>
                        <v-chip color="primary" size="small">{{ getPlayersAtTable(tableIndex).length }} joueurs</v-chip>
                      </v-card-title>
                      <v-card-text class="pa-0">
                        <div class="poker-table-container">
                          <div class="poker-table">
                            <!-- Bouton Dealer -->
                            <div v-if="dealerPosition !== null" class="dealer-button">D</div>
                            
                            <!-- Positions des joueurs -->
                            <div 
                              v-for="position in 10" 
                              :key="position"
                              :class="[
                                'player-position',
                                `position-${position - 1}`,
                                { 'occupied': isPositionOccupied(tableIndex, position - 1) }
                              ]"
                              @click="handlePositionClick(tableIndex, position - 1)"
                            >
                              <template v-if="getPlayerAtPosition(tableIndex, position - 1)">
                                <v-avatar size="40" class="elevation-2 player-avatar">
                                  <v-img
                                    v-if="getPlayerAtPosition(tableIndex, position - 1).profile_image_path"
                                    :src="getPlayerAtPosition(tableIndex, position - 1).profile_image_path"
                                    alt="Avatar"
                                  ></v-img>
                                  <v-icon v-else>mdi-account</v-icon>
                                </v-avatar>
                                <div class="player-name">
                                  {{ getPlayerAtPosition(tableIndex, position - 1).username }}
                                </div>
                              </template>
                              <template v-else>
                                <div class="empty-position">
                                  {{ position }}
                                </div>
                              </template>
                            </div>
                          </div>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
              </div>
            </v-window-item>
          </v-window>
        </v-card-text>
      </v-card>

      <!-- Dialogues pour les actions du tournoi -->
      <tournament-dialogs
        ref="dialogsRef"
        :total-players="activePlayers.length + eliminatedPlayers.length"
        @rebuy-confirmed="confirmRebuy"
        @elimination-confirmed="confirmElimination"
        @table-rebalance-confirmed="confirmRebalance"
      />

      <!-- Dialogue de confirmation pour passer au niveau suivant -->
      <v-dialog v-model="showNextLevelConfirm" max-width="400">
        <v-card>
          <v-card-title>Confirmer le changement de niveau</v-card-title>
          <v-card-text>
            Êtes-vous sûr de vouloir passer au niveau suivant ? 
            Cette action ne peut pas être annulée.
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="grey-lighten-1"
              variant="text"
              @click="showNextLevelConfirm = false"
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

      <!-- Dialogue de confirmation pour supprimer une table -->
      <v-dialog v-model="showBreakTableConfirm" max-width="400">
        <v-card>
          <v-card-title>Confirmer la suppression d'une table</v-card-title>
          <v-card-text>
            Quelle table souhaitez-vous supprimer ?
            Les joueurs seront répartis sur les autres tables.
          </v-card-text>
          <v-card-text>
            <v-select
              v-model="tableToBreak"
              :items="tableSelectItems"
              label="Sélectionner une table"
              required
            ></v-select>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="grey-lighten-1"
              variant="text"
              @click="showBreakTableConfirm = false"
            >
              Annuler
            </v-btn>
            <v-btn
              color="primary"
              @click="confirmBreakTable"
              :disabled="tableToBreak === null"
            >
              Confirmer
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Notifications -->
      <v-snackbar
        v-model="snackbar.show"
        :color="snackbar.color"
        :timeout="snackbar.timeout"
      >
        {{ snackbar.text }}
        <template v-slot:actions>
          <v-btn
            color="white"
            text
            @click="snackbar.show = false"
          >
            Fermer
          </v-btn>
        </template>
      </v-snackbar>
    </template>

    <!-- Message tournoi non trouvé -->
    <v-alert
      v-else-if="!loading"
      type="error"
      class="mt-4"
    >
      Tournoi non trouvé ou erreur lors du chargement.
    </v-alert>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTournamentStore } from '@/stores/tournament'
import { useAuthStore } from '@/stores/auth'
import { format, formatDistance } from 'date-fns'
import { fr } from 'date-fns/locale'
import { websocketService } from '@/services/websocket.service'

import TournamentDialogs from '@/components/tournament/TournamentDialogs.vue'

const route = useRoute()
const router = useRouter()
const tournamentStore = useTournamentStore()
const authStore = useAuthStore()

// Refs pour l'état UI
const loading = ref(true)
const activeTab = ref('players')
const dialogsRef = ref(null)
const showNextLevelConfirm = ref(false)
const showBreakTableConfirm = ref(false)
const showBlindsStructure = ref(false)
const tableToBreak = ref(null)
const wsConnected = ref(false)
const wsEventListeners = ref([])
const tournamentData = ref(null)

// État du tournoi
const currentLevel = ref(1)
const timeRemaining = ref(0)
const levelDuration = ref(0)
const dealerPosition = ref(0)
const isPaused = ref(false)
const lastUpdateTime = ref(Date.now())
const timerInterval = ref(null)

// Snackbar pour les notifications
const snackbar = ref({
  show: false,
  text: '',
  color: 'success',
  timeout: 3000
})

// Propriétés calculées
const tournament = computed(() => tournamentStore.currentTournament || null)
const isAdmin = computed(() => {
  if (!tournament.value || !authStore.user) return false
  return tournament.value.admin_id === authStore.user.id
})

const activePlayers = computed(() => {
  return tournamentStore.getActivePlayers?.filter(p => p && p.is_active) || []
})

const eliminatedPlayers = computed(() => {
  return tournamentStore.getEliminatedPlayers || []
})

const sortedPlayers = computed(() => {
  // Safely combine players with null checks
  const allPlayers = [
    ...(activePlayers.value || []), 
    ...(eliminatedPlayers.value || [])
  ].filter(p => p) // Filter out any null/undefined values
  
  if (!tournament.value) return allPlayers
  
  if (tournament.value.status === 'PLANNED') {
    // Tri par heure d'inscription pour les tournois planifiés
    return allPlayers.sort((a, b) => 
      new Date(a.registration_time) - new Date(b.registration_time)
    )
  } else {
    // Tri par position pour les tournois en cours ou terminés
    // Joueurs actifs d'abord (pas encore de position), puis par position pour les éliminés
    return allPlayers.sort((a, b) => {
      if (a.is_active && !b.is_active) return -1
      if (!a.is_active && b.is_active) return 1
      if (a.is_active && b.is_active) return 0
      return (a.current_position || 999) - (b.current_position || 999)
    })
  }
})

const tables = computed(() => {
  if (!tournament.value || !tournament.value.num_tables) return []
  return Array.from({ length: tournament.value.num_tables }, (_, i) => i)
})

const tableSelectItems = computed(() => {
  return tables.value.map((tableIndex, index) => ({
    value: tableIndex,
    title: `Table ${index + 1} (${getPlayersAtTable(tableIndex).length} joueurs)`
  }))
})

const canRedraw = computed(() => {
  return tournament.value?.status === 'IN_PROGRESS' && activePlayers.value.length > 0
})

const canRebuy = computed(() => {
  if (!tournament.value || !tournament.value.configuration) return false
  return currentLevel.value <= (tournament.value.configuration.rebuy_levels || 0)
})

// Propriétés calculées pour le timer et les blindes
const formattedTimeRemaining = computed(() => {
  const minutes = Math.floor(timeRemaining.value / 60)
  const seconds = Math.floor(timeRemaining.value % 60)
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

const timerProgress = computed(() => {
  if (levelDuration.value <= 0) return 0
  return 100 - ((timeRemaining.value / levelDuration.value) * 100)
})

const timerProgressColor = computed(() => {
  if (timeRemaining.value <= 30) return 'red'
  if (timeRemaining.value <= 60) return 'orange'
  return 'primary'
})

const currentBlinds = computed(() => {
  const level = blindsStructure.value.find(l => l.level === currentLevel.value)
  if (!level) return 'N/A'
  return `${level.small_blind} / ${level.big_blind}`
})

const nextBlinds = computed(() => {
  const nextLevel = blindsStructure.value.find(l => l.level === currentLevel.value + 1)
  if (!nextLevel) return 'Fin du tournoi'
  return `${nextLevel.small_blind} / ${nextLevel.big_blind}`
})

const blindsStructure = computed(() => {
  if (!tournament.value?.configuration?.blinds_structure) return []
  return tournament.value.configuration.blinds_structure
})

const blindsHeaders = computed(() => [
  { title: 'Niveau', key: 'level', align: 'center' },
  { title: 'Small Blind', key: 'small_blind', align: 'center' },
  { title: 'Big Blind', key: 'big_blind', align: 'center' },
  { title: 'Durée', key: 'duration', align: 'center' },
  { title: 'Actuel', key: 'current', align: 'center', sortable: false }
])

// En-têtes pour la table des joueurs
const playerHeaders = computed(() => {
  const headers = [
    { title: 'Joueur', key: 'player', sortable: false },
    { title: 'Inscription', key: 'registration_time' },
    { title: 'Buy-in Total', key: 'total_buyin' },
    { title: 'Rebuys', key: 'num_rebuys' },
    { title: 'Position', key: 'final_position' },
    { title: 'Gains', key: 'prize_won' }
  ]
  
  // Ajout de la colonne actions pour les admins
  if (isAdmin.value && tournament.value?.status === 'IN_PROGRESS') {
    headers.push({ title: 'Actions', key: 'actions', sortable: false })
  }
  
  return headers
})

// Statistiques du tournoi
const averageStack = computed(() => {
  if (!activePlayers.value || activePlayers.value.length === 0) return 0
  const totalChips = activePlayers.value.reduce((sum, player) => 
    sum + (player.current_chips || 0), 0
  )
  return formatNumber(totalChips / activePlayers.value.length)
})

const elapsedTime = computed(() => {
  if (!tournament.value?.start_time) return '00:00:00'
  const startTime = new Date(tournament.value.start_time)
  const now = new Date()
  const elapsedMs = now - startTime
  
  const hours = Math.floor(elapsedMs / 3600000)
  const minutes = Math.floor((elapsedMs % 3600000) / 60000)
  const seconds = Math.floor((elapsedMs % 60000) / 1000)
  
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

const currentTime = computed(() => {
  return format(new Date(), 'HH:mm:ss')
})

const prizeDistribution = computed(() => {
  if (!tournament.value?.prize_pool) return []
  
  // Récupérer la structure de paiement appropriée
  const payoutStructure = tournament.value.configuration?.payouts_structure
  if (!payoutStructure) return []
  
  // Trouver la structure qui correspond au nombre de joueurs
  const totalPlayers = activePlayers.value.length + eliminatedPlayers.value.length
  const structure = payoutStructure.find(s => s.num_players <= totalPlayers)
  if (!structure) return []
  
  // Calculer les montants en fonction du prize pool
  return structure.prizes.map(prize => ({
    position: `${prize.position}${getPositionSuffix(prize.position)}`,
    amount: (tournament.value.prize_pool * prize.percentage) / 100
  }))
})

// Fonctions utilitaires pour les formats d'affichage
const formatDate = (date) => {
  if (!date) return '-'
  return format(new Date(date), 'PPP à HH:mm', { locale: fr })
}

const formatTime = (dateTime) => {
  if (!dateTime) return '-'
  return format(new Date(dateTime), 'HH:mm:ss')
}

const formatMoney = (amount) => {
  if (amount === undefined || amount === null) return '-'
  return amount.toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' })
}

const formatNumber = (number) => {
  if (number === undefined || number === null) return '-'
  return number.toLocaleString('fr-FR')
}

const getPositionSuffix = (position) => {
  if (position === 1) return 'er'
  return 'ème'
}

// Fonctions utilitaires pour les statuts
const getStatusColor = (status) => {
  const colors = {
    'PLANNED': 'blue',
    'IN_PROGRESS': 'success',
    'COMPLETED': 'grey'
  }
  return colors[status] || 'grey'
}

const getStatusLabel = (status) => {
  const labels = {
    'PLANNED': 'Planifié',
    'IN_PROGRESS': 'En cours',
    'COMPLETED': 'Terminé'
  }
  return labels[status] || status
}

// Fonctions pour les badges des joueurs
const isWinner = (player) => {
  if (!player || !tournament.value) return false
  
  // For the tournaments JAPT, the winner is the holder of the clay token
  if (tournament.value.tournament_type === 'JAPT') {
    return player.user && player.user.id === tournament.value.clay_token_holder_id
  }
  
  // For other tournaments, the winner is in position 1
  return player.current_position === 1 && !player.is_active
}

const isBubbleBoy = (player) => {
  if (!player || !tournament.value || tournament.value.status !== 'COMPLETED') return false
  
  // Trouver la structure qui correspond au nombre de joueurs
  const totalPlayers = activePlayers.value.length + eliminatedPlayers.value.length
  const payoutStructure = tournament.value.configuration?.payouts_structure
  if (!payoutStructure) return false
  
  const structure = payoutStructure.find(s => s.num_players <= totalPlayers)
  if (!structure) return false
  
  // Trouver la dernière position payée
  const lastPaidPosition = Math.max(...structure.prizes.map(p => p.position))
  
  // Le bubble boy est celui qui est éliminé juste avant le premier joueur payé
  return player.current_position === lastPaidPosition + 1 && !player.is_active
}

const isBountyHunter = (player) => {
  if (!player || !tournament.value) return false
  if (tournament.value.tournament_type !== 'JAPT') return false
  return player.user && player.user.id === tournament.value.bounty_hunter_id
}

const hadClayToken = (player) => {
  // Logique pour déterminer si le joueur avait le jeton d'argile lors du tournoi précédent
  // Cette information nécessiterait d'être stockée dans l'historique du joueur
  // Pour l'exemple, retournons false
  return false
}

const hasDoubleWin = (player) => {
  // Logique pour déterminer si le joueur a réalisé un doublé
  // Cette information nécessiterait un historique des victoires
  // Pour l'exemple, retournons false
  return false
}

const hadDoubleWin = (player) => {
  // Logique pour déterminer si le joueur avait réalisé un doublé mais vient de perdre
  // Pour l'exemple, retournons false
  return false
}

const hasTripleWin = (player) => {
  // Logique pour déterminer si le joueur a réalisé un triplé
  // Pour l'exemple, retournons false
  return false
}

// Gestion des tables
const getPlayersAtTable = (tableIndex) => {
  if (!activePlayers.value) return []
  return activePlayers.value.filter(player => player.table === tableIndex)
}

const getPlayerAtPosition = (tableIndex, position) => {
  if (!activePlayers.value) return null
  return activePlayers.value.find(player => 
    player.table === tableIndex && player.position === position
  )
}

const isPositionOccupied = (tableIndex, position) => {
  return getPlayerAtPosition(tableIndex, position) !== undefined
}

const handlePositionClick = (tableIndex, position) => {
  // Si l'utilisateur n'est pas admin ou le tournoi n'est pas en cours, ne rien faire
  if (!isAdmin.value || tournament.value?.status !== 'IN_PROGRESS') return
  
  const player = getPlayerAtPosition(tableIndex, position)
  
  if (player) {
    // Si un joueur est déjà à cette position, ouvrir un menu d'action
    openPlayerActionMenu(player, tableIndex, position)
  } else {
    // Si la position est vide, permettre de déplacer un joueur
    // (cette fonctionnalité nécessiterait une autre interface)
    showMovePlayerDialog(tableIndex, position)
  }
}

const openPlayerActionMenu = (player, tableIndex, position) => {
  if (!dialogsRef.value) return
  
  const actions = []
  
  if (canRebuy.value) {
    actions.push({
      icon: 'mdi-refresh',
      title: 'Rebuy',
      action: () => handleRebuy(player)
    })
  }
  
  actions.push({
    icon: 'mdi-account-remove',
    title: 'Éliminer',
    action: () => handleElimination(player)
  })
  
  // Afficher un menu contextuel
  // Cette fonctionnalité nécessiterait un composant supplémentaire
}

const showMovePlayerDialog = (tableIndex, position) => {
  // Implémenter la logique pour déplacer un joueur vers cette position
}

// Gestion du timer et des niveaux
const startTimer = () => {
  stopTimer() // Arrêter tout timer existant
  
  if (isPaused.value) return
  
  lastUpdateTime.value = Date.now()
  
  timerInterval.value = setInterval(() => {
    if (timeRemaining.value > 0) {
      const now = Date.now()
      const elapsed = (now - lastUpdateTime.value) / 1000
      lastUpdateTime.value = now
      
      timeRemaining.value = Math.max(0, timeRemaining.value - elapsed)
      
      // Si le timer atteint zéro, notifier
      if (timeRemaining.value === 0) {
        levelComplete()
      }
    } else {
      stopTimer()
    }
  }, 1000)
}

const stopTimer = () => {
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
    timerInterval.value = null
  }
}

const resetTimer = async () => {
  if (!isAdmin.value || !tournament.value) return
  
  try {
    // Récupérer la durée du niveau actuel
    const level = blindsStructure.value.find(l => l.level === currentLevel.value)
    if (!level) return
    
    const durationInSeconds = level.duration * 60
    
    // Mettre à jour le timer sur le serveur
    await tournamentStore.updateTournamentTimer(tournament.value.id, durationInSeconds)
    
    // Mettre à jour localement
    timeRemaining.value = durationInSeconds
    levelDuration.value = durationInSeconds
    lastUpdateTime.value = Date.now()
    
    // Redémarrer le timer si nécessaire
    if (!isPaused.value) {
      startTimer()
    }
    
    showSuccess('Timer réinitialisé')
  } catch (error) {
    console.error('Erreur lors de la réinitialisation du timer:', error)
    showError('Erreur lors de la réinitialisation du timer')
  }
}

const levelComplete = () => {
  // Cette fonction est appelée quand un niveau est terminé
  if (isAdmin.value) {
    // Proposer de passer au niveau suivant
    showNextLevelConfirm.value = true
  }
}

const confirmNextLevel = () => {
  showNextLevelConfirm.value = true
}

const nextLevel = async () => {
  if (!isAdmin.value || !tournament.value) return
  
  try {
    const nextLevelNumber = currentLevel.value + 1
    await tournamentStore.updateTournamentLevel(tournament.value.id, nextLevelNumber)
    
    // Fermer le dialogue de confirmation
    showNextLevelConfirm.value = false
    
    // Mettre à jour localement
    currentLevel.value = nextLevelNumber
    
    // Mettre à jour le timer avec la durée du nouveau niveau
    const level = blindsStructure.value.find(l => l.level === nextLevelNumber)
    if (level) {
      timeRemaining.value = level.duration * 60
      levelDuration.value = level.duration * 60
      lastUpdateTime.value = Date.now()
      
      // Redémarrer le timer si nécessaire
      if (!isPaused.value) {
        startTimer()
      }
    }
    
    showSuccess(`Passage au niveau ${nextLevelNumber}`)
  } catch (error) {
    console.error('Erreur lors du changement de niveau:', error)
    showError('Erreur lors du changement de niveau')
  }
}

const togglePause = async () => {
  if (!isAdmin.value || !tournament.value) return
  
  try {
    if (isPaused.value) {
      // Reprendre le tournoi
      await tournamentStore.resumeTournament(tournament.value.id)
      isPaused.value = false
      lastUpdateTime.value = Date.now()
      startTimer()
      showSuccess('Tournoi repris')
    } else {
      // Mettre en pause le tournoi
      await tournamentStore.pauseTournament(tournament.value.id)
      isPaused.value = true
      stopTimer()
      showSuccess('Tournoi en pause')
    }
  } catch (error) {
    console.error('Erreur lors de la pause/reprise:', error)
    showError('Erreur lors de la pause/reprise')
  }
}

// Gestion des actions des joueurs
const handleRebuy = (player) => {
  if (!dialogsRef.value || !tournament.value) return
  dialogsRef.value.showRebuyDialog(player)
}

const confirmRebuy = async (data) => {
  if (!tournament.value) return
  
  try {
    await tournamentStore.processRebuy(tournament.value.id, {
      playerId: data.playerId,
      amount: data.amount,
      chips: data.chips
    })
    
    showSuccess(`Rebuy effectué pour ${data.playerName}`)
    await refreshTournament()
  } catch (error) {
    console.error('Erreur lors du rebuy:', error)
    showError('Erreur lors du rebuy')
  }
}

const handleElimination = (player) => {
  if (!dialogsRef.value || !tournament.value) return
  dialogsRef.value.showEliminationDialog(player)
}

const confirmElimination = async (data) => {
  if (!tournament.value) return
  
  try {
    await tournamentStore.eliminatePlayer(tournament.value.id, {
      playerId: data.playerId,
      position: data.position,
      prize: data.prize,
      hadClayToken: data.hadClayToken,
      bountyHunterId: data.bountyHunterId
    })
    
    showSuccess(`${data.playerName} éliminé en position ${data.position}`)
    await refreshTournament()
  } catch (error) {
    console.error('Erreur lors de l\'élimination:', error)
    showError('Erreur lors de l\'élimination')
  }
}

// Gestion des tables
const redrawTables = async () => {
  if (!isAdmin.value || !tournament.value) return
  
  try {
    await tournamentStore.redrawTables(tournament.value.id)
    showSuccess('Redraw effectué avec succès')
    await refreshTournament()
  } catch (error) {
    console.error('Erreur lors du redraw:', error)
    showError('Erreur lors du redraw')
  }
}

const breakTable = () => {
  if (!isAdmin.value || !tournament.value || tables.value.length <= 1) return
  showBreakTableConfirm.value = true
}

const confirmBreakTable = async () => {
  if (!isAdmin.value || !tournament.value || tableToBreak.value === null) return
  
  try {
    await tournamentStore.breakTable(tournament.value.id, tableToBreak.value)
    showBreakTableConfirm.value = false
    tableToBreak.value = null
    showSuccess('Table supprimée avec succès')
    await refreshTournament()
  } catch (error) {
    console.error('Erreur lors de la suppression de la table:', error)
    showError('Erreur lors de la suppression de la table')
  }
}

const confirmRebalance = async () => {
  if (!isAdmin.value || !tournament.value) return
  
  try {
    await tournamentStore.rebalanceTables(tournament.value.id)
    showSuccess('Tables rééquilibrées avec succès')
    await refreshTournament()
  } catch (error) {
    console.error('Erreur lors du rééquilibrage des tables:', error)
    showError('Erreur lors du rééquilibrage des tables')
  }
}

// Notification helpers
const showSuccess = (text) => {
  snackbar.value = {
    show: true,
    text,
    color: 'success',
    timeout: 3000
  }
}

const showError = (text) => {
  snackbar.value = {
    show: true,
    text,
    color: 'error',
    timeout: 5000
  }
}

// WebSocket management
const setupWebSocket = async () => {
  if (!tournament.value) return
  
  try {
    await websocketService.connect(tournament.value.id)
    wsConnected.value = true
    
    // Setup listeners
    const removeListeners = []
    
    // Initial state
    removeListeners.push(
      websocketService.on('initial_state', (data) => {
        console.log('Initial state received:', data)
        
        // Update tournament state
        if (data.current_level) {
          currentLevel.value = data.current_level
        }
        
        if (data.seconds_remaining !== undefined && data.level_duration !== undefined) {
          timeRemaining.value = data.seconds_remaining
          levelDuration.value = data.level_duration
          lastUpdateTime.value = Date.now()
        }
        
        isPaused.value = data.paused || false
        
        // Start timer if not paused
        if (!isPaused.value) {
          startTimer()
        }
      })
    )
    
    // Level changed
    removeListeners.push(
      websocketService.on('level_changed', (data) => {
        console.log('Level changed:', data)
        
        if (data.level) {
          currentLevel.value = data.level
        }
        
        if (data.seconds_remaining !== undefined && data.level_duration !== undefined) {
          timeRemaining.value = data.seconds_remaining
          levelDuration.value = data.level_duration
          lastUpdateTime.value = Date.now()
        }
        
        // Restart timer if not paused
        if (!isPaused.value) {
          startTimer()
        }
      })
    )
    
    // Pause status changed
    removeListeners.push(
      websocketService.on('pause_status_changed', (data) => {
        console.log('Pause status changed:', data)
        
        isPaused.value = data.paused || false
        
        if (data.seconds_remaining !== undefined) {
          timeRemaining.value = data.seconds_remaining
          lastUpdateTime.value = Date.now()
        }
        
        if (isPaused.value) {
          stopTimer()
        } else {
          startTimer()
        }
      })
    )
    
    // Timer tick
    removeListeners.push(
      websocketService.on('timer_tick', (data) => {
        // Only update if significant difference to avoid jitter
        if (data.seconds_remaining !== undefined) {
          const diff = Math.abs(timeRemaining.value - data.seconds_remaining)
          if (diff > 2) {
            timeRemaining.value = data.seconds_remaining
            lastUpdateTime.value = Date.now()
          }
        }
      })
    )
    
    // Player eliminated
    removeListeners.push(
      websocketService.on('player_eliminated', (data) => {
        console.log('Player eliminated:', data)
        refreshTournament()
      })
    )
    
    // Player rebuy
    removeListeners.push(
      websocketService.on('player_rebuy', (data) => {
        console.log('Player rebuy:', data)
        refreshTournament()
      })
    )
    
    // Tables updated
    removeListeners.push(
      websocketService.on('tables_updated', (data) => {
        console.log('Tables updated:', data)
        refreshTournament()
      })
    )
    
    wsEventListeners.value = removeListeners
  } catch (error) {
    console.error('WebSocket connection failed:', error)
    wsConnected.value = false
  }
}

const teardownWebSocket = () => {
  // Clean up WebSocket listeners
  wsEventListeners.value.forEach(removeListener => removeListener())
  wsEventListeners.value = []
  
  // Disconnect WebSocket
  websocketService.disconnect()
  wsConnected.value = false
}

const refreshTournament = async () => {
  if (!tournament.value) return;
  
  try {
    loading.value = true; // Empêche l'accès aux données pendant le chargement
    
    await tournamentStore.fetchTournament(tournament.value.id);
    tournamentData.value = tournamentStore.currentTournament;
    
    // Vérification supplémentaire pour s'assurer que les données sont valides
    if (tournamentData.value && tournamentData.value.participations) {
      // Préparer les données des joueurs pour éviter des erreurs ultérieures
      activePlayers.value = tournamentData.value.participations
        .filter(p => p && p.is_active)
        .map(p => ({...p})); // Copie pour éviter des références mutables
        
      eliminatedPlayers.value = tournamentData.value.participations
        .filter(p => p && !p.is_active)
        .map(p => ({...p}));
    } else {
      // Valeurs par défaut sécurisées
      activePlayers.value = [];
      eliminatedPlayers.value = [];
    }
  } catch (error) {
    console.error('Error refreshing tournament:', error);
    showError('Erreur lors de la mise à jour des données du tournoi');
  } finally {
    loading.value = false;
  }
}


// Lifecycle hooks
onMounted(async () => {
  loading.value = true
  
  try {
    const tournamentId = parseInt(route.params.id)
    if (isNaN(tournamentId)) {
      router.push('/tournaments')
      return
    }
    
    await tournamentStore.fetchTournament(tournamentId)
    tournamentData.value = tournamentStore.currentTournament
    
    if (!tournamentData.value) {
      showError('Tournoi non trouvé')
      return
    }

    // Set default active tab based on tournament status
    if (tournamentData.value.status === 'PLANNED') {
      activeTab.value = 'players'
    } else {
      activeTab.value = 'progress'
    }
    
    // Initialize timer state with null checks
    if (tournamentData.value.status === 'IN_PROGRESS') {
      currentLevel.value = tournamentData.value.current_level || 1
      timeRemaining.value = tournamentData.value.seconds_remaining || 0
      levelDuration.value = tournamentData.value.level_duration || 0
      isPaused.value = tournamentData.value.paused_at !== null
      
      // Setup WebSocket for real-time updates
      await setupWebSocket()
      
      // Start timer if not paused
      if (!isPaused.value) {
        startTimer()
      }
    }
  } catch (error) {
    console.error('Error loading tournament:', error)
    showError('Erreur lors du chargement du tournoi')
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  // Clean up timers and WebSocket
  stopTimer()
  teardownWebSocket()
})

// Watch for route changes to load new tournament
watch(() => route.params.id, async (newId) => {
  if (newId) {
    // Clean up existing timers and connections
    stopTimer()
    teardownWebSocket()
    
    loading.value = true
    
    try {
      const tournamentId = parseInt(newId)
      if (isNaN(tournamentId)) {
        router.push('/tournaments')
        return
      }
      
      await tournamentStore.fetchTournament(tournamentId)
      tournamentData.value = tournamentStore.currentTournament
      
      // Reset and initialize state for new tournament
      if (tournamentData.value?.status === 'IN_PROGRESS') {
        currentLevel.value = tournamentData.value.current_level || 1
        timeRemaining.value = tournamentData.value.seconds_remaining || 0
        levelDuration.value = tournamentData.value.level_duration || 0
        isPaused.value = tournamentData.value.paused_at !== null
        
        // Setup WebSocket for real-time updates
        await setupWebSocket()
        
        // Start timer if not paused
        if (!isPaused.value) {
          startTimer()
        }
      }
    } catch (error) {
      console.error('Error loading tournament:', error)
      showError('Erreur lors du chargement du tournoi')
    } finally {
      loading.value = false
    }
  }
})
</script>

<style scoped>
/* Styles généraux */
.tournament-detail-container {
  min-height: 100vh;
  background-color: #f5f8fa;
}

.header-card {
  border-bottom: 3px solid var(--v-primary-base);
}

/* Styles pour le timer */
.timer-card {
  background: linear-gradient(135deg, #1a2a6c, #2a4858);
  color: white;
  border-radius: 12px;
}

.timer-display {
  font-family: 'Roboto Mono', monospace;
  font-size: 5rem;
  font-weight: 700;
  letter-spacing: 2px;
  text-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
  margin: 20px 0;
}

.timer-warning {
  animation: pulse 1s infinite;
  color: #ff5252;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.6; }
  100% { opacity: 1; }
}

/* Styles pour les tables de poker */
.poker-table-container {
  padding: 16px;
  margin-bottom: 16px;
  position: relative;
  aspect-ratio: 1;
  max-height: 500px;
}

.poker-table {
  background: #0f5c2e;
  border-radius: 50%;
  border: 15px solid #8B4513;
  width: 100%;
  height: 100%;
  position: relative;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3), inset 0 2px 10px rgba(255, 255, 255, 0.2);
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
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  z-index: 2;
}

.player-position {
  position: absolute;
  width: 60px;
  height: 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.2s ease;
  z-index: 1;
}

.player-position:hover {
  transform: scale(1.1);
}

.player-avatar {
  background-color: white;
  border: 2px solid white;
  margin-bottom: 4px;
}

.player-name {
  color: white;
  font-size: 0.8rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
  background-color: rgba(0, 0, 0, 0.5);
  padding: 2px 6px;
  border-radius: 4px;
  max-width: 100px;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}

.empty-position {
  color: rgba(255, 255, 255, 0.5);
  border: 2px dashed rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.1);
}

.occupied {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  padding: 4px;
}

/* Positionnement des joueurs autour de la table */
.position-0 { top: 10%; left: 50%; transform: translate(-50%, 0); }
.position-1 { top: 20%; left: 80%; transform: translate(-50%, 0); }
.position-2 { top: 50%; left: 90%; transform: translate(-50%, -50%); }
.position-3 { top: 80%; left: 80%; transform: translate(-50%, -50%); }
.position-4 { top: 90%; left: 50%; transform: translate(-50%, -50%); }
.position-5 { top: 80%; left: 20%; transform: translate(-50%, -50%); }
.position-6 { top: 50%; left: 10%; transform: translate(-50%, -50%); }
.position-7 { top: 20%; left: 20%; transform: translate(-50%, 0); }
.position-8 { top: 15%; left: 35%; transform: translate(-50%, 0); }
.position-9 { top: 15%; left: 65%; transform: translate(-50%, 0); }

/* Styles pour les tableaux */
.blinds-table {
  border-radius: 8px;
  overflow: hidden;
}
</style>