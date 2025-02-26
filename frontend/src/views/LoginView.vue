<!-- src/views/LoginView.vue -->
<template>
  <v-container class="fill-height">
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark>
            <v-toolbar-title>Pokweb</v-toolbar-title>
          </v-toolbar>

          <v-tabs v-model="tab" color="primary">
            <v-tab value="login">Connexion</v-tab>
            <v-tab value="register">Inscription</v-tab>
          </v-tabs>

          <v-card-text>
            <v-window v-model="tab">
              <v-window-item value="login">
                <login-form @submit="handleLoginSuccess"/>
              </v-window-item>

              <v-window-item value="register">
                <register-form @submit="handleRegisterSuccess"/>
              </v-window-item>
            </v-window>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Snackbar pour les notifications -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import LoginForm from '@/components/auth/LoginForm.vue'
import RegisterForm from '@/components/auth/RegisterForm.vue'

const router = useRouter()
const tab = ref('login')

// Gestion des notifications
const snackbar = ref({
  show: false,
  text: '',
  color: 'success'
})

const handleLoginSuccess = () => {
  router.push('/')
}

const handleRegisterSuccess = () => {
  snackbar.value = {
    show: true,
    text: 'Inscription réussie ! Vous pouvez maintenant vous connecter',
    color: 'success'
  }
  tab.value = 'login'
}
</script>