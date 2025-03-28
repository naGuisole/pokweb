<!-- src/views/HomeView.vue -->
<template>
  <v-container>
        <!-- Écran de bienvenue pour les utilisateurs non connectés -->
        <v-row v-if="!isAuthenticated" justify="center" align="center">
          <v-col cols="12" sm="10" md="8">
            <v-card class="text-center pa-6">
              <v-card-title class="text-h4 mb-4">
                Bienvenue sur Poweb !
              </v-card-title>
              <v-card-subtitle class="text-h6 mb-6">
                Organisez et participez à des tournois de poker entre amis
              </v-card-subtitle>
              <v-card-text class="text-body-1">
                <v-row justify="center" class="mb-4">
                  <v-col cols="12" md="8">
                    <p>
                      Connectez-vous ou créez un compte pour accéder à toutes les fonctionnalités :
                    </p>
                    <v-list class="bg-transparent">
                      <v-list-item prepend-icon="mdi-cards-playing">
                        Organisation de tournois de poker
                      </v-list-item>
                      <v-list-item prepend-icon="mdi-trophy">
                        Suivi du Jeton d'Argile
                      </v-list-item>
                      <v-list-item prepend-icon="mdi-chart-box">
                        Statistiques détaillées
                      </v-list-item>
                      <v-list-item prepend-icon="mdi-post">
                        Blog communautaire
                      </v-list-item>
                    </v-list>
                  </v-col>
                </v-row>
              </v-card-text>
              <v-card-actions class="justify-center">
                <v-btn
                  color="primary"
                  size="large"
                  to="/login"
                >
                  Commencer
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>

    <!-- Dashboard pour les utilisateurs connectés -->
    <template v-else>
      <!-- En-tête avec boutons d'action rapide -->
      <v-row>
        <v-col cols="12" md="6">
          <v-btn
            color="primary"
            size="large"
            prepend-icon="mdi-plus"
            class="mr-4"
            @click="createNewTournament"
          >
            Créer un tournoi
          </v-btn>
        </v-col>
      </v-row>

      <!-- Prochain tournoi -->
      <v-row class="mt-4">
        <v-col cols="12">
          <template v-if="nextTournament">
            <v-card class="mb-4">
              <v-card-title class="bg-primary text-white">
                Prochain tournoi
              </v-card-title>
              <v-card-text class="pa-4">
                <v-row align="center">
                  <v-col cols="12" md="8">
                    <h3 class="text-h6 mb-2">{{ nextTournament.name }}</h3>
                    <div class="text-body-1">
                      <v-icon start>mdi-calendar</v-icon>
                      {{ formatDate(nextTournament.date) }}
                    </div>
                    <div class="text-body-1">
                      <v-icon start>mdi-account-group</v-icon>
                      {{ nextTournament.participations?.length || 0 }} / {{ nextTournament.max_players }} joueurs
                    </div>
                    <div class="text-body-1">
                      <v-icon start>mdi-poker-chip</v-icon>
                      Buy-in: {{ nextTournament.buy_in }}€
                    </div>
                  </v-col>
                  <v-col cols="12" md="4" class="text-center">
                    <v-btn
                      color="primary"
                      :to="`/tournaments/${nextTournament.id}`"
                      class="ma-2"
                    >
                      Voir les détails
                    </v-btn>
                    <v-btn
                      v-if="!isRegistered(nextTournament.id)"
                      color="success"
                      @click="registerToTournament(nextTournament.id)"
                      :loading="registrationLoading"
                      class="ma-2"
                    >
                      S'inscrire
                    </v-btn>
                    <v-btn
                      v-else
                      color="error"
                      @click="unregisterFromTournament(nextTournament.id)"
                      :loading="registrationLoading"
                      class="ma-2"
                    >
                      Se désinscrire
                    </v-btn>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </template>
          <v-card v-else class="mb-4">
            <v-card-title class="bg-primary text-white">
              Prochain tournoi
            </v-card-title>
            <v-card-text class="pa-4 text-center">
              <p class="text-h6 my-4">Aucun tournoi planifié pour le moment</p>
              <v-btn
                color="primary"
                prepend-icon="mdi-plus"
                @click="createNewTournament"
              >
                Créer un tournoi
              </v-btn>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Section pour le dernier tournoi terminé -->
      <v-row class="mt-4" v-if="lastTournament">
        <v-col cols="12">
          <v-card class="mb-4">
            <v-card-title class="bg-grey-lighten-2">
              Dernier tournoi terminé
            </v-card-title>
            <v-card-text class="pa-4">
              <v-row align="center">
                <v-col cols="12" md="8">
                  <h3 class="text-h6 mb-2">{{ lastTournament.name }}</h3>
                  <div class="text-body-1">
                    <v-icon start>mdi-calendar</v-icon>
                    {{ formatDate(lastTournament.date) }}
                  </div>
                  <div class="text-body-1">
                    <v-icon start>mdi-account-group</v-icon>
                    {{ (lastTournament.participations?.length || 0) }} joueurs
                  </div>
                  <div v-if="lastTournament.winner" class="text-body-1">
                    <v-icon start>mdi-trophy</v-icon>
                    Gagnant: {{ lastTournament.winner.username }}
                  </div>
                </v-col>
                <v-col cols="12" md="4" class="text-center">
                  <v-btn
                    color="primary"
                    :to="`/tournaments/${lastTournament.id}`"
                    class="ma-2"
                  >
                    Voir les résultats
                  </v-btn>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Stats et infos importantes -->
      <v-row>
        <!-- Détenteur du Jeton d'Argile -->
        <v-col cols="12" md="6">
          <v-card height="100%">
            <v-card-title>
              <v-icon start color="amber-darken-2">mdi-crown</v-icon>
              Détenteur du Jeton d'Argile
            </v-card-title>
            <v-card-text class="text-center pa-4">
              <v-avatar size="100" class="mb-4">
                <v-img
                  v-if="clayTokenHolder?.profile_image_path"
                  :src="clayTokenHolder.profile_image_path"
                  alt="Détenteur du Jeton"
                ></v-img>
                <v-icon v-else size="48">mdi-account</v-icon>
              </v-avatar>
              <h3 class="text-h5">{{ clayTokenHolder?.username || 'Aucun détenteur' }}</h3>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Meilleur chasseur de primes -->
        <v-col cols="12" md="6">
          <v-card height="100%">
            <v-card-title>
              <v-icon start color="red">mdi-target</v-icon>
              Meilleur chasseur de primes
            </v-card-title>
            <v-card-text class="text-center pa-4">
              <v-avatar size="100" class="mb-4">
                <v-img
                  v-if="topBountyHunter?.profile_image_path"
                  :src="topBountyHunter.profile_image_path"
                  alt="Chasseur de primes"
                ></v-img>
                <v-icon v-else size="48">mdi-account</v-icon>
              </v-avatar>
              <h3 class="text-h5">{{ topBountyHunter?.username || 'Aucun chasseur' }}</h3>
              <div class="text-subtitle-1">
                {{ topBountyHunter?.bounty_count || 0 }} primes
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Classement des chasseurs -->
      <v-row class="mt-4">
        <v-col cols="12">
          <v-card>
            <v-card-title>Classement des chasseurs de primes</v-card-title>
            <v-card-text>
              <v-table>
                <thead>
                  <tr>
                    <th>Position</th>
                    <th>Joueur</th>
                    <th>Primes</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(hunter, index) in bountyHunters" :key="hunter.id">
                    <td>{{ index + 1 }}</td>
                    <td class="d-flex align-center">
                      <v-avatar size="32" class="mr-2">
                        <v-img
                          v-if="hunter.profile_image_path"
                          :src="hunter.profile_image_path"
                          alt="Avatar"
                        ></v-img>
                        <v-icon v-else>mdi-account</v-icon>
                      </v-avatar>
                      {{ hunter.username }}
                    </td>
                    <td>{{ hunter.bounty_count }}</td>
                  </tr>
                </tbody>
              </v-table>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>

    <!-- Dialogue de création de tournoi -->
    <v-dialog v-model="showCreateTournament" max-width="600px">
      <v-card>
        <v-card-title>Créer un nouveau tournoi</v-card-title>
        <v-card-text>
          <tournament-form
            @submit="handleTournamentCreate"
            @cancel="showCreateTournament = false"
            :loading="creatingTournament"
          />
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Snackbar pour les notifications -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
    >
      {{ snackbar.text }}
      <template v-slot:actions>
        <v-btn
          variant="text"
          @click="snackbar.show = false"
        >
          Fermer
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'
import { useAuthStore } from '@/stores/auth'
import { useTournamentStore } from '@/stores/tournament'
import TournamentForm from '@/components/tournament/TournamentForm.vue'

const router = useRouter()
const authStore = useAuthStore()
const tournamentStore = useTournamentStore()

const showCreateTournament = ref(false)
const isAuthenticated = computed(() => authStore.isAuthenticated)

const nextTournament = computed(() => tournamentStore.nextTournament)
const clayTokenHolder = ref(null)
const topBountyHunter = ref(null)
const bountyHunters = ref([])

const lastTournament = computed(() => tournamentStore.lastCompletedTournament)

// États de chargement
const creatingTournament = ref(false)
const registrationLoading = ref(false)
const dataLoading = ref(false)

// Snackbar pour les notifications
const snackbar = ref({
  show: false,
  text: '',
  color: 'success',
  timeout: 3000
})

// Fonctions utilitaires
const formatDate = (date) => {
  return format(new Date(date), 'PPP à HH:mm', { locale: fr })
}

const isRegistered = (tournamentId) => {
  return tournamentStore.isUserRegistered(tournamentId, authStore.user?.id)
}

// Affichage des notifications
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

const showWarning = (text) => {
  snackbar.value = {
    show: true,
    text,
    color: 'warning',
    timeout: 4000
  }
}

// Actions avec gestion d'erreurs améliorée
const createNewTournament = () => {
  // Vérifier si l'utilisateur a une ligue
  if (!authStore.user?.league_id) {
    showWarning("Vous devez rejoindre une ligue pour créer un tournoi. Rendez-vous dans la section Ligues.")
    return
  }
  showCreateTournament.value = true
}

const handleTournamentCreate = async (tournamentData) => {
  creatingTournament.value = true
  try {
    const createdTournament = await tournamentStore.createTournament(tournamentData)
    showSuccess("Tournoi créé avec succès")
    showCreateTournament.value = false
    router.push(`/tournaments/${createdTournament.id}`)
  } catch (error) {
    console.error('Erreur lors de la création du tournoi:', error)
    const errorMessage = error.response?.data?.detail || "Erreur lors de la création du tournoi"
    showError(errorMessage)
  } finally {
    creatingTournament.value = false
  }
}

const registerToTournament = async (tournamentId) => {
  if (registrationLoading.value) return
  
  registrationLoading.value = true
  try {
    // Vérifier si l'utilisateur a une ligue
    if (!authStore.user?.league_id) {
      showWarning("Vous devez rejoindre une ligue pour vous inscrire à un tournoi")
      return
    }

    await tournamentStore.registerPlayer(tournamentId)
    showSuccess("Inscription au tournoi réussie")
    await loadTournaments()
  } catch (error) {
    console.error('Erreur lors de l\'inscription:', error)
    // Extraction du message d'erreur spécifique du backend
    const errorMessage = error.response?.data?.detail || "Erreur lors de l'inscription au tournoi"
    showError(errorMessage)
  } finally {
    registrationLoading.value = false
  }
}

const unregisterFromTournament = async (tournamentId) => {
  if (registrationLoading.value) return
  
  registrationLoading.value = true
  try {
    await tournamentStore.unregisterPlayer(tournamentId)
    showSuccess("Désinscription du tournoi réussie")
    await loadTournaments()
  } catch (error) {
    console.error('Erreur lors de la désinscription:', error)
    const errorMessage = error.response?.data?.detail || "Erreur lors de la désinscription"
    showError(errorMessage)
  } finally {
    registrationLoading.value = false
  }
}

// Chargement initial des données
onMounted(async () => {
  if (isAuthenticated.value) {
    dataLoading.value = true
    try {
      await Promise.all([
        loadTournaments(),
        fetchClayTokenHolder(),
        fetchBountyHunters()
      ])
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error)
      showError('Erreur lors du chargement des données initiales')
    } finally {
      dataLoading.value = false
    }
  }
})

const loadTournaments = async () => {
  try {
    await tournamentStore.fetchTournaments()
  } catch (error) {
    console.error('Erreur lors du chargement des tournois:', error)
    throw error // Propager l'erreur pour la gestion dans onMounted
  }
}

const fetchClayTokenHolder = async () => {
  try {
    const response = await authStore.getCurrentClayTokenHolder()
    clayTokenHolder.value = response
  } catch (error) {
    console.error('Erreur lors de la récupération du détenteur du jeton:', error)
    throw error
  }
}

const fetchBountyHunters = async () => {
  try {
    const response = await authStore.getBountyHuntersRanking()
    bountyHunters.value = response
    if (response.length > 0) {
      topBountyHunter.value = response[0]
    }
  } catch (error) {
    console.error('Erreur lors de la récupération du classement:', error)
    throw error
  }
}
</script>