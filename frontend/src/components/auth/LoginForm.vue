<!-- src/components/auth/LoginForm.vue -->
<template>
  <v-form ref="form" v-model="valid" @submit.prevent="handleSubmit">
    <v-text-field
      v-model="formData.email"
      label="Email"
      type="email"
      prepend-inner-icon="mdi-email"
      :rules="emailRules"
      required
      autocomplete="username"
    ></v-text-field>

    <v-text-field
      v-model="formData.password"
      label="Mot de passe"
      :type="showPassword ? 'text' : 'password'"
      prepend-inner-icon="mdi-lock"
      :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
      @click:append-inner="showPassword = !showPassword"
      :rules="passwordRules"
      required
      autocomplete="current-password"
    ></v-text-field>

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
      :disabled="!valid"
    >
      Se connecter
    </v-btn>
  </v-form>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const emit = defineEmits(['submit'])
const authStore = useAuthStore()

// État du formulaire
const form = ref(null)
const valid = ref(false)
const loading = ref(false)
const error = ref(null)
const showPassword = ref(false)

const formData = ref({
  email: '',
  password: ''
})

// Règles de validation
const emailRules = [
  v => !!v || 'L\'email est requis',
  v => /.+@.+\..+/.test(v) || 'L\'email doit être valide'
]

const passwordRules = [
  v => !!v || 'Le mot de passe est requis'
]

const handleSubmit = async () => {
  if (!valid.value) return

  loading.value = true
  error.value = null

  try {
    await authStore.login(formData.value.email, formData.value.password)
    emit('submit')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Erreur lors de la connexion'
  } finally {
    loading.value = false
  }
}
</script>