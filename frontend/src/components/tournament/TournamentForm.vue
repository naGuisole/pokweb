<!-- src/components/tournament/TournamentForm.vue -->
<template>
  <v-form ref="form" v-model="valid" @submit.prevent="handleSubmit">
    <v-container>
      <!-- Informations de base -->
      <v-row>
        <v-col cols="12">
          <v-text-field
            v-model="formData.name"
            label="Nom du tournoi"
            :rules="nameRules"
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
            :rules="[v => !!v || 'Le type de tournoi est requis']"
            required
          ></v-select>
        </v-col>

        <v-col cols="12" md="6">
          <v-text-field
            v-model.number="formData.buy_in"
            label="Buy-in (€)"
            type="number"
            :rules="buyInRules"
            required
          ></v-text-field>
        </v-col>
      </v-row>

      <!-- Date et heure -->
      <v-row>
        <v-col cols="12" md="6">
          <v-dialog
            ref="dateDialog"
            v-model="showDatePicker"
            persistent
            width="auto"
          >
            <template v-slot:activator="{ props }">
              <v-text-field
                v-model="formattedDate"
                label="Date"
                readonly
                v-bind="props"
                prepend-icon="mdi-calendar"
                :rules="[v => !!v || 'La date est requise']"
              ></v-text-field>
            </template>
            
            <v-date-picker
              v-model="formData.date"
              :min="minDate"
              @update:model-value="showDatePicker = false"
            ></v-date-picker>
          </v-dialog>
        </v-col>

        <v-col cols="12" md="6">
          <v-dialog
            ref="timeDialog"
            v-model="showTimePicker"
            persistent
            width="auto"
          >
            <template v-slot:activator="{ props }">
              <v-text-field
                v-model="formData.time"
                label="Heure"
                readonly
                v-bind="props"
                prepend-icon="mdi-clock"
                :rules="[v => !!v || 'L\'heure est requise']"
              ></v-text-field>
            </template>
            
            <time-selector
              v-model="formData.time"
              label="Heure"
              :rules="[v => !!v || 'L\'heure est requise']"
            ></time-selector>
          </v-dialog>
        </v-col>
      </v-row>

      <!-- Configuration du tournoi -->
      <v-row>
        <v-col cols="12" md="6">
          <v-text-field
            v-model.number="formData.max_players"
            label="Nombre maximum de joueurs"
            type="number"
            :rules="maxPlayersRules"
            required
          ></v-text-field>
        </v-col>

        <v-col cols="12" md="6" v-if="formData.tournament_type === 'MTT'">
          <v-select
            v-model.number="formData.players_per_table"
            label="Joueurs par table"
            :items="[8, 9, 10]"
            :rules="playersPerTableRules"
            required
          ></v-select>
        </v-col>
      </v-row>

      <!-- Configuration de la structure -->
      <v-row>
        <v-col cols="12">
          <v-select
            v-model="formData.configuration_id"
            label="Structure du tournoi"
            :items="availableConfigurations"
            item-title="name"
            item-value="id"
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
      </v-row>

      <!-- Configuration sonore -->
      <v-row>
        <v-col cols="12">
          <v-select
            v-model="formData.sound_configuration_id"
            label="Configuration sonore"
            :items="availableSoundConfigs"
            item-title="name"
            item-value="id"
            :rules="[v => !!v || 'La configuration sonore est requise']"
            required
          ></v-select>
        </v-col>
      </v-row>

      <!-- Notes additionnelles -->
      <v-row>
        <v-col cols="12">
          <v-textarea
            v-model="formData.notes"
            label="Notes"
            rows="3"
            counter
            maxlength="500"
          ></v-textarea>
        </v-col>
      </v-row>

      <!-- Boutons d'action -->
      <v-row>
        <v-col class="d-flex justify-end">
          <v-btn
            color="grey-lighten-1"
            variant="text"
            class="mr-4"
            @click="$emit('cancel')"
          >
            Annuler
          </v-btn>
          <v-btn
            color="primary"
            type="submit"
            :loading="loading"
            :disabled="!valid"
          >
            {{ editMode ? 'Modifier' : 'Créer' }}
          </v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-form>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { format } from 'date-fns'
import { fr } from 'date-fns/locale'
import TimeSelector from '@/components/common/TimeSelector.vue'
import { useConfigurationStore } from '@/stores/configuration'
import { useAuthStore } from '@/stores/auth'


const configStore = useConfigurationStore()
const authStore = useAuthStore()


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

const emit = defineEmits(['submit', 'cancel'])

// État du formulaire
const form = ref(null)
const valid = ref(false)
const showDatePicker = ref(false)
const showTimePicker = ref(false)

// État des dialogues
const dateDialog = ref(null)
const timeDialog = ref(null)

// Configurations disponibles (à charger depuis l'API)
const availableConfigurations = ref([])
const availableSoundConfigs = ref([])

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
  league_id: authStore.user?.league_id  // Ajout du league_id
})

// Computed
const editMode = computed(() => !!props.tournament)

const formattedDate = computed(() => {
  return format(new Date(formData.value.date), 'PPP', { locale: fr })
})

const minDate = computed(() => {
  return format(new Date(), 'yyyy-MM-dd')
})

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
      configStore.fetchSoundConfigs()
    ])
    
    availableConfigurations.value = configStore.tournamentConfigs
    availableSoundConfigs.value = configStore.soundConfigs
  } catch (error) {
    console.error('Erreur lors du chargement des configurations:', error)
  }
}

const initializeForm = () => {
  if (props.tournament) {
    const tournamentDate = new Date(props.tournament.date)
    formData.value = {
      ...props.tournament,
      date: format(tournamentDate, 'yyyy-MM-dd'),
      time: format(tournamentDate, 'HH:mm')
    }
  }
}

const handleSubmit = async () => {
  const { valid } = await form.value.validate()
  if (!valid) return

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
      throw new Error("Vous devez être membre d'une ligue pour créer un tournoi")
    }

    emit('submit', tournamentData)
  } catch (error) {
    console.error('Erreur lors de la soumission:', error)
  }
}

// Vérification de l'appartenance à une ligue
const isFormValid = computed(() => {
  return valid.value && !!authStore.user?.league_id  // Vérifie aussi l'appartenance à une ligue
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
})

// Initialisation
onMounted(async () => {
  await loadConfigurations()
  if (editMode.value) {
    initializeForm()
  }
})
</script>