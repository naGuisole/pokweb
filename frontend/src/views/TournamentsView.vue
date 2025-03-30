<!-- src/views/TournamentsView.vue -->
<template>
  <v-container>
    <!-- Barre d'outils -->
    <v-card class="mb-4">
      <v-toolbar flat>
        <v-toolbar-title>Tournois</v-toolbar-title>
        <v-spacer></v-spacer>

        <!-- Filtres -->
        <v-btn-group class="mr-4">
          <v-select
            v-model="filters.type"
            :items="tournamentTypes"
            label="Type"
            density="comfortable"
            style="min-width: 150px"
            hide-details
          ></v-select>

          <v-select
            v-model="filters.status"
            :items="tournamentStatuses"
            label="Statut"
            density="comfortable"
            style="min-width: 150px"
            hide-details
          ></v-select>
        </v-btn-group>

        <!-- Bouton création -->
        <v-btn
          color="primary"
          prepend-icon="mdi-plus"
          @click="createTournament"
        >
          Nouveau tournoi
        </v-btn>
      </v-toolbar>
    </v-card>

    <!-- Affichage du chargement -->
    <v-row v-if="loading">
      <v-col cols="12" class="text-center">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
        <div class="mt-2">Chargement des tournois...</div>
      </v-col>
    </v-row>

    <!-- Liste des tournois -->
    <v-row v-else>
      <v-col 
        v-for="tournament in filteredTournaments"
        :key="tournament.id"
        cols="12" md="6" lg="4"
      >
        <tournament-card
          :tournament="tournament"
          @register="registerToTournament"
          @unregister="unregisterFromTournament"
          @start="startTournament"
          @edit="editTournament"
          @delete="confirmDelete"
          @pause="pauseTournament"
        />
      </v-col>

      <!-- Message si aucun tournoi -->
      <v-col v-if="filteredTournaments.length === 0" cols="12">
        <v-alert
          type="info"
          text="Aucun tournoi ne correspond aux critères de recherche"
        ></v-alert>
      </v-col>
    </v-row>

    <!-- Dialog de création/édition -->
    <v-dialog v-model="showTournamentForm" max-width="800">
      <v-card>
        <v-card-title>
          {{ editingTournament ? 'Modifier le tournoi' : 'Créer un tournoi' }}
        </v-card-title>
        <v-card-text>
          <tournament-form
            :tournament="editingTournament"
            :loading="saving"
            @submit="saveTournament"
            @cancel="closeTournamentForm"
          />
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Dialog de confirmation suppression -->
    <v-dialog v-model="showDeleteConfirm" max-width="400">
      <v-card>
        <v-card-title>Confirmer la suppression</v-card-title>
        <v-card-text>
          Êtes-vous sûr de vouloir supprimer ce tournoi ?
          Cette action est irréversible.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey-lighten-1"
            variant="text"
            @click="showDeleteConfirm = false"
          >
            Annuler
          </v-btn>
          <v-btn
            color="error"
            @click="deleteTournament"
          >
            Supprimer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar pour les notifications -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="3000"
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
import { useTournamentStore } from '@/stores/tournament'
import { useAuthStore } from '@/stores/auth'
import TournamentCard from '@/components/tournament/TournamentCard.vue'
import TournamentForm from '@/components/tournament/TournamentForm.vue'

const router = useRouter()
const tournamentStore = useTournamentStore()
const authStore = useAuthStore()

// État local
const showTournamentForm = ref(false)
const showDeleteConfirm = ref(false)
const editingTournament = ref(null)
const tournamentToDelete = ref(null)
const saving = ref(false)
const loading = ref(false)

const filters = ref({
  type: null,
  status: null
})

const snackbar = ref({
  show: false,
  text: '',
  color: 'success'
})

// Options pour les filtres
const tournamentTypes = [
  { title: 'Tous les types', value: null },
  { title: 'JAPT', value: 'JAPT' },
  { title: 'Classique', value: 'CLASSIQUE' },
  { title: 'MTT', value: 'MTT' }
]

const tournamentStatuses = [
  { title: 'Tous les statuts', value: null },
  { title: 'Planifié', value: 'PLANNED' },
  { title: 'En cours', value: 'IN_PROGRESS' },
  { title: 'Terminé', value: 'COMPLETED' }
]

// Computed
const filteredTournaments = computed(() => {
  // S'assurer que getFilteredTournaments retourne toujours un tableau
  const tournaments = tournamentStore.getFilteredTournaments
  return Array.isArray(tournaments) ? tournaments : []
})

// Synchroniser les filtres du composant avec le store
watch(filters, (newFilters) => {
  tournamentStore.filters = newFilters
  loadTournaments()
}, { deep: true })

// Méthodes
const createTournament = () => {
  editingTournament.value = null
  showTournamentForm.value = true
}

const editTournament = async (tournament) => {
    try {
      loading.value = true;
      
      console.log("Tournoi initial pour édition:", tournament);
      
      // Récupérer les données complètes du tournoi pour s'assurer d'avoir toutes les infos
      const fullTournament = await tournamentStore.fetchTournament(tournament.id);
      console.log("Données complètes du tournoi pour édition:", fullTournament);
      
      // S'assurer que nous avons bien les IDs de configuration directs
      if (!fullTournament.configuration_id && fullTournament.configuration) {
        fullTournament.configuration_id = fullTournament.configuration.id;
      }
      
      if (!fullTournament.sound_configuration_id && fullTournament.sound_configuration) {
        fullTournament.sound_configuration_id = fullTournament.sound_configuration.id;
      }
      
      // Stocker les données complètes du tournoi
      editingTournament.value = fullTournament;
      showTournamentForm.value = true;
    } catch (error) {
      console.error("Erreur lors de la récupération des données du tournoi:", error);
      showError("Erreur lors de la récupération des données du tournoi");
    } finally {
      loading.value = false;
    }
  }

const saveTournament = async (tournamentData) => {
  saving.value = true
  try {
    if (editingTournament.value) {
      await tournamentStore.updateTournament(editingTournament.value.id, tournamentData)
      showSuccess('Tournoi modifié avec succès')
    } else {
      await tournamentStore.createTournament(tournamentData)
      showSuccess('Tournoi créé avec succès')
    }
    closeTournamentForm()
    await loadTournaments()
  } catch (error) {
    console.error('Erreur lors de l\'enregistrement du tournoi:', error)
    showError('Erreur lors de l\'enregistrement du tournoi')
  } finally {
    saving.value = false
  }
}

const confirmDelete = (tournament) => {
  tournamentToDelete.value = tournament
  showDeleteConfirm.value = true
}

const deleteTournament = async () => {
  try {
    await tournamentStore.deleteTournament(tournamentToDelete.value.id)
    showSuccess('Tournoi supprimé avec succès')
    showDeleteConfirm.value = false
    await loadTournaments()
  } catch (error) {
    console.error('Erreur lors de la suppression du tournoi:', error)
    showError('Erreur lors de la suppression du tournoi')
  }
}

const registerToTournament = async (tournamentId) => {
  try {
    await tournamentStore.registerPlayer(tournamentId)
    showSuccess('Inscription réussie')
    await loadTournaments()
  } catch (error) {
    console.error('Erreur lors de l\'inscription:', error)
    showError('Erreur lors de l\'inscription')
  }
}

const unregisterFromTournament = async (tournamentId) => {
  try {
    await tournamentStore.unregisterPlayer(tournamentId)
    showSuccess('Désinscription réussie')
    await loadTournaments()
  } catch (error) {
    console.error('Erreur lors de la désinscription:', error)
    showError('Erreur lors de la désinscription')
  }
}

const startTournament = async (tournamentId) => {
  try {
    await tournamentStore.startTournament(tournamentId)
    router.push(`/tournaments/${tournamentId}`)
  } catch (error) {
    console.error('Erreur lors du démarrage du tournoi:', error)
    showError('Erreur lors du démarrage du tournoi')
  }
}

const pauseTournament = async (tournamentId) => {
  try {
    await tournamentStore.pauseTournament(tournamentId)
    await loadTournaments()
  } catch (error) {
    console.error('Erreur lors de la mise en pause du tournoi:', error)
    showError('Erreur lors de la mise en pause du tournoi')
  }
}

const closeTournamentForm = () => {
  showTournamentForm.value = false
  editingTournament.value = null
}

const loadTournaments = async () => {
  loading.value = true
  try {
    await tournamentStore.fetchTournaments()
  } catch (error) {
    console.error('Erreur lors du chargement des tournois:', error)
    showError('Erreur lors du chargement des tournois')
  } finally {
    loading.value = false
  }
}

// Notifications
const showSuccess = (text) => {
  snackbar.value = {
    show: true,
    text,
    color: 'success'
  }
}

const showError = (text) => {
  snackbar.value = {
    show: true,
    text,
    color: 'error'
  }
}

// Initialisation
onMounted(() => {
  loadTournaments()
})
</script>