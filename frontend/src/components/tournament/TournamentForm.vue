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

        <!-- Date et heure avec v-date-picker intégré -->
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
                  persistent-hint
                  hint="Cliquez pour sélectionner la date et l'heure"
                ></v-text-field>
              </template>
              
              <v-card min-width="300px">
                <v-card-title class="text-center">
                  Sélectionner la date et l'heure
                </v-card-title>
                
                <v-card-text>
                  <v-date-picker
                    v-model="selectedDate"
                    :first-day-of-week="1"
                    locale="fr"
                    width="100%"
                    @update:model-value="handleDateSelection"
                  ></v-date-picker>
                  
                  <v-divider class="my-4"></v-divider>
                  
                  <v-row align="center" class="mx-0">
                    <v-col cols="4">
                      <v-select
                        v-model="selectedHour"
                        :items="hourOptions"
                        label="Heure"
                        variant="outlined"
                        density="comfortable"
                      ></v-select>
                    </v-col>
                    <v-col cols="1" class="text-center pa-0">
                      <span class="text-h5">:</span>
                    </v-col>
                    <v-col cols="4">
                      <v-select
                        v-model="selectedMinute"
                        :items="minuteOptions"
                        label="Minute"
                        variant="outlined"
                        density="comfortable"
                      ></v-select>
                    </v-col>
                  </v-row>
                </v-card-text>
                
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn
                    text
                    color="grey-darken-1"
                    @click="showDatePicker = false"
                  >
                    Annuler
                  </v-btn>
                  <v-btn
                    text
                    color="primary"
                    @click="confirmDateTime"
                  >
                    Confirmer
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-menu>
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

// Variables pour le sélecteur de date et heure
const showDatePicker = ref(false)
const selectedDate = ref(null) // Date au format 'YYYY-MM-DD'
const selectedHour = ref('20')
const selectedMinute = ref('00')
const datePicked = ref(false)
const dateObject = ref(new Date()) // Objet Date JavaScript pour manipulations

// Options pour les sélecteurs d'heure et de minute
const hourOptions = Array.from({length: 24}, (_, i) => {
  return i.toString().padStart(2, '0');
})

const minuteOptions = Array.from({length: 12}, (_, i) => {
  return (i * 5).toString().padStart(2, '0');
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
  if (!dateObject.value) return '';
  
  try {
    // Utiliser l'objet Date directement pour le formatage
    return format(dateObject.value, 'EEEE d MMMM yyyy à HH:mm', { locale: fr });
  } catch (e) {
    console.error("Erreur lors du formatage de la date:", e);
    return 'Erreur de date';
  }
});

// Méthode pour gérer la sélection de date
const handleDateSelection = (newDate) => {
  console.log("Date sélectionnée:", newDate);
  
  // Mettre à jour dateObject sans changer l'heure
  if (typeof newDate === 'string' && newDate.includes('-')) {
    const [year, month, day] = newDate.split('-').map(Number);
    const newDateObj = new Date(dateObject.value);
    newDateObj.setFullYear(year, month - 1, day);
    dateObject.value = newDateObj;
  }
}

// Fonction pour confirmer la date et l'heure
const confirmDateTime = () => {
  try {
    // Obtenir les heures et minutes 
    const hours = parseInt(selectedHour.value);
    const minutes = parseInt(selectedMinute.value);
    
    // Mettre à jour l'objet Date en fonction de la date sélectionnée et de l'heure
    if (typeof selectedDate.value === 'string') {
      // Si c'est déjà une chaîne au format YYYY-MM-DD
      const [year, month, day] = selectedDate.value.split('-').map(Number);
      dateObject.value = new Date(year, month - 1, day, hours, minutes, 0, 0);
    } else if (selectedDate.value instanceof Date) {
      // Si c'est déjà un objet Date
      dateObject.value = new Date(selectedDate.value);
      dateObject.value.setHours(hours, minutes, 0, 0);
    } else if (selectedDate.value) {
      // Si c'est un autre format, essayer de le convertir
      const date = new Date(selectedDate.value);
      if (!isNaN(date.getTime())) {
        dateObject.value = date;
        dateObject.value.setHours(hours, minutes, 0, 0);
      }
    }
    
    // Vérifier si la date est valide
    if (!isNaN(dateObject.value.getTime())) {
      // Mettre à jour les valeurs du formulaire
      formData.value.date = format(dateObject.value, 'yyyy-MM-dd');
      formData.value.time = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
      dateTimeValue.value = dateObject.value.toISOString();
      datePicked.value = true;
      console.log("Date validée et enregistrée:", dateTimeValue.value);
    } else {
      console.error("Date invalide lors de la confirmation:", dateObject.value);
    }
  } catch (e) {
    console.error("Erreur lors de la confirmation de la date:", e);
  }
  
  // Fermer le sélecteur
  showDatePicker.value = false;
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
    try {
      console.log("Initialisation du formulaire avec tournoi:", props.tournament);
      
      const tournamentDate = new Date(props.tournament.date);
      if (isNaN(tournamentDate.getTime())) {
        throw new Error("Date de tournoi invalide");
      }
      
      // Mettre à jour l'objet date principal
      dateObject.value = tournamentDate;
      
      // Initialiser les valeurs de date et heure au format correct
      selectedDate.value = format(tournamentDate, 'yyyy-MM-dd');
      selectedHour.value = format(tournamentDate, 'HH');
      selectedMinute.value = format(tournamentDate, 'mm');
      
      // Ajuster minutes à l'intervalle de 5 minutes le plus proche si nécessaire
      const minute = parseInt(selectedMinute.value);
      const roundedMinute = Math.round(minute / 5) * 5;
      selectedMinute.value = roundedMinute.toString().padStart(2, '0');
      if (roundedMinute >= 60) {
        selectedMinute.value = '55'; // Maximum 55 minutes
      }
      
      // Extraire les IDs de configuration en utilisant à la fois les IDs directs et les objets de configuration
      let configId = null;
      if (props.tournament.configuration_id !== undefined && props.tournament.configuration_id !== null) {
        configId = props.tournament.configuration_id;
      } else if (props.tournament.configuration && props.tournament.configuration.id !== undefined) {
        configId = props.tournament.configuration.id;
      }
      
      let soundId = null;
      if (props.tournament.sound_configuration_id !== undefined && props.tournament.sound_configuration_id !== null) {
        soundId = props.tournament.sound_configuration_id;
      } else if (props.tournament.sound_configuration && props.tournament.sound_configuration.id !== undefined) {
        soundId = props.tournament.sound_configuration.id;
      }
      
      console.log("IDs extraits:", { configId, soundId });
      console.log("Configuration complète:", props.tournament.configuration);
      console.log("Sound configuration complète:", props.tournament.sound_configuration);
      
      // Mettre à jour les données du formulaire
      formData.value = {
        name: props.tournament.name,
        tournament_type: props.tournament.tournament_type,
        buy_in: props.tournament.buy_in,
        max_players: props.tournament.max_players,
        players_per_table: props.tournament.players_per_table,
        configuration_id: configId,
        sound_configuration_id: soundId,
        league_id: props.tournament.league_id,
        date: selectedDate.value,
        time: `${selectedHour.value}:${selectedMinute.value}`,
        notes: props.tournament.notes || ''
      };
      
      // Initialiser dateTimeValue
      dateTimeValue.value = tournamentDate.toISOString();
      
      console.log("Formulaire initialisé avec le tournoi existant:", {
        formData: formData.value,
        selectedDate: selectedDate.value,
        selectedHour: selectedHour.value,
        selectedMinute: selectedMinute.value,
        dateTimeValue: dateTimeValue.value,
        dateObject: dateObject.value,
        configId: configId,
        soundId: soundId
      });
    } catch (e) {
      console.error("Erreur lors de l'initialisation du formulaire:", e);
      showError("Erreur d'initialisation de la date du tournoi");
    }
  }
}

const handleSubmit = async () => {
  if (!form.value.validate()) return

  try {
    // Vérifier que nous avons une date valide
    if (!dateTimeValue.value || !dateObject.value || isNaN(dateObject.value.getTime())) {
      // Si nous n'avons pas de date valide, essayer de la construire
      if (selectedDate.value && selectedHour.value && selectedMinute.value) {
        let year, month, day;
        
        if (typeof selectedDate.value === 'string' && selectedDate.value.includes('-')) {
          [year, month, day] = selectedDate.value.split('-').map(Number);
          month -= 1; // Ajuster pour le format JavaScript (0-11)
        } else if (selectedDate.value instanceof Date) {
          year = selectedDate.value.getFullYear();
          month = selectedDate.value.getMonth();
          day = selectedDate.value.getDate();
        } else {
          throw new Error("Format de date non pris en charge");
        }
        
        const hours = parseInt(selectedHour.value);
        const minutes = parseInt(selectedMinute.value);
        
        const dateTime = new Date(year, month, day, hours, minutes, 0, 0);
        
        if (!isNaN(dateTime.getTime())) {
          dateObject.value = dateTime;
          dateTimeValue.value = dateTime.toISOString();
        } else {
          throw new Error("Date invalide. Veuillez sélectionner une date et une heure valides.");
        }
      } else {
        throw new Error("Veuillez sélectionner une date et une heure.");
      }
    }
    
    const tournamentData = {
      ...formData.value,
      date: dateTimeValue.value,
      league_id: authStore.user?.league_id  
    }
    
    delete tournamentData.time  // Supprime le champ time car on utilise dateTimeValue

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
  
  // Par défaut à 20:00
  now.setHours(20, 0, 0, 0);
  
  // Initialiser nos variables
  dateObject.value = now;
  selectedDate.value = format(now, 'yyyy-MM-dd');
  selectedHour.value = '20';
  selectedMinute.value = '00';
  
  // Sauvegarder la date complète
  dateTimeValue.value = now.toISOString();
  
  // Log pour debug
  console.log("Date initiale:", {
    selectedDate: selectedDate.value,
    selectedHour: selectedHour.value,
    selectedMinute: selectedMinute.value,
    dateTimeValue: dateTimeValue.value,
    dateObject: dateObject.value
  });
  
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