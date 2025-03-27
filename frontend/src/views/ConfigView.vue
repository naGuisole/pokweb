<!-- src/views/ConfigView.vue -->
<!-- src/views/ConfigView.vue - Template -->
<template>
  <v-container>
    <!-- En-tête -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-tabs v-model="activeTab">
            <v-tab value="configurations">Configurations de tournoi</v-tab>
            <v-tab value="structures">Structures de blindes</v-tab>
            <v-tab value="sounds">Configurations sonores</v-tab>
          </v-tabs>

          <v-card-text>
            <!-- Configurations de tournoi (1er onglet) -->
            <v-window v-model="activeTab">
              <v-window-item value="configurations">
                <v-row>
                  <v-col cols="12" class="d-flex justify-space-between align-center">
                    <h3 class="text-h6">Configurations de tournoi</h3>
                    <v-btn
                      color="primary"
                      prepend-icon="mdi-plus"
                      @click="showTournamentConfigDialog = true"
                    >
                      Nouvelle configuration
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
                      :items-per-page="10"
                    >
                      <template v-slot:item.blinds_structure="{ item }">
                        <span>{{ item.blinds_structure ? item.blinds_structure.name : 'Non configuré' }}</span>
                      </template>
                      
                      <template v-slot:item.sound_configuration="{ item }">
                        <span>{{ item.sound_configuration ? item.sound_configuration.name : 'Non configuré' }}</span>
                      </template>

                      <template v-slot:item.is_default="{ item }">
                        <v-chip
                          :color="item.is_default ? 'success' : 'grey'"
                          size="small"
                        >
                          {{ item.is_default ? 'Oui' : 'Non' }}
                        </v-chip>
                      </template>

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

              <!-- Structures de blindes (2ème onglet) -->
              <v-window-item value="structures">
                <v-row>
                  <v-col cols="12" class="d-flex justify-space-between align-center">
                    <h3 class="text-h6">Structures de blindes</h3>
                    <v-btn
                      color="primary"
                      prepend-icon="mdi-plus"
                      @click="showBlindsStructureDialog = true"
                    >
                      Nouvelle structure
                    </v-btn>
                  </v-col>
                </v-row>

                <!-- Liste des structures de blindes -->
                <v-row>
                  <v-col cols="12">
                    <v-alert
                      v-if="!blindsStructures || blindsStructures.length === 0"
                      type="info"
                      text="Aucune structure de blindes personnalisée trouvée."
                      variant="tonal"
                      class="mb-4"
                    ></v-alert>
                    
                    <v-data-table
                      v-else
                      :headers="blindsHeaders"
                      :items="blindsStructures"
                      :loading="loadingBlindsStructures"
                      :items-per-page="10"
                    >
                      <template v-slot:item.levels="{ item }">
                        <span>{{ item.structure ? item.structure.length : 0 }} niveaux</span>
                      </template>

                      <template v-slot:item.actions="{ item }">
                        <v-btn
                          icon
                          variant="text"
                          color="primary"
                          @click="viewBlindsStructure(item)"
                        >
                          <v-icon>mdi-eye</v-icon>
                        </v-btn>
                        <v-btn
                          icon
                          variant="text"
                          color="primary"
                          @click="editBlindsStructure(item)"
                        >
                          <v-icon>mdi-pencil</v-icon>
                        </v-btn>
                        <v-btn
                          icon
                          variant="text"
                          color="error"
                          @click="deleteBlindsStructure(item)"
                        >
                          <v-icon>mdi-delete</v-icon>
                        </v-btn>
                      </template>
                    </v-data-table>
                  </v-col>
                </v-row>
              </v-window-item>

              <!-- Configurations sonores (3ème onglet) -->
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
                    <v-alert
                      v-if="!soundConfigs || soundConfigs.length === 0"
                      type="info"
                      text="Aucune configuration sonore personnalisée trouvée."
                      variant="tonal"
                      class="mb-4"
                    ></v-alert>
                    
                    <v-data-table
                      v-else
                      :headers="soundHeaders"
                      :items="soundConfigs"
                      :loading="loadingSoundConfigs"
                      :items-per-page="10"
                    >
                      <template v-slot:item.sounds="{ item }">
                        <span>{{ Object.keys(item.sounds || {}).length }} sons</span>
                      </template>
                      
                      <template v-slot:item.is_default="{ item }">
                        <v-chip
                          :color="item.is_default ? 'success' : 'grey'"
                          size="small"
                        >
                          {{ item.is_default ? 'Oui' : 'Non' }}
                        </v-chip>
                      </template>

                      <template v-slot:item.actions="{ item }">
                        <v-btn
                          icon
                          variant="text"
                          color="info"
                          @click="viewSounds(item)"
                          title="Voir les sons"
                        >
                          <v-icon>mdi-eye</v-icon>
                        </v-btn>
                        <v-btn
                          icon
                          variant="text"
                          color="primary"
                          @click="editSoundConfig(item)"
                          :disabled="item.is_default"
                          title="Modifier"
                        >
                          <v-icon>mdi-pencil</v-icon>
                        </v-btn>
                        <v-btn
                          icon
                          variant="text"
                          color="error"
                          @click="deleteSoundConfig(item)"
                          :disabled="item.is_default"
                          title="Supprimer"
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
              v-model.number="tournamentConfigData.buy_in"
              label="Buy-in (€)"
              type="number"
              required
            ></v-text-field>

            <v-select
              v-model="tournamentConfigData.blinds_structure_id"
              :items="blindsStructuresSelectItems"
              label="Structure de blindes"
              :rules="[v => !!v || 'La structure de blindes est requise']"
              required
            ></v-select>

            <v-select
              v-model="tournamentConfigData.payout_structure_id"
              :items="payoutStructuresSelectItems"
              label="Structure de paiements"
              :rules="[v => !!v || 'La structure de paiements est requise']"
              required
            ></v-select>

            <v-select
              v-model="tournamentConfigData.sound_configuration_id"
              :items="soundConfigsSelectItems"
              label="Configuration sonore"
              clearable
            ></v-select>
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
            :loading="savingConfig"
          >
            Enregistrer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog pour la structure de blindes -->
    <v-dialog v-model="showBlindsStructureDialog" max-width="800px">
      <v-card>
        <v-card-title>
          {{ editingBlindsStructure ? 'Modifier la structure' : 'Nouvelle structure de blindes' }}
        </v-card-title>
        <v-card-text>
          <v-form ref="blindsStructureForm" v-model="blindsStructureValid">
            <v-text-field
              v-model="blindsStructureData.name"
              label="Nom de la structure"
              :rules="[v => !!v || 'Le nom est requis']"
              required
            ></v-text-field>

            <div class="d-flex justify-space-between align-center mt-4 mb-2">
              <h3 class="text-subtitle-1">Niveaux de blindes</h3>
              <v-btn
                color="primary"
                size="small"
                prepend-icon="mdi-plus"
                @click="addBlindLevel"
              >
                Ajouter un niveau
              </v-btn>
            </div>

            <v-alert
              v-if="!blindsStructureData.structure || blindsStructureData.structure.length === 0"
              type="warning"
              text="Ajoutez au moins un niveau de blindes"
              variant="tonal"
              class="mb-4"
            ></v-alert>

            <v-table v-else dense>
              <thead>
                <tr>
                  <th>Niveau</th>
                  <th>Petite Blinde</th>
                  <th>Grosse Blinde</th>
                  <th>Durée (min)</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(level, index) in blindsStructureData.structure" :key="index">
                  <td>{{ level.level }}</td>
                  <td>
                    <v-text-field
                      v-model.number="level.small_blind"
                      type="number"
                      density="compact"
                      variant="outlined"
                      hide-details
                    ></v-text-field>
                  </td>
                  <td>
                    <v-text-field
                      v-model.number="level.big_blind"
                      type="number"
                      density="compact"
                      variant="outlined"
                      hide-details
                    ></v-text-field>
                  </td>
                  <td>
                    <v-text-field
                      v-model.number="level.duration"
                      type="number"
                      density="compact"
                      variant="outlined"
                      hide-details
                    ></v-text-field>
                  </td>
                  <td>
                    <v-btn
                      icon
                      size="small"
                      color="error"
                      variant="text"
                      @click="removeBlindLevel(index)"
                    >
                      <v-icon>mdi-delete</v-icon>
                    </v-btn>
                  </td>
                </tr>
              </tbody>
            </v-table>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey-lighten-1"
            variant="text"
            @click="showBlindsStructureDialog = false"
          >
            Annuler
          </v-btn>
          <v-btn
            color="primary"
            @click="saveBlindsStructure"
            :disabled="!blindsStructureValid || !blindsStructureData.structure || blindsStructureData.structure.length === 0"
            :loading="savingBlindsStructure"
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
          {{ editingSoundConfig ? 'Modifier la configuration' : 'Nouvelle configuration sonore' }}
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
              prepend-icon="mdi-music-note"
              required
            ></v-file-input>

            <v-file-input
              v-model="soundFiles.level_warning"
              label="Son d'avertissement"
              accept="audio/*"
              :rules="[v => !!v || 'Ce son est requis']"
              prepend-icon="mdi-music-note"
              required
            ></v-file-input>

            <v-file-input
              v-model="soundFiles.break_start"
              label="Son de début de pause"
              accept="audio/*"
              :rules="[v => !!v || 'Ce son est requis']"
              prepend-icon="mdi-music-note"
              required
            ></v-file-input>

            <v-file-input
              v-model="soundFiles.break_end"
              label="Son de fin de pause"
              accept="audio/*"
              :rules="[v => !!v || 'Ce son est requis']"
              prepend-icon="mdi-music-note"
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
            :loading="savingSoundConfig"
          >
            Enregistrer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog pour voir la structure de blindes -->
    <v-dialog v-model="showBlindsDetailsDialog" max-width="700px">
      <v-card>
        <v-card-title>{{ selectedBlindsStructure ? selectedBlindsStructure.name : 'Structure de blindes' }}</v-card-title>
        <v-card-text>
          <v-data-table
            v-if="selectedBlindsStructure && selectedBlindsStructure.structure"
            :headers="[
              { title: 'Niveau', key: 'level', sortable: true },
              { title: 'Petite Blinde', key: 'small_blind', sortable: true },
              { title: 'Grosse Blinde', key: 'big_blind', sortable: true },
              { title: 'Durée', key: 'duration', sortable: true }
            ]"
            :items="selectedBlindsStructure.structure"
            density="compact"
            class="elevation-1"
          >
            <template v-slot:item.duration="{ item }">
              {{ item.duration }} min
            </template>
          </v-data-table>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            @click="showBlindsDetailsDialog = false"
          >
            Fermer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Nouveau Dialog pour visualiser et écouter les sons -->
    <v-dialog v-model="showSoundsDialog" max-width="600px">
      <v-card>
        <v-card-title>{{ selectedSoundConfig ? selectedSoundConfig.name : 'Configuration sonore' }}</v-card-title>
        <v-card-text>
          <v-list v-if="selectedSoundConfig && selectedSoundConfig.sounds">
            <v-list-item v-for="(soundUrl, soundName) in selectedSoundConfig.sounds" :key="soundName">
              <template v-slot:prepend>
                <v-btn 
                  icon 
                  color="primary" 
                  @click="playSound(soundUrl)"
                  :loading="currentlyPlayingSound === soundUrl"
                  :disabled="currentlyPlayingSound && currentlyPlayingSound !== soundUrl"
                >
                  <v-icon>{{ currentlyPlayingSound === soundUrl ? 'mdi-stop' : 'mdi-play' }}</v-icon>
                </v-btn>
              </template>
              <v-list-item-title>{{ getSoundTitle(soundName) }}</v-list-item-title>
              <v-list-item-subtitle>{{ getFileName(soundUrl) }}</v-list-item-subtitle>
            </v-list-item>
          </v-list>
          <v-alert v-else type="info" text="Aucun son disponible dans cette configuration" variant="tonal"></v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            @click="closeSoundsDialog"
          >
            Fermer
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

    <!-- Élément audio caché pour la lecture des sons -->
    <audio ref="audioPlayer" @ended="handleAudioEnded"></audio>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useConfigurationStore } from '@/stores/configuration'
import { storeToRefs } from 'pinia'

// Initialisation du store
const configStore = useConfigurationStore()

// Utilisation de storeToRefs pour garder la réactivité
const { 
  tournamentConfigs,
  blindsStructures,
  soundConfigs
} = storeToRefs(configStore)

// État local
const activeTab = ref('configurations')
const tournamentConfigValid = ref(false)
const blindsStructureValid = ref(false)
const soundConfigValid = ref(false)

// Dialogues
const showTournamentConfigDialog = ref(false)
const showBlindsStructureDialog = ref(false)
const showSoundConfigDialog = ref(false)
const showBlindsDetailsDialog = ref(false)

// États de chargement
const loadingTournamentConfigs = ref(false)
const loadingBlindsStructures = ref(false)
const loadingSoundConfigs = ref(false)
const savingConfig = ref(false)
const savingBlindsStructure = ref(false)
const savingSoundConfig = ref(false)

// Formulaires et données d'édition
const tournamentConfigForm = ref(null)
const blindsStructureForm = ref(null)
const soundConfigForm = ref(null)

const editingTournamentConfig = ref(null)
const editingBlindsStructure = ref(null)
const editingSoundConfig = ref(null)
const selectedBlindsStructure = ref(null)

// Données de formulaire
const tournamentConfigData = ref({
  name: '',
  tournament_type: 'JAPT',
  buy_in: 20,
  blinds_structure_id: null,
  sound_configuration_id: null,
  is_default: false,
  rebuy_levels: 0
})

const blindsStructureData = ref({
  name: '',
  structure: [],
  starting_chips: 5000
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

// Items pour les selects
const blindsStructuresSelectItems = computed(() => {
  if (!blindsStructures.value) return [];
  return blindsStructures.value.map(bs => ({
    title: bs.name,
    value: bs.id
  }));
});

const soundConfigsSelectItems = computed(() => {
  if (!soundConfigs.value) return [];
  return soundConfigs.value.map(sc => ({
    title: sc.name,
    value: sc.id
  }));
});

// En-têtes des tableaux
const tournamentHeaders = [
  { title: 'Nom', key: 'name' },
  { title: 'Type', key: 'tournament_type' },
  { title: 'Buy-in', key: 'buy_in' },
  { title: 'Structure', key: 'blinds_structure' },
  { title: 'Sons', key: 'sound_configuration' },
  { title: 'Par défaut', key: 'is_default' },
  { title: 'Actions', key: 'actions', sortable: false }
]

const blindsHeaders = [
  { title: 'Nom', key: 'name' },
  { title: 'Jetons de départ', key: 'starting_chips' },
  { title: 'Niveaux', key: 'levels' },
  { title: 'Actions', key: 'actions', sortable: false }
]

const soundHeaders = [
  { title: 'Nom', key: 'name' },
  { title: 'Sons', key: 'sounds' },
  { title: 'Par défaut', key: 'is_default' },
  { title: 'Actions', key: 'actions', sortable: false }
]

const tournamentTypes = [
  { title: 'JAPT', value: 'JAPT' },
  { title: 'Classique', value: 'CLASSIQUE' },
  { title: 'Multi-tables', value: 'MTT' }
]

// Méthodes pour la gestion des configurations
const loadConfigurations = async () => {
  loadingTournamentConfigs.value = true
  loadingBlindsStructures.value = true
  loadingSoundConfigs.value = true
  try {
    await Promise.all([
      configStore.fetchTournamentConfigs(),
      configStore.fetchBlindsStructures(),
      configStore.fetchSoundConfigs()
    ])
    console.log('Configurations chargées:', {
      tournamentConfigs: tournamentConfigs.value,
      blindsStructures: blindsStructures.value,
      soundConfigs: soundConfigs.value
    })
  } catch (error) {
    console.error('Erreur lors du chargement des configurations:', error)
    showError('Erreur lors du chargement des configurations')
  } finally {
    loadingTournamentConfigs.value = false
    loadingBlindsStructures.value = false
    loadingSoundConfigs.value = false
  }
}

// Méthodes pour les configurations de tournoi
const saveTournamentConfig = async () => {
  if (!tournamentConfigForm.value.validate()) return

  savingConfig.value = true
  try {
    if (editingTournamentConfig.value) {
      await configStore.updateTournamentConfig(
        editingTournamentConfig.value.id, 
        tournamentConfigData.value
      )
      showSuccess('Configuration mise à jour avec succès')
    } else {
      await configStore.createTournamentConfig(tournamentConfigData.value)
      showSuccess('Configuration créée avec succès')
    }
    showTournamentConfigDialog.value = false
  } catch (error) {
    console.error('Erreur lors de l\'enregistrement de la configuration:', error)
    showError('Erreur lors de l\'enregistrement de la configuration')
  } finally {
    savingConfig.value = false
  }
}

const editTournamentConfig = (config) => {
  editingTournamentConfig.value = config
  tournamentConfigData.value = {
    name: config.name,
    tournament_type: config.tournament_type,
    buy_in: config.buy_in,
    blinds_structure_id: config.blinds_structure_id,
    sound_configuration_id: config.sound_configuration_id,
    is_default: config.is_default,
    rebuy_levels: config.rebuy_levels || 0
  }
  showTournamentConfigDialog.value = true
}

const deleteTournamentConfig = async (config) => {
  if (confirm('Êtes-vous sûr de vouloir supprimer cette configuration ?')) {
    loadingTournamentConfigs.value = true
    try {
      await configStore.deleteTournamentConfig(config.id)
      showSuccess('Configuration supprimée avec succès')
    } catch (error) {
      console.error('Erreur lors de la suppression de la configuration:', error)
      showError('Erreur lors de la suppression de la configuration')
    } finally {
      loadingTournamentConfigs.value = false
    }
  }
}

// Méthodes pour les structures de blindes
const addBlindLevel = () => {
  if (!blindsStructureData.value.structure) {
    blindsStructureData.value.structure = []
  }
  
  const lastLevel = blindsStructureData.value.structure.length > 0 
    ? blindsStructureData.value.structure[blindsStructureData.value.structure.length - 1] 
    : null
  
  const newLevel = {
    level: blindsStructureData.value.structure.length + 1,
    small_blind: lastLevel ? lastLevel.small_blind * 1.5 : 25,
    big_blind: lastLevel ? lastLevel.big_blind * 1.5 : 50,
    duration: 15
  }
  
  blindsStructureData.value.structure.push(newLevel)
}

const removeBlindLevel = (index) => {
  blindsStructureData.value.structure.splice(index, 1)
  // Mise à jour des numéros de niveau
  blindsStructureData.value.structure.forEach((level, i) => {
    level.level = i + 1
  })
}

const saveBlindsStructure = async () => {
  if (!blindsStructureForm.value.validate()) return
  if (!blindsStructureData.value.structure || blindsStructureData.value.structure.length === 0) {
    showError('Ajoutez au moins un niveau de blindes')
    return
  }
  
  if (!blindsStructureData.value.starting_chips || blindsStructureData.value.starting_chips < 1000) {
    showError('Le nombre de jetons de départ doit être d\'au moins 1000')
    return
  }

  savingBlindsStructure.value = true
  try {
    if (editingBlindsStructure.value) {
      await configStore.updateBlindsStructure(
        editingBlindsStructure.value.id,
        blindsStructureData.value
      )
      showSuccess('Structure de blindes mise à jour avec succès')
    } else {
      await configStore.createBlindsStructure(blindsStructureData.value)
      showSuccess('Structure de blindes créée avec succès')
    }
    showBlindsStructureDialog.value = false
  } catch (error) {
    console.error('Erreur lors de l\'enregistrement de la structure de blindes:', error)
    showError('Erreur lors de l\'enregistrement de la structure de blindes')
  } finally {
    savingBlindsStructure.value = false
  }
}

const editBlindsStructure = (structure) => {
  editingBlindsStructure.value = structure
  blindsStructureData.value = {
    name: structure.name,
    structure: [...structure.structure],
    starting_chips: structure.starting_chips || 5000
  }
  showBlindsStructureDialog.value = true
}

const viewBlindsStructure = (structure) => {
  selectedBlindsStructure.value = structure
  showBlindsDetailsDialog.value = true
}

const deleteBlindsStructure = async (structure) => {
  if (confirm('Êtes-vous sûr de vouloir supprimer cette structure de blindes ?')) {
    loadingBlindsStructures.value = true
    try {
      await configStore.deleteBlindsStructure(structure.id)
      showSuccess('Structure de blindes supprimée avec succès')
    } catch (error) {
      console.error('Erreur lors de la suppression de la structure de blindes:', error)
      showError('Erreur lors de la suppression de la structure de blindes')
    } finally {
      loadingBlindsStructures.value = false
    }
  }
}

// Méthodes pour les configurations sonores
const saveSoundConfig = async () => {
  if (!soundConfigForm.value.validate()) return

  savingSoundConfig.value = true
  try {
    const formData = new FormData()
    formData.append('name', soundConfigData.value.name)
    
    Object.entries(soundFiles.value).forEach(([key, file]) => {
      if (file) formData.append(key, file)
    })

    if (editingSoundConfig.value) {
      await configStore.updateSoundConfig(editingSoundConfig.value.id, formData)
      showSuccess('Configuration sonore mise à jour avec succès')
    } else {
      await configStore.createSoundConfig(formData)
      showSuccess('Configuration sonore créée avec succès')
    }
    showSoundConfigDialog.value = false
  } catch (error) {
    console.error('Erreur lors de l\'enregistrement de la configuration sonore:', error)
    showError('Erreur lors de l\'enregistrement de la configuration sonore')
  } finally {
    savingSoundConfig.value = false
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
    loadingSoundConfigs.value = true
    try {
      await configStore.deleteSoundConfig(config.id)
      showSuccess('Configuration sonore supprimée avec succès')
    } catch (error) {
      console.error('Erreur lors de la suppression de la configuration sonore:', error)
      showError('Erreur lors de la suppression de la configuration sonore')
    } finally {
      loadingSoundConfigs.value = false
    }
  }
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
    buy_in: 20,
    blinds_structure_id: null,
    payout_structure_id: null,
    sound_configuration_id: null,
    is_default: false
  }
  editingTournamentConfig.value = null
}

const resetBlindsStructure = () => {
  blindsStructureData.value = {
    name: '',
    structure: []
  }
  editingBlindsStructure.value = null
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

watch(showBlindsStructureDialog, (newValue) => {
  if (!newValue) resetBlindsStructure()
})

watch(showSoundConfigDialog, (newValue) => {
  if (!newValue) resetSoundConfig()
})

// Chargement initial
onMounted(async () => {
  // Ajouter un petit délai pour s'assurer que le store est prêt
  setTimeout(() => {
    loadConfigurations()
  }, 100)
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