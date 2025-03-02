<!-- src/components/auth/RegisterForm.vue -->
<template>
  <v-form ref="form" @submit.prevent="handleSubmit">
    <v-text-field
      v-model="requiredFormData.email"
      label="Email"
      type="email"
      prepend-inner-icon="mdi-email"
      :rules="emailRules"
      required
      autocomplete="username"
    ></v-text-field>

    <v-text-field
      v-model="requiredFormData.username"
      label="Nom d'utilisateur"
      prepend-inner-icon="mdi-account"
      :rules="usernameRules"
      required
    ></v-text-field>

    <v-text-field
      v-model="requiredFormData.first_name"
      label="Prénom"
      prepend-inner-icon="mdi-account"
      :rules="nameRules"
      required
      autocomplete="given-name"
    ></v-text-field>

    <v-text-field
      v-model="requiredFormData.last_name"
      label="Nom"
      prepend-inner-icon="mdi-account"
      :rules="nameRules"
      required
      autocomplete="family-name"
    ></v-text-field>

    <v-text-field
      v-model="requiredFormData.password"
      label="Mot de passe"
      :type="showPassword ? 'text' : 'password'"
      prepend-inner-icon="mdi-lock"
      :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
      @click:append-inner="showPassword = !showPassword"
      :rules="passwordRules"
      required
      autocomplete="new-password"
    ></v-text-field>

    <v-text-field
      v-model="optionalFormData.address"
      label="Adresse"
      prepend-inner-icon="mdi-map-marker"
      autocomplete="street-address"
    ></v-text-field>

    <!-- Sélection de ligue simplifiée -->
    <v-card variant="outlined" class="pa-4 mb-4">
      <v-select
        v-model="selectedLeagueId"
        :items="availableLeagues"
        item-title="name"
        item-value="id"
        label="Ligue (optionnel)"
        prepend-inner-icon="mdi-shield-home"
        clearable
        :loading="loadingLeagues"
        no-data-text="Aucune ligue disponible"
      >
        <template v-slot:prepend>
          <v-tooltip location="top">
            <template v-slot:activator="{ props }">
              <v-icon v-bind="props" color="info">mdi-information-outline</v-icon>
            </template>
            Vous pourrez également créer ou rejoindre une ligue plus tard
          </v-tooltip>
        </template>
      </v-select>
      <div class="text-caption text-grey mt-2">
        La sélection d'une ligue est optionnelle. Vous pourrez en créer une ou en rejoindre une plus tard.
      </div>
    </v-card>

    <!-- Input file natif pour la photo de profil -->
    <div class="custom-file-input my-4">
      <label for="profile-image" class="mb-2 d-block">Photo de profil</label>
      <input
        type="file"
        id="profile-image"
        ref="profileImageInput"
        accept="image/*"
        @change="onFileChange"
      />
      <div v-if="imagePreview" class="mt-2">
        <img :src="imagePreview" alt="Prévisualisation" style="max-width: 200px; max-height: 200px;" />
        <div class="mt-1">{{ selectedFile ? selectedFile.name : '' }}</div>
      </div>
    </div>

    <v-alert
      v-if="error"
      type="error"
      class="mb-4"
      variant="tonal"
    >
      {{ error }}
    </v-alert>

    <v-btn
      block
      color="primary"
      type="submit"
      :loading="loading"
      :disabled="!isFormValid"
    >
      S'inscrire
    </v-btn>
  </v-form>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const emit = defineEmits(['submit'])
const authStore = useAuthStore()

// État du formulaire
const form = ref(null)
const loading = ref(false)
const error = ref(null)
const showPassword = ref(false)
const profileImageInput = ref(null)
const selectedFile = ref(null)
const imagePreview = ref(null)

// État des ligues
const availableLeagues = ref([])
const loadingLeagues = ref(false)
const selectedLeagueId = ref(null)

const optionalFormData = ref({
  address: ''
})

const requiredFormData = ref({
  email: '',
  username: '',
  first_name: '',
  last_name: '',
  password: ''
})

// Chargement des ligues
const fetchLeagues = async () => {
  loadingLeagues.value = true
  try {
    const response = await api.get('/leagues/')
    availableLeagues.value = response.data
  } catch (error) {
    console.error('Erreur lors du chargement des ligues:', error)
  } finally {
    loadingLeagues.value = false
  }
}

// Gestionnaire pour le changement de fichier
const onFileChange = (event) => {
  const file = event.target.files[0]
  
  if (file) {
    console.log('File selected:', file.name, file.type, file.size)
    selectedFile.value = file
    
    // Prévisualisation
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  } else {
    selectedFile.value = null
    imagePreview.value = null
  }
}

// Règles de validation
const emailRules = [
  v => !!v || 'L\'email est requis',
  v => /.+@.+\..+/.test(v) || 'L\'email doit être valide'
]

const usernameRules = [
  v => !!v || 'Le nom d\'utilisateur est requis',
  v => v.length >= 3 || 'Le nom d\'utilisateur doit contenir au moins 3 caractères'
]

const nameRules = [
  v => !!v || 'Ce champ est requis',
  v => v.length >= 2 || 'Minimum 2 caractères'
]

const passwordRules = [
  v => !!v || 'Le mot de passe est requis',
  v => v.length >= 8 || 'Le mot de passe doit contenir au moins 8 caractères',
  v => /[A-Z]/.test(v) || 'Le mot de passe doit contenir au moins une majuscule',
  v => /[0-9]/.test(v) || 'Le mot de passe doit contenir au moins un chiffre',
  v => /[!@#$%^&*]/.test(v) || 'Le mot de passe doit contenir au moins un caractère spécial'
]

// Validation du formulaire
const isFormValid = computed(() => {
  const allFieldsFilled = Object.values(requiredFormData.value).every(value => !!value)
  if (!allFieldsFilled) return false

  // Vérifier que toutes les règles sont respectées
  return emailRules.every(rule => rule(requiredFormData.value.email) === true) &&
    usernameRules.every(rule => rule(requiredFormData.value.username) === true) &&
    nameRules.every(rule => rule(requiredFormData.value.first_name) === true) &&
    nameRules.every(rule => rule(requiredFormData.value.last_name) === true) &&
    passwordRules.every(rule => rule(requiredFormData.value.password) === true)
})

const handleSubmit = async () => {
  if (!form.value.validate()) return

  // Validation de l'image si elle existe
  if (selectedFile.value) {
    if (selectedFile.value.size > 2000000) {
      error.value = 'L\'image doit faire moins de 2MB'
      return
    }
    if (!selectedFile.value.type.startsWith('image/')) {
      error.value = 'Le fichier doit être une image'
      return
    }
  }

  loading.value = true
  error.value = null

  try {
    // Préparer les données de la ligue si sélectionnée
    let leagueData = null
    if (selectedLeagueId.value) {
      leagueData = { id: selectedLeagueId.value }
    }

    const registerData = {
      ...requiredFormData.value,
      ...optionalFormData.value,
      profile_image: selectedFile.value,
      league: leagueData
    }
    
    console.log('Sending registration data:', registerData);
    if (selectedFile.value) {
      console.log('With file:', selectedFile.value.name, selectedFile.value.size, selectedFile.value.type);
    }
    
    await authStore.register(registerData)
    emit('submit')
  } catch (err) {
    console.error('Registration error:', err)
    error.value = err.response?.data?.detail || 'Erreur lors de l\'inscription'
  } finally {
    loading.value = false
  }
}

// Chargement des ligues au montage du composant
onMounted(() => {
  fetchLeagues()
})
</script>

<style scoped>
.custom-file-input {
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 4px;
  padding: 16px;
}
</style>