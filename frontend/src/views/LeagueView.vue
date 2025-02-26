<!-- src/views/LeagueView.vue -->
<template>
    <v-container>
      <!-- En-tête avec bouton de création -->
      <v-row>
        <v-col cols="12" class="d-flex align-center">
          <h1 class="text-h4">Les Ligues</h1>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            prepend-icon="mdi-plus"
            @click="showCreateLeague = true"
          >
            Nouvelle ligue
          </v-btn>
        </v-col>
      </v-row>
  
      <!-- Liste des ligues -->
      <v-row>
        <v-col cols="12">
          <v-expansion-panels>
            <v-expansion-panel
              v-for="league in leagues"
              :key="league.id"
              :disabled="!isMemberOf(league.id)"
            >
              <v-expansion-panel-title>
                <div class="d-flex align-center">
                  <div>
                    <div class="text-h6">{{ league.name }}</div>
                    <div class="text-subtitle-2">{{ league.description }}</div>
                  </div>
                  <v-spacer></v-spacer>
                  <v-chip
                    class="mr-2"
                    :color="isMemberOf(league.id) ? 'primary' : 'grey'"
                  >
                    {{ league.member_count }} membres
                  </v-chip>
                  <v-chip
                    v-if="isAdminOf(league.id)"
                    color="error"
                    class="mr-2"
                  >
                    Admin
                  </v-chip>
                </div>
              </v-expansion-panel-title>
              
              <v-expansion-panel-text>
                <v-data-table
                  :headers="tableHeaders"
                  :items="league.members"
                  :loading="loading"
                >
                  <template v-slot:item.role="{ item }">
                    <v-chip
                      :color="item.isAdmin ? 'error' : 'primary'"
                      size="small"
                    >
                      {{ item.isAdmin ? 'Admin' : 'Membre' }}
                    </v-chip>
                    <v-btn
                      v-if="isAdminOf(league.id) && !item.isAdmin"
                      icon="mdi-shield-crown"
                      variant="text"
                      size="small"
                      color="warning"
                      class="ml-2"
                      @click="promoteToAdmin(league.id, item.id)"
                    ></v-btn>
                  </template>
                </v-data-table>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-col>
      </v-row>
  
      <!-- Dialog de création de ligue -->
      <v-dialog v-model="showCreateLeague" max-width="600px">
        <v-card>
          <v-card-title>Créer une nouvelle ligue</v-card-title>
          <v-card-text>
            <v-form ref="form" v-model="valid">
              <v-text-field
                v-model="newLeague.name"
                label="Nom de la ligue"
                :rules="nameRules"
                required
              ></v-text-field>
  
              <v-textarea
                v-model="newLeague.description"
                label="Description"
                :rules="descriptionRules"
                counter
                required
              ></v-textarea>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="grey-lighten-1"
              variant="text"
              @click="showCreateLeague = false"
            >
              Annuler
            </v-btn>
            <v-btn
              color="primary"
              :loading="saving"
              :disabled="!valid"
              @click="createLeague"
            >
              Créer
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
  import { ref, computed, onMounted } from 'vue'
  import { useLeagueStore } from '@/stores/league'
  import { useAuthStore } from '@/stores/auth'
  
  const leagueStore = useLeagueStore()
  const authStore = useAuthStore()
  
  // État local
  const showCreateLeague = ref(false)
  const valid = ref(false)
  const saving = ref(false)
  const loading = ref(false)
  const form = ref(null)
  
  const newLeague = ref({
    name: '',
    description: ''
  })
  
  const snackbar = ref({
    show: false,
    text: '',
    color: 'success'
  })
  
  // En-têtes du tableau des membres
  const tableHeaders = [
    { title: 'Utilisateur', key: 'username' },
    { title: 'Nom', key: 'last_name' },
    { title: 'Prénom', key: 'first_name' },
    { title: 'Email', key: 'email' },
    { title: 'Rôle', key: 'role' }
  ]
  
  // Règles de validation
  const nameRules = [
    v => !!v || 'Le nom est requis',
    v => v.length >= 3 || 'Le nom doit contenir au moins 3 caractères',
    v => v.length <= 100 || 'Le nom ne doit pas dépasser 100 caractères'
  ]
  
  const descriptionRules = [
    v => !!v || 'La description est requise',
    v => v.length <= 500 || 'La description ne doit pas dépasser 500 caractères'
  ]
  
  // Computed
  const leagues = computed(() => leagueStore.leagues)
  const currentUser = computed(() => authStore.user)
  
  // Méthodes
  const isMemberOf = (leagueId) => {
    return currentUser.value?.league_id === leagueId
  }
  
  const isAdminOf = (leagueId) => {
    const league = leagues.value.find(l => l.id === leagueId)
    return league?.admins?.includes(currentUser.value?.id)
  }
  
  const loadLeagues = async () => {
    loading.value = true
    try {
      await leagueStore.fetchLeagues()
    } catch (error) {
      showError('Erreur lors du chargement des ligues')
    } finally {
      loading.value = false
    }
  }
  
  const createLeague = async () => {
    if (!form.value.validate()) return
  
    saving.value = true
    try {

      // Debug
      console.log('User Auth State:', authStore.isAuthenticated);
      console.log('Token:', localStorage.getItem('token'));

      await leagueStore.createLeague(newLeague.value)
      showSuccess('Ligue créée avec succès')
      showCreateLeague.value = false
      newLeague.value = { name: '', description: '' }
      await loadLeagues()
    } catch (error) {
      showError('Erreur lors de la création de la ligue')
    } finally {
      saving.value = false
    }
  }
  
  const promoteToAdmin = async (leagueId, userId) => {
    try {
      await leagueStore.addAdmin(leagueId, userId)
      showSuccess('Administrateur ajouté avec succès')
      await loadLeagues()
    } catch (error) {
      showError('Erreur lors de la promotion de l\'administrateur')
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
    loadLeagues()
  })
  </script>