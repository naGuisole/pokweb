<!-- src/views/LeagueView.vue -->
<template>
  <v-container>
    <!-- En-tête avec bouton de création -->
    <v-row>
      <v-col cols="12" class="d-flex align-center">
        <h1 class="text-h4">Les Ligues</h1>
        <v-spacer></v-spacer>
        <v-btn-group>
          <v-btn
            v-if="!currentUser.league_id"
            color="secondary"
            prepend-icon="mdi-account-group"
            @click="showJoinLeague = true"
            class="mr-2"
          >
            Rejoindre une ligue
          </v-btn>
          <v-btn
            color="primary"
            prepend-icon="mdi-plus"
            @click="showCreateLeague = true"
          >
            Nouvelle ligue
          </v-btn>
        </v-btn-group>
      </v-col>
    </v-row>

    <!-- Affichage de la ligue de l'utilisateur actuel -->
    <!-- <v-card v-if="getUserLeague" class="mb-4">
      <v-card-title class="bg-primary text-white">
        Ma ligue: {{ getUserLeague.name }}
      </v-card-title>
      <v-card-text>
        <div class="d-flex align-center">
          <div>
            <div class="text-body-1">{{ getUserLeague.description }}</div>
            <div class="mt-2">
              <v-chip color="error" v-if="isLeagueAdminRobust(getUserLeague.id)">Administrateur</v-chip>
              <v-chip color="primary" v-else>Membre</v-chip>
            </div>
          </div>
        </div>
      </v-card-text>
    </v-card> -->

    <!-- Liste des ligues -->
    <v-row>
      <v-col cols="12">
        <v-expansion-panels v-model="expandedPanels" multiple>
          <!-- Ligues dont l'utilisateur est membre en premier -->
          <template v-for="(league, index) in sortedLeagues" :key="league.id">
            <v-expansion-panel
              :elevation="isUserLeague(league) ? 4 : 1"
              :class="{'user-league': isUserLeague(league)}"
            >
              <v-expansion-panel-title>
                <div class="d-flex align-center w-100">
                  <div>
                    <div v-if="isUserLeague(league)" class="league-badge mb-1">
                      <v-chip color="primary" size="small">Votre ligue</v-chip>
                    </div>
                    <div class="text-h6">{{ league.name }}</div>
                    <div class="text-subtitle-2">{{ league.description }}</div>
                  </div>
                  <v-spacer></v-spacer>
                  <div class="d-flex align-center">
                    <v-chip
                      v-if="isLeagueAdminRobust(league.id)"
                      color="error"
                      class="mr-2"
                    >
                      Admin
                    </v-chip>
                    <v-chip
                      v-else-if="isMemberOf(league.id)"
                      color="primary"
                      class="mr-2"
                    >
                      Membre
                    </v-chip>
                    <v-chip
                      v-else-if="isPendingMember(league.id)"
                      color="warning"
                      class="mr-2"
                    >
                      En attente
                    </v-chip>
                    <v-chip
                      class="mr-2"
                      :color="isMemberOf(league.id) ? 'primary' : 'grey'"
                    >
                      {{ league.members?.length || 0 }} membres
                    </v-chip>
                    <v-btn
                      v-if="!isMemberOf(league.id) && !isPendingMember(league.id) && !currentUser.league_id"
                      size="small"
                      color="primary"
                      @click.stop="joinSpecificLeague(league.id)"
                    >
                      Rejoindre
                    </v-btn>
                  </div>
                </div>
              </v-expansion-panel-title>

              <v-expansion-panel-text>
                <!-- Onglets pour les admins: Membres / Membres en attente -->
                <v-tabs v-if="isLeagueAdminRobust(league.id)" v-model="activeTab">
                  <v-tab value="members">Membres</v-tab>
                  <v-tab value="pending">En attente ({{ getPendingMembers(league).length }})</v-tab>
                </v-tabs>

                <v-window v-if="isLeagueAdminRobust(league.id)" v-model="activeTab">
                  <!-- Membres actifs -->
                  <v-window-item value="members">
                    <v-data-table
                      :headers="memberHeaders"
                      :items="getApprovedMembers(league)"
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
                          v-if="isLeagueAdminRobust(league.id) && !item.isAdmin && item.id !== currentUser.id"
                          icon="mdi-shield-crown"
                          variant="text"
                          size="small"
                          color="warning"
                          class="ml-2"
                          title="Promouvoir comme admin"
                          @click="promoteToAdmin(league.id, item.id)"
                        ></v-btn>
                      </template>
                    </v-data-table>
                  </v-window-item>

                  <!-- Membres en attente -->
                  <v-window-item value="pending">
                    <v-data-table
                      :headers="pendingHeaders"
                      :items="getPendingMembers(league)"
                      :loading="loading"
                      no-data-text="Aucun membre en attente d'approbation"
                    >
                      <template v-slot:item.actions="{ item }">
                        <v-btn-group>
                          <v-btn
                            color="success"
                            size="small"
                            prepend-icon="mdi-check"
                            @click="approveMember(league.id, item.id)"
                          >
                            Approuver
                          </v-btn>
                          <v-btn
                            color="error"
                            size="small"
                            prepend-icon="mdi-close"
                            @click="rejectMember(league.id, item.id)"
                          >
                            Refuser
                          </v-btn>
                        </v-btn-group>
                      </template>
                    </v-data-table>
                  </v-window-item>
                </v-window>

                <!-- Vue simple pour les membres non-admin -->
                <div v-else>
                  <v-data-table
                    :headers="memberHeaders"
                    :items="getApprovedMembers(league)"
                    :loading="loading"
                  >
                    <template v-slot:item.role="{ item }">
                      <v-chip
                        :color="item.isAdmin ? 'error' : 'primary'"
                        size="small"
                      >
                        {{ item.isAdmin ? 'Admin' : 'Membre' }}
                      </v-chip>
                    </template>
                  </v-data-table>
                </div>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </template>
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

    <!-- Dialog pour rejoindre une ligue -->
    <v-dialog v-model="showJoinLeague" max-width="600px">
      <v-card>
        <v-card-title>Rejoindre une ligue</v-card-title>
        <v-card-text>
          <v-select
            v-model="selectedLeagueToJoin"
            :items="availableLeaguesToJoin"
            item-title="name"
            item-value="id"
            label="Sélectionnez une ligue"
            :rules="[v => !!v || 'Veuillez sélectionner une ligue']"
            required
          ></v-select>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey-lighten-1"
            variant="text"
            @click="showJoinLeague = false"
          >
            Annuler
          </v-btn>
          <v-btn
            color="primary"
            :loading="saving"
            :disabled="!selectedLeagueToJoin"
            @click="joinLeague"
          >
            Rejoindre
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
import { useLeagueStore } from '@/stores/league'
import { useAuthStore } from '@/stores/auth'

const leagueStore = useLeagueStore()
const authStore = useAuthStore()

// État local
const showCreateLeague = ref(false)
const showJoinLeague = ref(false)
const valid = ref(false)
const saving = ref(false)
const loading = ref(false)
const form = ref(null)
const activeTab = ref('members')
const expandedPanels = ref([0]) // Premier panel ouvert par défaut

const newLeague = ref({
  name: '',
  description: ''
})

const selectedLeagueToJoin = ref(null)

const snackbar = ref({
  show: false,
  text: '',
  color: 'success'
})

// En-têtes du tableau des membres
const memberHeaders = [
  { title: 'Utilisateur', key: 'username' },
  { title: 'Nom', key: 'last_name' },
  { title: 'Prénom', key: 'first_name' },
  { title: 'Email', key: 'email' },
  { title: 'Rôle', key: 'role' }
]

// En-têtes du tableau des membres en attente
const pendingHeaders = [
  { title: 'Utilisateur', key: 'username' },
  { title: 'Nom', key: 'last_name' },
  { title: 'Prénom', key: 'first_name' },
  { title: 'Email', key: 'email' },
  { title: 'Actions', key: 'actions', sortable: false }
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
const leagues = computed(() => leagueStore.getAvailableLeagues || [])
const currentUser = computed(() => authStore.user)

// Computed pour récupérer facilement la ligue de l'utilisateur
const getUserLeague = computed(() => {
  if (!currentUser.value?.league_id) return null;
  return leagues.value.find(l => l.id === currentUser.value.league_id) || null;
});

// Trier les ligues pour placer celle de l'utilisateur en haut
const sortedLeagues = computed(() => {
  if (!leagues.value || leagues.value.length === 0) {
    return [];
  }

  return [...leagues.value].sort((a, b) => {
    // Si l'utilisateur est membre d'une ligue, elle va en haut
    if (isMemberOf(a.id) && !isMemberOf(b.id)) return -1;
    if (!isMemberOf(a.id) && isMemberOf(b.id)) return 1;

    // Si l'utilisateur est admin d'une ligue, elle va en haut
    if (isLeagueAdminRobust(a.id) && !isLeagueAdminRobust(b.id)) return -1;
    if (!isLeagueAdminRobust(a.id) && isLeagueAdminRobust(b.id)) return 1;

    // Par défaut, tri par nom
    return a.name.localeCompare(b.name);
  });
})

// Ligues disponibles pour rejoindre (celles dont l'utilisateur n'est pas membre)
const availableLeaguesToJoin = computed(() => {
  if (!currentUser.value || !leagues.value) return []
  return leagues.value.filter(league =>
    !isMemberOf(league.id) && !isPendingMember(league.id)
  )
})

// Méthodes améliorées pour vérifier le statut de l'utilisateur
const isMemberOf = (leagueId) => {
  // Vérifie directement si l'ID de la ligue de l'utilisateur correspond
  return currentUser.value?.league_id === leagueId &&
         currentUser.value?.member_status === 'APPROVED';
}

// Méthode pour vérifier si l'utilisateur est admin (ancienne méthode, gardée pour compatibilité)
const isAdminOf = (leagueId) => {
  const league = leagues.value.find(l => l.id === leagueId)
  return league?.admins?.includes(currentUser.value?.id) || false
}

// Méthode alternative qui vérifie directement avec le store des ligues
const isLeagueAdmin = (leagueId) => {
  // Vérifier si l'utilisateur est dans la liste des administrateurs de la ligue
  const league = leagueStore.leagues.find(l => l.id === leagueId);
  const adminIds = league?.admins?.map(admin => admin.id) || [];
  return adminIds.includes(currentUser.value?.id);
}

// Une méthode plus robuste qui combine les approches
const isLeagueAdminRobust = (leagueId) => {
  // Vérifie si l'utilisateur est membre de cette ligue
  if (currentUser.value?.league_id !== leagueId) return false;

  // Vérifie si le flag is_league_admin existe
  if (currentUser.value?.is_league_admin === true) return true;

  // Vérifie si le flag administered_league existe et correspond
  if (currentUser.value?.administered_league &&
      currentUser.value.administered_league.id === leagueId) {
    return true;
  }

  // Vérifie par ID dans le tableau admins de la ligue
  return isAdminByUserId(leagueId);
};

// Méthode pour vérifier si l'utilisateur est en attente d'approbation
const isPendingMember = (leagueId) => {
  return currentUser.value?.league_id === leagueId &&
         currentUser.value?.member_status === 'PENDING';
}

// Utiliser cette méthode pour afficher visuellement la ligue actuelle de l'utilisateur
const isUserLeague = (league) => {
  return currentUser.value?.league_id === league.id;
}

// Filtrer les membres approuvés
const getApprovedMembers = (league) => {
  if (!league.members) return []

  return league.members
    .filter(m => m.status !== 'PENDING')
    .map(member => ({
      ...member,
      isAdmin: league.admins?.includes(member.id) || false
    }))
}

// Filtrer les membres en attente
const getPendingMembers = (league) => {
  if (!league.members) return []
  return league.members.filter(m => m.status === 'PENDING')
}

const loadLeagues = async () => {
  loading.value = true
  try {
    await leagueStore.fetchLeagues();

    // Logs détaillés pour le débogage
    console.log('Current User (detailed):', JSON.stringify(currentUser.value, null, 2));
    console.log('User league_id:', currentUser.value?.league_id);

    leagues.value.forEach((league, index) => {
      console.log(`League ${index} (id=${league.id}, name=${league.name}):`);
      console.log('Admins property:', league.admins);
      if (Array.isArray(league.admins)) {
        console.log('Admins is array of length:', league.admins.length);
        if (league.admins.length > 0) {
          console.log('First admin item type:', typeof league.admins[0]);
          console.log('First admin item:', league.admins[0]);
        }
      } else {
        console.log('Admins is not an array, type:', typeof league.admins);
      }

      // Vérifier si l'utilisateur actuel est admin de cette ligue
      const isAdmin = isLeagueAdminRobust(league.id);
      console.log(`Current user is admin of league ${league.id}:`, isAdmin);
    });

    // Déterminer les panels à ouvrir par défaut
    if (currentUser.value?.league_id) {
      const userLeagueIndex = sortedLeagues.value.findIndex(
        l => l.id === currentUser.value.league_id
      );
      if (userLeagueIndex >= 0) {
        expandedPanels.value = [userLeagueIndex];
      }
    }
  } catch (error) {
    console.error('Erreur lors du chargement des ligues:', error);
    showError('Erreur lors du chargement des ligues');
  } finally {
    loading.value = false;
  }
};

// Vérification spécifique par ID uniquement
const isAdminByUserId = (leagueId) => {
  const league = leagues.value.find(l => l.id === leagueId);

  if (!league || !league.admins || !Array.isArray(league.admins)) return false;

  // Si les administrateurs sont des objets avec un ID
  if (league.admins.length > 0 && typeof league.admins[0] === 'object') {
    return league.admins.some(admin => admin.id === currentUser.value?.id);
  }

  // Si les administrateurs sont directement des IDs
  return league.admins.includes(currentUser.value?.id);
};

const createLeague = async () => {
  if (!form.value.validate()) return

  saving.value = true
  try {
    // Debug
    console.log('User Auth State:', authStore.isAuthenticated);
    console.log('Token:', localStorage.getItem('token'));

    await leagueStore.createLeague(newLeague.value)

    // Rafraîchir le profil utilisateur pour mettre à jour son league_id
    await authStore.fetchUserProfile()

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

const joinLeague = async () => {
  if (!selectedLeagueToJoin.value) return

  saving.value = true
  try {
    await leagueStore.joinLeague(selectedLeagueToJoin.value)
    showSuccess('Demande d\'adhésion envoyée avec succès')
    showJoinLeague.value = false
    selectedLeagueToJoin.value = null

    // Rafraîchir les données
    await loadLeagues()
    await authStore.fetchUserProfile()
  } catch (error) {
    showError('Erreur lors de la demande d\'adhésion')
  } finally {
    saving.value = false
  }
}

const joinSpecificLeague = async (leagueId) => {
  saving.value = true
  try {
    await leagueStore.joinLeague(leagueId)
    showSuccess('Demande d\'adhésion envoyée avec succès')

    // Rafraîchir les données
    await loadLeagues()
    await authStore.fetchUserProfile()
  } catch (error) {
    showError('Erreur lors de la demande d\'adhésion')
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

const approveMember = async (leagueId, userId) => {
  try {
    await leagueStore.approveMember(leagueId, userId)
    showSuccess('Membre approuvé avec succès')
    await loadLeagues()
  } catch (error) {
    showError('Erreur lors de l\'approbation du membre')
  }
}

const rejectMember = async (leagueId, userId) => {
  try {
    await leagueStore.rejectMember(leagueId, userId)
    showSuccess('Demande d\'adhésion refusée')
    await loadLeagues()
  } catch (error) {
    showError('Erreur lors du refus de la demande d\'adhésion')
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

<style scoped>
.v-expansion-panel-title {
  padding: 16px;
}

.user-league {
  border-left: 4px solid var(--v-primary-base);
  background-color: rgba(var(--v-theme-primary), 0.05);
}

.league-badge {
  position: absolute;
  top: -8px;
  left: 16px;
}
</style>