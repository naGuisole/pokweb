<!-- src/components/tournament/TournamentForm.vue -->
<template>
  <v-form ref="form" v-model="valid" @submit.prevent="handleSubmit">
    <v-card variant="elevated" class="mb-6">
      <v-card-item class="bg-primary pb-2">
        <v-card-title class="text-white font-weight-bold">
          {{ editMode ? 'Modifier un tournoi' : 'Créer un nouveau tournoi' }}
        </v-card-title>
        <v-card-subtitle class="text-white">
          Configurez les paramètres de votre tournoi
        </v-card-subtitle>
      </v-card-item>

      <v-card-text class="pt-4">
        <!-- Informations de base avec design amélioré -->
        <div class="section-title d-flex align-center mb-2">
          <v-icon icon="mdi-information-outline" color="primary" class="mr-2" />
          <h3 class="text-h6 font-weight-medium">Informations générales</h3>
        </div>
        <v-divider class="mb-4"></v-divider>

        <v-row dense>
          <v-col cols="12">
            <v-text-field
              v-model="formData.name"
              label="Nom du tournoi"
              variant="outlined"
              density="comfortable"
              color="primary"
              :rules="nameRules"
              prepend-inner-icon="mdi-trophy"
              required
            ></v-text-field>
          </v-col>

          <v-col cols="12" md="6">
            <v-select
              v-model="formData.tournament_type"
              label="Type de tournoi"
              :items="tournamentTypes"
              item-title="label"
              item-value="value"
              variant="outlined"
              density="comfortable"
              color="primary"
              prepend-inner-icon="mdi-cards-playing"
              :rules="[v => !!v || 'Le type de tournoi est requis']"
              required
            ></v-select>
          </v-col>

          <v-col cols="12" md="6">
            <v-text-field
              v-model.number="formData.buy_in"
              label="Buy-in (€)"
              type="number"
              variant="outlined"
              density="comfortable"
              color="primary"
              prepend-inner-icon="mdi-currency-eur"
              :rules="buyInRules"
              required
            ></v-text-field>
          </v-col>
        </v-row>

        <!-- Date et heure avec v-date-picker -->
        <div class="section-title d-flex align-center mt-4 mb-2">
          <v-icon icon="mdi-calendar-clock" color="primary" class="mr-2" />
          <h3 class="text-h6 font-weight-medium">Planification</h3>
        </div>
        <v-divider class="mb-4"></v-divider>

        <v-row dense>
          <v-col cols="12">
            <v-menu
              v-model="showDatePicker"
              :close-on-content-click="false"
              transition="scale-transition"
              min-width="auto"
            >
              <template v-slot:activator="{ props }">
                <v-text-field
                  v-model="formattedDateTime"
                  label="Date et heure"
                  variant="outlined"
                  density="comfortable"
                  color="primary"
                  prepend-inner-icon="mdi-calendar-clock"
                  readonly
                  v-bind="props"
                  :rules="[v => !!dateTimeValue || 'La date et l\'heure sont requises']"
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="selectedDate"
                :first-day-of-week="1"
                locale="fr"
                @update:model-value="handleDateChange"
              >
                <v-spacer></v-spacer>
                <v-btn
                  text
                  color="primary"
                  @click="showDatePicker = false"
                >
                  Annuler
                </v-btn>
                <v-btn
                  text
                  color="primary"
                  @click="confirmDate"
                >
                  OK
                </v-btn>
              </v-date-picker>
            </v-menu>
            
            <!-- Sélecteur d'heure (vous pouvez ajouter cela séparément) -->
            <v-dialog
              v-model="showTimePicker"
              max-width="290px"
            >
              <template v-slot:activator="{ props }">
                <v-btn
                  variant="text"
                  v-bind="props"
                  color="primary"
                  class="mt-2"
                >
                  Changer l'heure: {{ selectedTime }}
                </v-btn>
              </template>
              <v-card>
                <v-card-title>Sélectionner l'heure</v-card-title>
                <v-card-text>
                  <v-select
                    v-model="selectedTime"
                    label="Heure"
                    :items="timeOptions"
                    variant="outlined"
                    density="comfortable"
                  ></v-select>
                </v-card-text>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn
                    text
                    color="primary"
                    @click="confirmTime"
                  >
                    OK
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-col>
        </v-row>

        <!-- Configuration du tournoi avec design amélioré -->
        <div class="section-title d-flex align-center mt-4 mb-2">
          <v-icon icon="mdi-cog-outline" color="primary" class="mr-2" />
          <h3 class="text-h6 font-weight-medium">Configuration</h3>
        </div>
        <v-divider class="mb-4"></v-divider>

        <v-row dense>
          <v-col cols="12" md="6">
            <v-text-field
              v-model.number="formData.max_players"
              label="Nombre maximum de joueurs"
              type="number"
              variant="outlined"
              density="comfortable"
              color="primary"
              prepend-inner-icon="mdi-account-group"
              :rules="maxPlayersRules"
              required
            ></v-text-field>
          </v-col>

          <v-col cols="12" md="6" v-if="formData.tournament_type === 'MTT'">
            <v-select
              v-model.number="formData.players_per_table"
              label="Joueurs par table"
              :items="[8, 9, 10]"
              variant="outlined"
              density="comfortable"
              color="primary"
              prepend-inner-icon="mdi-table-furniture"
              :rules="playersPerTableRules"
              required
            ></v-select>
          </v-col>
        </v-row>

        <!-- Configuration de la structure avec design amélioré -->
        <div class="section-title d-flex align-center mt-4 mb-2">
          <v-icon icon="mdi-chart-timeline-variant" color="primary" class="mr-2" />
          <h3 class="text-h6 font-weight-medium">Structure et Sons</h3>
        </div>
        <v-divider class="mb-4"></v-divider>

        <v-row dense>
          <v-col cols="12">
            <v-select
              v-model="formData.configuration_id"
              label="Structure du tournoi"
              :items="availableConfigurations"
              item-title="name"
              item-value="id"
              variant="outlined"
              density="comfortable"
              color="primary"
              prepend-inner-icon="mdi-format-list-bulleted"
              :rules="[v => !!v || 'La structure est requise']"
              required
            >
              <template v-slot:prepend-item>
                <v-list-item
                  title="Configurations disponibles"
                  subtitle="Sélectionnez une structure prédéfinie ou personnalisée"
                ></v-list-item>
                <v-divider class="mt-2"></v-divider>
              </template>
            </v-select>
          </v-col>

          <v-col cols="12">
            <v-select
              v-model="formData.sound_configuration_id"
              label="Configuration sonore"
              :items="availableSoundConfigs"
              item-title="name"
              item-value="id"
              variant="outlined"
              density="comfortable"
              color="primary"
              prepend-inner-icon="mdi-volume-high"
              :rules="[v => !!v || 'La configuration sonore est requise']"
              required
            ></v-select>
          </v-col>
        </v-row>

        <!-- Notes additionnelles avec design amélioré -->
        <div class="section-title d-flex align-center mt-4 mb-2">
          <v-icon icon="mdi-note-text-outline" color="primary" class="mr-2" />
          <h3 class="text-h6 font-weight-medium">Notes additionnelles</h3>
        </div>
        <v-divider class="mb-4"></v-divider>

        <v-row dense>
          <v-col cols="12">
            <v-textarea
              v-model="formData.notes"
              label="Notes"
              variant="outlined"
              density="comfortable"
              color="primary"
              prepend-inner-icon="mdi-pencil"
              rows="3"
              counter
              maxlength="500"
              placeholder="Informations complémentaires sur le tournoi..."
            ></v-textarea>
          </v-col>
        </v-row>
      </v-card-text>

      <!-- Boutons d'action avec design amélioré -->
      <v-divider></v-divider>
      <v-card-actions class="pa-4">
        <v-spacer></v-spacer>
        <v-btn
          variant="outlined"
          color="grey-darken-1"
          class="mr-4"
          prepend-icon="mdi-close"
          @click="$emit('cancel')"
        >
          Annuler
        </v-btn>
        <v-btn
          variant="elevated"
          color="primary"
          type="submit"
          :loading="loading"
          :disabled="!valid"
          prepend-icon="mdi-check"
        >
          {{ editMode ? 'Modifier' : 'Créer' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-form>
  
  <!-- Snackbar pour les messages d'erreur -->
  <v-snackbar
    v-model="snackbar.show"
    :color="snackbar.color"
    :timeout="snackbar.timeout"
    location="top"
  >
    {{ snackbar.text }}
    <template v-slot:actions>
      <v-btn
        variant="text"
        icon="mdi-close"
        @click="snackbar.show = false"
      ></v-btn>
    </template>
  </v-snackbar>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'
import { useConfigurationStore } from '@/stores/configuration'
import { useAuthStore } from '@/stores/auth'
import { useTournamentStore } from '@/stores/tournament'

const configStore = useConfigurationStore()
const authStore = useAuthStore()
const tournamentStore = useTournamentStore()

const props = defineProps({
  tournament: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'cancel', 'error'])

// État du formulaire
const form = ref(null)
const valid = ref(false)

// Valeur pour le date-time picker
const dateTimeValue = ref(null)

// Variables pour le nouveau sélecteur de date
const showDatePicker = ref(false)
const showTimePicker = ref(false)
const selectedDate = ref(null)
const selectedTime = ref('20:00')
const datePicked = ref(false)

// Options d'heures pour le sélecteur
const timeOptions = Array.from({length: 24 * 6}, (_, i) => {
  const hour = Math.floor(i / 6);
  const minute = (i % 6) * 10;
  return `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
})

// État de la snackbar
const snackbar = ref({
  show: false,
  text: '',
  color: 'error',
  timeout: 5000
})

// IDs par défaut pour les configurations
let defaultJAPTConfigId = null
let defaultSoundConfigId = null

// Configurations disponibles (à charger depuis l'API)
const availableConfigurations = ref([])
const availableSoundConfigs = ref([])

// Nombre de tournois de type JAPT existants pour auto-incrémenter le numéro
const japtCount = ref(0)

// Types de tournoi
const tournamentTypes = [
  { label: 'JAPT', value: 'JAPT' },
  { label: 'Classique', value: 'CLASSIQUE' },
  { label: 'Multi-tables', value: 'MTT' }
]

// Formulaire
const formData = ref({
  name: '',
  tournament_type: 'JAPT',
  buy_in: 20,
  date: format(new Date(), 'yyyy-MM-dd'),
  time: '20:00',
  max_players: 10,
  players_per_table: 10,
  configuration_id: null,
  sound_configuration_id: null,
  notes: '',
  league_id: authStore.user?.league_id
})

// Computed pour la date formatée
const formattedDateTime = computed(() => {
  if (!selectedDate.value) return '';
  return format(new Date(`${selectedDate.value}T${selectedTime.value}`), 'PPP à HH:mm', { locale: fr });
})

// Fonction pour confirmer la date sélectionnée
const confirmDate = () => {
  showDatePicker.value = false;
  if (datePicked.value && selectedDate.value) {
    formData.value.date = selectedDate.value;
    // Assurez-vous de créer correctement l'objet Date
    try {
      const dateTime = new Date(`${selectedDate.value}T${selectedTime.value}`);
      // Vérifier si la date est valide
      if (!isNaN(dateTime.getTime())) {
        dateTimeValue.value = dateTime.toISOString();
      } else {
        console.error("Date invalide:", selectedDate.value, selectedTime.value);
      }
    } catch (e) {
      console.error("Erreur lors de la création de la date:", e);
    }
  }
}

const handleDateChange = (newDate) => {
  datePicked.value = true;
  // S'assurer que c'est une chaîne au format YYYY-MM-DD
  selectedDate.value = newDate;
}

// Fonction pour confirmer l'heure sélectionnée
const confirmTime = () => {
  showTimePicker.value = false;
  formData.value.time = selectedTime.value;
  if (selectedDate.value) {
    const dateTime = new Date(`${selectedDate.value}T${selectedTime.value}`);
    dateTimeValue.value = dateTime.toISOString();
  }
}

// Computed
const editMode = computed(() => !!props.tournament)

// Règles de validation
const nameRules = [
  v => !!v || 'Le nom est requis',
  v => v.length >= 3 || 'Le nom doit contenir au moins 3 caractères'
]

const buyInRules = [
  v => !!v || 'Le buy-in est requis',
  v => v > 0 || 'Le buy-in doit être positif'
]

const maxPlayersRules = computed(() => [
  v => !!v || 'Le nombre de joueurs est requis',
  v => v >= 2 || 'Minimum 2 joueurs',
  v => {
    if (formData.value.tournament_type !== 'MTT') {
      return v <= 10 || 'Maximum 10 joueurs pour ce type de tournoi'
    }
    return true
  }
])

const playersPerTableRules = [
  v => {
    if (formData.value.tournament_type === 'MTT') {
      return !!v || 'Le nombre de joueurs par table est requis'
    }
    return true
  },
  v => {
    if (formData.value.tournament_type === 'MTT') {
      return v >= 8 && v <= 10 || 'Entre 8 et 10 joueurs par table'
    }
    return true
  }
]

// Méthodes
const loadConfigurations = async () => {
  try {
    // Chargement des configurations via le store
    await Promise.all([
      configStore.fetchTournamentConfigs(),
      configStore.fetchSoundConfigs(),
      tournamentStore.fetchTournaments() // Charger les tournois pour déterminer le numéro suivant
    ])
    
    availableConfigurations.value = configStore.tournamentConfigs
    availableSoundConfigs.value = configStore.soundConfigs

    // Trouver les configurations par défaut
    const japtConfig = availableConfigurations.value.find(
      config => config.name === 'JAPT Standard' && config.is_default
    )
    
    const defaultSoundConfig = availableSoundConfigs.value.find(
      config => config.name === 'Sons par défaut' && config.is_default
    )

    if (japtConfig) {
      defaultJAPTConfigId = japtConfig.id
    }
    
    if (defaultSoundConfig) {
      defaultSoundConfigId = defaultSoundConfig.id
    }

    // Si non en mode édition, initialiser avec les valeurs par défaut
    if (!editMode.value) {
      formData.value.configuration_id = defaultJAPTConfigId
      formData.value.sound_configuration_id = defaultSoundConfigId
      
      // Calculer le nom du tournoi suivant
      setNextTournamentName()
    }
  } catch (error) {
    console.error('Erreur lors du chargement des configurations:', error)
  }
}

const setNextTournamentName = () => {
  // Filtrer les tournois de type JAPT pour déterminer le dernier numéro
  if (tournamentStore.tournaments && tournamentStore.tournaments.length > 0) {
    const japtTournaments = tournamentStore.tournaments.filter(
      t => t.tournament_type === 'JAPT' && t.name.startsWith('JAPT #')
    )
    
    let maxNumber = 0
    japtTournaments.forEach(tournament => {
      // Extraire le numéro du nom "JAPT #X"
      const match = tournament.name.match(/JAPT #(\d+)/)
      if (match && match[1]) {
        const num = parseInt(match[1])
        if (!isNaN(num) && num > maxNumber) {
          maxNumber = num
        }
      }
    })
    
    // Définir le nouveau nom avec le numéro incrémenté
    formData.value.name = `JAPT #${maxNumber + 1}`
  } else {
    // S'il n'y a aucun tournoi, commencer à 1
    formData.value.name = 'JAPT #1'
  }
}

const initializeForm = () => {
  if (props.tournament) {
    const tournamentDate = new Date(props.tournament.date)
    
    // Initialiser les valeurs de date et heure
    selectedDate.value = format(tournamentDate, 'yyyy-MM-dd')
    selectedTime.value = format(tournamentDate, 'HH:mm')
    
    formData.value = {
      ...props.tournament,
      date: format(tournamentDate, 'yyyy-MM-dd'),
      time: format(tournamentDate, 'HH:mm')
    }
    
    // Initialiser dateTimeValue
    dateTimeValue.value = tournamentDate.toISOString()
  }
}

const handleSubmit = async () => {
  if (!form.value.validate()) return

  try {
    // Combiner date et heure
    const dateTime = new Date(`${formData.value.date}T${formData.value.time}`)
    
    const tournamentData = {
      ...formData.value,
      date: dateTime.toISOString(),
      league_id: authStore.user?.league_id  
    }
    
    delete tournamentData.time  // Supprime le champ time car on utilise dateTime

    if (!tournamentData.league_id) {
      showError("Vous devez être membre d'une ligue pour créer un tournoi")
      return
    }

    emit('submit', tournamentData)
  } catch (error) {
    console.error('Erreur lors de la soumission:', error)
    showError(error.message || 'Erreur lors de la soumission du formulaire')
  }
}

// Vérification de l'appartenance à une ligue
const isFormValid = computed(() => {
  return valid.value && !!authStore.user?.league_id
})

// Surveillance du type de tournoi
watch(() => formData.value.tournament_type, (newType) => {
  if (newType === 'MTT') {
    formData.value.max_players = 20
    formData.value.players_per_table = 8
  } else {
    formData.value.max_players = 10
    formData.value.players_per_table = 10
  }
  
  // Ajuster le nom du tournoi en fonction du type
  if (!editMode.value) {
    if (newType === 'JAPT') {
      setNextTournamentName()
    } else if (newType === 'CLASSIQUE') {
      formData.value.name = 'Classique'
    } else if (newType === 'MTT') {
      formData.value.name = 'Tournoi Multi-Tables'
    }
  }
})

// Méthodes pour la gestion des messages
const showError = (message) => {
  snackbar.value = {
    show: true,
    text: message,
    color: 'error',
    timeout: 5000
  }
}

const showSuccess = (message) => {
  snackbar.value = {
    show: true,
    text: message,
    color: 'success',
    timeout: 3000
  }
}

// Initialisation
onMounted(async () => {
  await loadConfigurations();
  
  // Initialiser la date et l'heure par défaut
  const now = new Date();
  now.setHours(20, 0, 0, 0); // Par défaut à 20:00
  
  // Formater comme YYYY-MM-DD sans utiliser date-fns
  selectedDate.value = now.toISOString().split('T')[0]; // Format YYYY-MM-DD
  selectedTime.value = '20:00';
  
  dateTimeValue.value = now.toISOString();
  
  if (editMode.value) {
    initializeForm();
  } else {
    // Définir la date et l'heure par défaut dans formData
    formData.value.date = selectedDate.value;
    formData.value.time = '20:00';
  }
});
</script>

<style scoped>
.section-title {
  transition: color 0.3s ease;
}

.section-title:hover {
  color: var(--v-primary-base);
}

.v-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.v-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15) !important;
}

.v-btn {
  transition: transform 0.2s ease;
}

.v-btn:hover {
  transform: translateY(-1px);
}
</style>