<!-- src/views/StatsView.vue -->
<template>
    <v-container>
      <!-- Filtres -->
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title>Statistiques</v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12" sm="4">
                  <v-select
                    v-model="filters.tournamentType"
                    :items="tournamentTypes"
                    label="Type de tournoi"
                    clearable
                  ></v-select>
                </v-col>
                <v-col cols="12" sm="4">
                  <v-text-field
                    v-model.number="filters.minGames"
                    type="number"
                    label="Nombre minimum de parties"
                    min="0"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="4">
                  <v-select
                    v-model="filters.timeRange"
                    :items="timeRanges"
                    label="Période"
                  ></v-select>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
  
      <!-- Statistiques globales -->
      <v-row class="mt-4">
        <v-col v-for="stat in globalStats" :key="stat.label" cols="12" sm="6" md="3">
          <v-card>
            <v-card-text class="text-center">
              <div class="text-h4 mb-2">{{ stat.value }}</div>
              <div class="text-subtitle-1">{{ stat.label }}</div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
  
      <!-- Graphiques -->
      <v-row class="mt-4">
        <!-- ROI Evolution -->
        <v-col cols="12" md="6">
          <v-card>
            <v-card-title>Évolution du ROI</v-card-title>
            <v-card-text>
              <line-chart
                :data="roiChartData"
                :options="lineChartOptions"
              />
            </v-card-text>
          </v-card>
        </v-col>
  
        <!-- Gains/Pertes -->
        <v-col cols="12" md="6">
          <v-card>
            <v-card-title>Gains/Pertes par mois</v-card-title>
            <v-card-text>
              <bar-chart
                :data="profitChartData"
                :options="barChartOptions"
              />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
  
      <!-- Tableau détaillé des statistiques par joueur -->
      <v-row class="mt-4">
        <v-col cols="12">
          <v-card>
            <v-card-title class="d-flex align-center">
              Classement des joueurs
              <v-spacer></v-spacer>
              <v-text-field
                v-model="search"
                append-icon="mdi-magnify"
                label="Rechercher"
                single-line
                hide-details
                density="compact"
              ></v-text-field>
            </v-card-title>
            <v-card-text>
              <v-data-table
                :headers="tableHeaders"
                :items="filteredPlayers"
                :search="search"
                :sort-by="[{ key: 'roi', order: 'desc' }]"
                class="elevation-1"
              >
                <!-- Colonne Joueur -->
                <template v-slot:item.player="{ item }">
                  <div class="d-flex align-center">
                    <v-avatar size="32" class="mr-2">
                      <v-img
                        v-if="item.profile_image_path"
                        :src="item.profile_image_path"
                        alt="avatar"
                      ></v-img>
                      <v-icon v-else>mdi-account</v-icon>
                    </v-avatar>
                    {{ item.username }}
                  </div>
                </template>
  
                <!-- Colonnes avec formatage -->
                <template v-slot:item.roi="{ item }">
                  <span :class="{ 'text-success': item.roi > 0, 'text-error': item.roi < 0 }">
                    {{ formatNumber(item.roi, 2) }}%
                  </span>
                </template>
  
                <template v-slot:item.avgProfit="{ item }">
                  <span :class="{ 'text-success': item.avgProfit > 0, 'text-error': item.avgProfit < 0 }">
                    {{ formatNumber(item.avgProfit, 2) }}€
                  </span>
                </template>
  
                <template v-slot:item.totalProfit="{ item }">
                  <span :class="{ 'text-success': item.totalProfit > 0, 'text-error': item.totalProfit < 0 }">
                    {{ formatNumber(item.totalProfit, 2) }}€
                  </span>
                </template>
  
                <template v-slot:item.winRate="{ item }">
                  {{ formatNumber(item.winRate, 1) }}%
                </template>
  
                <template v-slot:item.itm="{ item }">
                  {{ formatNumber(item.itm, 1) }}%
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
  
      <!-- Statistiques spéciales JAPT -->
      <v-row class="mt-4">
        <v-col cols="12" md="6">
          <v-card>
            <v-card-title>Top Chasseurs de Primes</v-card-title>
            <v-card-text>
              <v-list>
                <v-list-item
                  v-for="hunter in topBountyHunters"
                  :key="hunter.id"
                  :subtitle="`${hunter.bounties} primes - ${formatNumber(hunter.bountyRatio, 1)}% des éliminations`"
                >
                  <template v-slot:prepend>
                    <v-avatar size="40">
                      <v-img
                        v-if="hunter.profile_image_path"
                        :src="hunter.profile_image_path"
                        alt="avatar"
                      ></v-img>
                      <v-icon v-else>mdi-account</v-icon>
                    </v-avatar>
                  </template>
                  {{ hunter.username }}
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
  
        <v-col cols="12" md="6">
          <v-card>
            <v-card-title>Historique Jeton d'Argile</v-card-title>
            <v-card-text>
              <v-timeline density="compact">
                <v-timeline-item
                  v-for="holder in clayTokenHistory"
                  :key="holder.date"
                  :dot-color="holder.current ? 'primary' : 'grey'"
                  size="small"
                >
                  <template v-slot:opposite>
                    {{ formatDate(holder.date) }}
                  </template>
                  <div class="d-flex align-center">
                    <v-avatar size="32" class="mr-2">
                      <v-img
                        v-if="holder.profile_image_path"
                        :src="holder.profile_image_path"
                        alt="avatar"
                      ></v-img>
                      <v-icon v-else>mdi-account</v-icon>
                    </v-avatar>
                    {{ holder.username }}
                  </div>
                </v-timeline-item>
              </v-timeline>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue'
  import { format } from 'date-fns'
  import { fr } from 'date-fns/locale'
  import { Line as LineChart, Bar as BarChart } from 'vue-chartjs'
  import { 
    Chart as ChartJS, 
    CategoryScale, 
    LinearScale, 
    PointElement, 
    LineElement,
    BarElement,
    Title,
    Tooltip,
    Legend 
  } from 'chart.js'
  
  // Enregistrement des composants Chart.js
  ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    Title,
    Tooltip,
    Legend
  )
  
  // Filtres
  const filters = ref({
    tournamentType: null,
    minGames: 10,
    timeRange: 'all'
  })
  
  const search = ref('')
  
  // Options de filtres
  const tournamentTypes = [
    { title: 'Tous les types', value: null },
    { title: 'JAPT', value: 'JAPT' },
    { title: 'Classique', value: 'CLASSIQUE' },
    { title: 'MTT', value: 'MTT' }
  ]
  
  const timeRanges = [
    { title: 'Toute la période', value: 'all' },
    { title: '3 derniers mois', value: '3m' },
    { title: '6 derniers mois', value: '6m' },
    { title: 'Cette année', value: '1y' }
  ]
  
  // En-têtes du tableau
  const tableHeaders = [
    { title: 'Joueur', key: 'player', sortable: false },
    { title: 'Parties jouées', key: 'gamesPlayed', align: 'end' },
    { title: 'Victoires', key: 'victories', align: 'end' },
    { title: 'ROI', key: 'roi', align: 'end' },
    { title: 'ITM', key: 'itm', align: 'end' },
    { title: 'Gains moyens', key: 'avgProfit', align: 'end' },
    { title: 'Gains totaux', key: 'totalProfit', align: 'end' },
    { title: 'Taux de victoire', key: 'winRate', align: 'end' },
    { title: 'Bulles', key: 'bubbles', align: 'end' }
  ]
  
  // Données des statistiques globales
  const globalStats = computed(() => [
    { 
      label: 'Tournois joués',
      value: statsData.value?.totalTournaments || 0
    },
    {
      label: 'Prize pool total',
      value: `${formatNumber(statsData.value?.totalPrizePool || 0, 0)}€`
    },
    {
      label: 'Moyenne joueurs/tournoi',
      value: formatNumber(statsData.value?.avgPlayers || 0, 1)
    },
    {
      label: 'Plus gros prize pool',
      value: `${formatNumber(statsData.value?.biggestPrizePool || 0, 0)}€`
    }
  ])
  
  // Données des graphiques
  const roiChartData = computed(() => ({
    labels: statsData.value?.roiHistory?.map(item => format(new Date(item.date), 'MMM yyyy', { locale: fr })) || [],
    datasets: [{
      label: 'ROI %',
      data: statsData.value?.roiHistory?.map(item => item.roi) || [],
      fill: false,
      borderColor: '#1976D2',
      tension: 0.1
    }]
  }))
  
  const profitChartData = computed(() => ({
    labels: statsData.value?.monthlyProfits?.map(item => format(new Date(item.date), 'MMM yyyy', { locale: fr })) || [],
    datasets: [{
      label: 'Gains/Pertes (€)',
      data: statsData.value?.monthlyProfits?.map(item => item.profit) || [],
      backgroundColor: statsData.value?.monthlyProfits?.map(item => item.profit >= 0 ? '#4CAF50' : '#FF5252') || []
    }]
  }))
  
  // Options des graphiques
  const lineChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
  
  const barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      }
    }
  }
  
  // Données des joueurs filtrées
  const filteredPlayers = computed(() => {
    let players = statsData.value?.players || []
    
    if (filters.value.tournamentType) {
      players = players.filter(p => p.tournamentType === filters.value.tournamentType)
    }
    
    if (filters.value.minGames > 0) {
      players = players.filter(p => p.gamesPlayed >= filters.value.minGames)
    }
    
    return players
  })
  
  // Données des chasseurs de primes et du jeton d'argile
  const topBountyHunters = ref([])
  const clayTokenHistory = ref([])
  
  // Chargement des données
  const statsData = ref({})
  const loading = ref(false)
  
  const loadStats = async () => {
    loading.value = true
    try {
      const response = await fetch('/api/stats', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(filters.value)
      })
      statsData.value = await response.json()
    } catch (error) {
      console.error('Erreur lors du chargement des statistiques:', error)
    } finally {
      loading.value = false
    }
  }
  
  const loadJAPTStats = async () => {
    try {
      const [bountyResponse, clayResponse] = await Promise.all([
        fetch('/api/stats/bounty-hunters'),
        fetch('/api/stats/clay-token-history')
      ])
      topBountyHunters.value = await bountyResponse.json()
      clayTokenHistory.value = await clayResponse.json()
    } catch (error) {
      console.error('Erreur lors du chargement des statistiques JAPT:', error)
    }
  }
  
  // Méthodes utilitaires
  const formatNumber = (value, decimals = 0) => {
    return Number(value).toLocaleString('fr-FR', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    })
  }
  
  const formatDate = (date) => {
    return format(new Date(date), 'PPP', { locale: fr })
  }
  
  // Watch des filtres
  watch(filters, () => {
    loadStats()
  }, { deep: true })
  
  // Initialisation
  onMounted(() => {
    loadStats()
    loadJAPTStats()
  })
  </script>
  
  <style scoped>
  .v-data-table {
    background: transparent !important;
  }
  
  .text-success {
    color: #4CAF50 !important;
  }
  
  .text-error {
    color: #FF5252 !important;
  }
  
  :deep(.v-timeline-item__body) {
    min-height: 48px;
  }
  </style>