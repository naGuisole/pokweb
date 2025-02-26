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

    <league-selector
      v-model="leagueData"
      class="mt-4"
    ></league-selector>
    <div class="text-caption text-grey">
      Vous pourrez rejoindre ou créer une ligue plus tard
    </div>

    <v-file-input
      v-model="optionalFormData.profile_image"
      label="Photo de profil"
      prepend-icon="mdi-camera"
      accept="image/*"
      show-size
    ></v-file-input>

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
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import LeagueSelector from '@/components/league/LeagueSelector.vue'

const emit = defineEmits(['submit'])
const authStore = useAuthStore()

// État du formulaire
const form = ref(null)
const loading = ref(false)
const error = ref(null)
const showPassword = ref(false)

const optionalFormData = ref({
  address: '',
  profile_image: null
})

const requiredFormData = ref({
  email: '',
  username: '',
  first_name: '',
  last_name: '',
  password: ''
})

const leagueData = ref({})

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
  if (optionalFormData.value.profile_image?.[0]) {
    const file = optionalFormData.value.profile_image[0]
    if (file.size > 2000000) {
      error.value = 'L\'image doit faire moins de 2MB'
      return
    }
    if (!file.type.startsWith('image/')) {
      error.value = 'Le fichier doit être une image'
      return
    }
  }

  loading.value = true
  error.value = null

  try {
    const registerData = {
      ...requiredFormData.value,
      ...optionalFormData.value,
      league: leagueData.value?.id ? leagueData.value : null
    }
    await authStore.register(registerData)
    emit('submit')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Erreur lors de l\'inscription'
  } finally {
    loading.value = false
  }
}
</script>