<!-- src/views/ConfigView.vue -->
<template>
  <v-container>
    <!-- En-tête -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-tabs v-model="activeTab">
            <v-tab value="tournament">Structures de tournoi</v-tab>
            <v-tab value="sounds">Configuration sonore</v-tab>
          </v-tabs>

          <v-card-text>
            <!-- Configurations de tournoi -->
            <v-window v-model="activeTab">
              <v-window-item value="tournament">
                <v-row>
                  <v-col cols="12" class="d-flex justify-space-between align-center">
                    <h3 class="text-h6">Structures disponibles</h3>
                    <v-btn
                      color="primary"
                      prepend-icon="mdi-plus"
                      @click="showTournamentConfigDialog = true"
                    >
                      Nouvelle structure
                    </v-btn>
                  </v-col>
                </v-row>

                <!-- Liste des configurations de tournoi -->
                <v-row>
                  <v-col cols="12">
                    <v-data-table
                      :headers="tournamentHeaders"
                      :items="tournamentConfigs"
                      :loading="loadingTournamentConfigs"
                    >
                      <template v-slot:item.actions="{ item }">
                        <v-btn
                          icon
                          variant="text"
                          color="primary"
                          @click="editTournamentConfig(item)"
                          :disabled="item.is_default"
                        >
                          <v-icon>mdi-pencil</v-icon>
                        </v-btn>
                        <v-btn
                          icon
                          variant="text"
                          color="error"
                          @click="deleteTournamentConfig(item)"
                          :disabled="item.is_default"
                        >
                          <v-icon>mdi-delete</v-icon>
                        </v-btn>
                      </template>
                    </v-data-table>
                  </v-col>
                </v-row>
              </v-window-item>

              <!-- Configurations sonores -->
              <v-window-item value="sounds">
                <v-row>
                  <v-col cols="12" class="d-flex justify-space-between align-center">
                    <h3 class="text-h6">Configurations sonores</h3>
                    <v-btn
                      color="primary"
                      prepend-icon="mdi-plus"
                      @click="showSoundConfigDialog = true"
                    >
                      Nouvelle configuration
                    </v-btn>
                  </v-col>
                </v-row>

                <!-- Liste des configurations sonores -->
                <v-row>
                  <v-col cols="12">
                    <v-data-table
                      :headers="soundHeaders"
                      :items="soundConfigs"
                      :loading="loadingSoundConfigs"
                    >
                      <template v-slot:item.actions="{ item }">
                        <v-btn
                          icon
                          variant="text"
                          color="primary"
                          @click="editSoundConfig(item)"
                          :disabled="item.is_default"
                        >
                          <v-icon>mdi-pencil</v-icon>
                        </v-btn>
                        <v-btn
                          icon
                          variant="text"
                          color="error"
                          @click="deleteSoundConfig(item)"
                          :disabled="item.is_default"
                        >
                          <v-icon>mdi-delete</v-icon>
                        </v-btn>
                      </template>
                    </v-data-table>
                  </v-col>
                </v-row>
              </v-window-item>
            </v-window>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Dialog pour la configuration de tournoi -->
    <v-dialog v-model="showTournamentConfigDialog" max-width="800px">
      <v-card>
        <v-card-title>
          {{ editingTournamentConfig ? 'Modifier la configuration' : 'Nouvelle configuration' }}
        </v-card-title>
        <v-card-text>
          <v-form ref="tournamentConfigForm" v-model="tournamentConfigValid">
            <!-- Formulaire de configuration de tournoi -->
            <v-text-field
              v-model="tournamentConfigData.name"
              label="Nom de la configuration"
              :rules="[v => !!v || 'Le nom est requis']"
              required
            ></v-text-field>

            <v-select
              v-model="tournamentConfigData.tournament_type"
              :items="tournamentTypes"
              label="Type de tournoi"
              required
            ></v-select>

            <v-text-field
              v-model.number="tournamentConfigData.starting_chips"
              label="Jetons de départ"
              type="number"
              required
            ></v-text-field>

            <!-- Structure des blindes -->
            <v-expansion-panels>
              <v-expansion-panel title="Structure des blindes">
                <template v-slot:text>
                  <v-btn
                    color="primary"
                    @click="addBlindLevel"
                    class="mb-4"
                  >
                    Ajouter un niveau
                  </v-btn>

                  <div
                    v-for="(level, index) in tournamentConfigData.blinds_structure"
                    :key="index"
                    class="d-flex align-center mb-2"
                  >
                    <v-text-field
                      v-model.number="level.small_blind"
                      label="Petite blinde"
                      type="number"
                      class="mr-2"
                    ></v-text-field>
                    
                    <v-text-field
                      v-model.number="level.big_blind"
                      label="Grosse blinde"
                      type="number"
                      class="mr-2"
                    ></v-text-field>
                    
                    <v-text-field
                      v-model.number="level.duration"
                      label="Durée (min)"
                      type="number"
                      class="mr-2"
                    ></v-text-field>

                    <v-btn
                      icon
                      color="error"
                      variant="text"
                      @click="removeBlindLevel(index)"
                    >
                      <v-icon>mdi-delete</v-icon>
                    </v-btn>
                  </div>
                </template>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey-lighten-1"
            variant="text"
            @click="showTournamentConfigDialog = false"
          >
            Annuler
          </v-btn>
          <v-btn
            color="primary"
            @click="saveTournamentConfig"
            :disabled="!tournamentConfigValid"
          >
            Enregistrer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog pour la configuration sonore -->
    <v-dialog v-model="showSoundConfigDialog" max-width="600px">
      <v-card>
        <v-card-title>
          {{ editingSoundConfig ? 'Modifier la configuration' : 'Nouvelle configuration' }}
        </v-card-title>
        <v-card-text>
          <v-form ref="soundConfigForm" v-model="soundConfigValid">
            <v-text-field
              v-model="soundConfigData.name"
              label="Nom de la configuration"
              :rules="[v => !!v || 'Le nom est requis']"
              required
            ></v-text-field>

            <v-file-input
              v-model="soundFiles.level_start"
              label="Son de début de niveau"
              accept="audio/*"
              :rules="[v => !!v || 'Ce son est requis']"
              required
            ></v-file-input>

            <v-file-input
              v-model="soundFiles.level_warning"
              label="Son d'avertissement"
              accept="audio/*"
              :rules="[v => !!v || 'Ce son est requis']"
              required
            ></v-file-input>

            <v-file-input
              v-model="soundFiles.break_start"
              label="Son de début de pause"
              accept="audio/*"
              :rules="[v => !!v || 'Ce son est requis']"
              required
            ></v-file-input>

            <v-file-input
              v-model="soundFiles.break_end"
              label="Son de fin de pause"
              accept="audio/*"
              :rules="[v => !!v || 'Ce son est requis']"
              required
            ></v-file-input>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey-lighten-1"
            variant="text"
            @click="showSoundConfigDialog = false"
          >
            Annuler
          </v-btn>
          <v-btn
            color="primary"
            @click="saveSoundConfig"
            :disabled="!soundConfigValid"
          >
            Enregistrer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar pour les notifications -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      timeout="3000"
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
import { ref, onMounted, watch } from 'vue'
import { useConfigurationStore } from '@/stores/configuration'
import { storeToRefs } from 'pinia'

// Initialisation du store
const configStore = useConfigurationStore()

// Utilisation de storeToRefs pour garder la réactivité
const { 
  tournamentConfigs, 
  soundConfigs, 
  loading: storeLoading 
} = storeToRefs(configStore)

// État local
const activeTab = ref('tournament')
const tournamentConfigValid = ref(false)
const soundConfigValid = ref(false)
const showTournamentConfigDialog = ref(false)
const showSoundConfigDialog = ref(false)

// Formulaires et données d'édition
const tournamentConfigForm = ref(null)
const soundConfigForm = ref(null)
const editingTournamentConfig = ref(null)
const editingSoundConfig = ref(null)

const tournamentConfigData = ref({
  name: '',
  tournament_type: 'JAPT',
  starting_chips: 20000,
  blinds_structure: []
})

const soundConfigData = ref({
  name: '',
  sounds: {}
})

const soundFiles = ref({
  level_start: null,
  level_warning: null,
  break_start: null,
  break_end: null
})

// Snackbar
const snackbar = ref({
  show: false,
  color: 'success',
  text: ''
})

// Constantes
const tournamentHeaders = [
  { title: 'Nom', key: 'name' },
  { title: 'Type', key: 'tournament_type' },
  { title: 'Par défaut', key: 'is_default' },
  { title: 'Actions', key: 'actions', sortable: false }
]

const soundHeaders = [
  { title: 'Nom', key: 'name' },
  { title: 'Par défaut', key: 'is_default' },
  { title: 'Actions', key: 'actions', sortable: false }
]

const tournamentTypes = [
  { title: 'JAPT', value: 'JAPT' },
  { title: 'Classique', value: 'CLASSIQUE' },
  { title: 'Multi-tables', value: 'MTT' }
]

// Méthodes pour la gestion des configurations de tournoi
const loadConfigurations = async () => {
  try {
    await Promise.all([
      configStore.fetchTournamentConfigs(),
      configStore.fetchSoundConfigs()
    ])
  } catch (error) {
    showError('Erreur lors du chargement des configurations')
  }
}

const saveTournamentConfig = async () => {
  if (!tournamentConfigForm.value.validate()) return

  try {
    if (editingTournamentConfig.value) {
      await configStore.updateTournamentConfig(
        editingTournamentConfig.value.id, 
        tournamentConfigData.value
      )
    } else {
      await configStore.createTournamentConfig(tournamentConfigData.value)
    }
    
    showSuccess('Configuration enregistrée avec succès')
    showTournamentConfigDialog.value = false
  } catch (error) {
    showError('Erreur lors de l\'enregistrement de la configuration')
  }
}

const editTournamentConfig = (config) => {
  editingTournamentConfig.value = config
  tournamentConfigData.value = { ...config }
  showTournamentConfigDialog.value = true
}

const deleteTournamentConfig = async (config) => {
  if (confirm('Êtes-vous sûr de vouloir supprimer cette configuration ?')) {
    try {
      await configStore.deleteTournamentConfig(config.id)
      showSuccess('Configuration supprimée avec succès')
    } catch (error) {
      showError('Erreur lors de la suppression de la configuration')
    }
  }
}

// Méthodes pour la gestion des configurations sonores
const saveSoundConfig = async () => {
  if (!soundConfigForm.value.validate()) return

  try {
    const formData = new FormData()
    formData.append('name', soundConfigData.value.name)
    
    Object.entries(soundFiles.value).forEach(([key, file]) => {
      if (file) formData.append(key, file)
    })

    if (editingSoundConfig.value) {
      await configStore.updateSoundConfig(editingSoundConfig.value.id, formData)
    } else {
      await configStore.createSoundConfig(formData)
    }

    showSuccess('Configuration sonore enregistrée avec succès')
    showSoundConfigDialog.value = false
  } catch (error) {
    showError('Erreur lors de l\'enregistrement de la configuration sonore')
  }
}

const editSoundConfig = (config) => {
  editingSoundConfig.value = config
  soundConfigData.value = { name: config.name }
  soundFiles.value = {
    level_start: null,
    level_warning: null,
    break_start: null,
    break_end: null
  }
  showSoundConfigDialog.value = true
}

const deleteSoundConfig = async (config) => {
  if (confirm('Êtes-vous sûr de vouloir supprimer cette configuration sonore ?')) {
    try {
      await configStore.deleteSoundConfig(config.id)
      showSuccess('Configuration sonore supprimée avec succès')
    } catch (error) {
      showError('Erreur lors de la suppression de la configuration sonore')
    }
  }
}

// Méthodes pour la gestion des blindes
const addBlindLevel = () => {
  tournamentConfigData.value.blinds_structure.push({
    level: tournamentConfigData.value.blinds_structure.length + 1,
    small_blind: 0,
    big_blind: 0,
    duration: 15
  })
}

const removeBlindLevel = (index) => {
  tournamentConfigData.value.blinds_structure.splice(index, 1)
  // Mise à jour des numéros de niveau
  tournamentConfigData.value.blinds_structure.forEach((level, i) => {
    level.level = i + 1
  })
}

// Méthodes utilitaires
const showSuccess = (text) => {
  snackbar.value = {
    show: true,
    color: 'success',
    text
  }
}

const showError = (text) => {
  snackbar.value = {
    show: true,
    color: 'error',
    text
  }
}

// Réinitialisation des formulaires
const resetTournamentConfig = () => {
  tournamentConfigData.value = {
    name: '',
    tournament_type: 'JAPT',
    starting_chips: 20000,
    blinds_structure: []
  }
  editingTournamentConfig.value = null
}

const resetSoundConfig = () => {
  soundConfigData.value = { name: '' }
  soundFiles.value = {
    level_start: null,
    level_warning: null,
    break_start: null,
    break_end: null
  }
  editingSoundConfig.value = null
}

// Watchers
watch(showTournamentConfigDialog, (newValue) => {
  if (!newValue) resetTournamentConfig()
})

watch(showSoundConfigDialog, (newValue) => {
  if (!newValue) resetSoundConfig()
})

// Chargement initial
onMounted(() => {
  loadConfigurations()
})
</script>

<style scoped>
.v-expansion-panels {
  margin: 16px 0;
}

.blind-level {
  margin-bottom: 8px;
  border: 1px solid rgba(var(--v-border-color), 0.12);
  padding: 8px;
  border-radius: 4px;
}
</style>