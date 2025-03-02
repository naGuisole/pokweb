<!-- src/views/ProfileView.vue -->
<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title class="text-h5 d-flex align-center">
            <span>Profil Utilisateur</span>
            <v-spacer></v-spacer>
            <v-btn
              v-if="!editing"
              color="primary"
              @click="startEditing"
              prepend-icon="mdi-pencil"
            >
              Modifier
            </v-btn>
          </v-card-title>

          <v-card-text>
            <v-row>
              <!-- Photo de profil -->
              <v-col cols="12" sm="4" class="text-center">
                <profile-image
                  :path="profileImagePreview || user?.profile_image_path"
                  :size="150"
                  :alt="user?.username || 'Avatar'"
                />

                <v-file-input
                  v-if="editing"
                  v-model="newProfileImage"
                  accept="image/*"
                  label="Changer la photo"
                  prepend-icon="mdi-camera"
                  class="mt-4"
                  hide-details
                  @update:model-value="handleImagePreview"
                ></v-file-input>
              </v-col>

              <!-- Informations utilisateur -->
              <v-col cols="12" sm="8">
                <v-form ref="form" v-model="valid">
                  <v-text-field
                    v-model="profileData.email"
                    label="Email"
                    :readonly="true"
                    prepend-inner-icon="mdi-email"
                    class="mb-4"
                  ></v-text-field>

                  <v-text-field
                    v-model="profileData.username"
                    label="Nom d'utilisateur"
                    :readonly="true"
                    prepend-inner-icon="mdi-account"
                    class="mb-4"
                  ></v-text-field>

                  <v-text-field
                    v-model="profileData.first_name"
                    label="Prénom"
                    :readonly="!editing"
                    prepend-inner-icon="mdi-badge-account-horizontal-outline"
                    :rules="nameRules"
                    class="mb-4"
                  ></v-text-field>

                  <v-text-field
                    v-model="profileData.last_name"
                    label="Nom"
                    :readonly="!editing"
                    prepend-inner-icon="mdi-badge-account-horizontal-outline"
                    :rules="nameRules"
                    class="mb-4"
                  ></v-text-field>

                  <v-text-field
                    v-model="profileData.address"
                    label="Adresse"
                    :readonly="!editing"
                    prepend-inner-icon="mdi-map-marker"
                    class="mb-4"
                  ></v-text-field>

                  <!-- Affichage de la ligue (toujours en lecture seule) -->
                  <v-card variant="outlined" class="pa-4 mb-4">
                    <div class="d-flex align-center">
                      <v-icon color="primary" class="mr-3">mdi-shield-home</v-icon>
                      <div>
                        <div class="text-subtitle-1">Ligue</div>
                        <div class="text-body-1 font-weight-bold">{{ userLeague?.name || 'Aucune ligue' }}</div>
                      </div>
                    </div>
                    <div class="text-caption text-grey mt-2">
                      Pour changer de ligue ou en créer une nouvelle, veuillez vous rendre dans la section 
                      <v-btn variant="text" color="primary" size="small" to="/leagues" class="px-1 py-0">
                        <v-icon size="small" class="mr-1">mdi-cards-playing</v-icon>
                        Ligues
                      </v-btn>
                    </div>
                  </v-card>

                  <!-- Boutons de contrôle en mode édition -->
                  <v-row v-if="editing">
                    <v-col>
                      <v-btn
                        block
                        color="primary"
                        @click="saveChanges"
                        :loading="saving"
                        :disabled="!valid"
                      >
                        Enregistrer
                      </v-btn>
                    </v-col>
                    <v-col>
                      <v-btn
                        block
                        color="error"
                        @click="cancelEditing"
                        :disabled="saving"
                      >
                        Annuler
                      </v-btn>
                    </v-col>
                  </v-row>
                </v-form>
              </v-col>
            </v-row>

            <!-- Statistiques -->
            <v-divider class="my-4"></v-divider>
            <v-row>
              <v-col cols="12">
                <h3 class="text-h6 mb-4">Statistiques</h3>
                <v-row>
                  <v-col cols="12" sm="6" md="3">
                    <v-card>
                      <v-card-text class="text-center">
                        <div class="text-h4">{{ userStats.totalGames || 0 }}</div>
                        <div class="text-subtitle-1">Parties jouées</div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="12" sm="6" md="3">
                    <v-card>
                      <v-card-text class="text-center">
                        <div class="text-h4">{{ userStats.victories || 0 }}</div>
                        <div class="text-subtitle-1">Victoires</div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="12" sm="6" md="3">
                    <v-card>
                      <v-card-text class="text-center">
                        <div class="text-h4">{{ userStats.bountyCount || 0 }}</div>
                        <div class="text-subtitle-1">Primes obtenues</div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="12" sm="6" md="3">
                    <v-card>
                      <v-card-text class="text-center">
                        <div class="text-h4">{{ `${userStats.roi || 0}%` }}</div>
                        <div class="text-subtitle-1">ROI</div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <v-card class="mt-4">
          <v-card-text class="text-center">
            <v-btn
              color="error"
              prepend-icon="mdi-logout"
              @click="handleLogout"
            >
              Se déconnecter
            </v-btn>
          </v-card-text>
        </v-card>

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
      </v-col>
    </v-row>
  </v-container>
</template>
  
<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useLeagueStore } from '@/stores/league'
import ProfileImage from '@/components/common/ProfileImage.vue';

const authStore = useAuthStore()
const leagueStore = useLeagueStore()
const router = useRouter()
const user = computed(() => authStore.user)
  
// État du formulaire
const form = ref(null)
const valid = ref(true)
const editing = ref(false)
const saving = ref(false)
const userLeague = ref(null)
  
// Données du profil
const profileData = reactive({
  email: '',
  username: '',
  first_name: '',
  last_name: '',
  address: ''
})
  
// Image de profil
const newProfileImage = ref(null)
const profileImagePreview = ref(null)
  
// Statistiques utilisateur
const userStats = reactive({
  totalGames: 0,
  victories: 0,
  bountyCount: 0,
  roi: 0
})
  
// Snackbar pour les notifications
const snackbar = reactive({
  show: false,
  text: '',
  color: 'success'
})
  
// Règles de validation
const nameRules = [
  v => !!v || 'Ce champ est requis',
  v => v.length >= 2 || 'Minimum 2 caractères'
]
  
// Initialisation des données
onMounted(async () => {
  if (user.value) {
    Object.assign(profileData, user.value)
    
    await Promise.all([
      fetchUserStats(),
      fetchUserLeague(),
    ])
  }
})

// Récupération de la ligue de l'utilisateur
const fetchUserLeague = async () => {
  try {
    if (user.value?.league_id) {
      await leagueStore.fetchLeague(user.value.league_id)
      userLeague.value = leagueStore.currentLeague
    } else {
      userLeague.value = null
    }
  } catch (error) {
    console.error('Erreur lors du chargement de la ligue:', error)
    showError('Erreur lors du chargement de la ligue')
  }
}

// Récupération des statistiques
const fetchUserStats = async () => {
  try {
    const stats = await authStore.fetchUserStats()
    Object.assign(userStats, stats)
  } catch (error) {
    showError('Erreur lors du chargement des statistiques')
  }
}

// Récupération de l'URL de l'image
const getProfileImageUrl = (path) => {
  if (!path) return null;
  // Si le chemin commence déjà par http ou blob, on le retourne tel quel
  if (path.startsWith('http') || path.startsWith('blob')) {
    return path;
  }
  // Sinon on préfixe avec l'URL de l'API
  return `${import.meta.env.VITE_API_URL}/${path}`;
};
  
// Gestion de l'édition
const startEditing = () => {
  editing.value = true
}
  
const clearImagePreview = () => {
  if (profileImagePreview.value) {
    URL.revokeObjectURL(profileImagePreview.value)
    profileImagePreview.value = null
  }
}

const cancelEditing = () => {
  editing.value = false
  Object.assign(profileData, user.value)
  newProfileImage.value = null
  clearImagePreview()
}
  
// Prévisualisation de l'image
const handleImagePreview = (file) => {
  if (!file) {
    profileImagePreview.value = null
    return
  }
  profileImagePreview.value = URL.createObjectURL(file)
}
  
// Sauvegarde des modifications
const saveChanges = async () => {
  if (!form.value.validate()) return

  saving.value = true
  try {
    // Préparation des données de mise à jour
    const updateData = {
      ...profileData,
      // Conserver la ligue_id actuelle, car on ne peut pas la changer ici
      league_id: user.value.league_id
    }

    console.log('Données envoyées:', updateData)

    // Mise à jour du profil
    await authStore.updateProfile(updateData)

    // Upload de la nouvelle image si nécessaire
    if (newProfileImage.value) {
      console.log("MAJ Image")
      await authStore.uploadProfileImage(newProfileImage.value)
    }

    editing.value = false
    clearImagePreview()
    showSuccess('Profil mis à jour avec succès')
  } catch (error) {
    showError('Erreur lors de la mise à jour du profil')
  } finally {
    saving.value = false
  }
}

// Déloggage
const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
  
// Gestion des notifications
const showSuccess = (text) => {
  snackbar.color = 'success'
  snackbar.text = text
  snackbar.show = true
}
  
const showError = (text) => {
  snackbar.color = 'error'
  snackbar.text = text
  snackbar.show = true
}
</script>
  
<style scoped>
.v-card-text {
  padding-top: 20px;
}
</style>