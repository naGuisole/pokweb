// src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

import { useAuthStore } from './stores/auth'
import './assets/styles/main.scss'

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'

// Importation des traductions françaises complètes pour Vuetify
import { fr } from 'vuetify/locale'

// Configuration de date-fns pour le format français
import { fr as dateFnsFr } from 'date-fns/locale'
import DateFnsAdapter from '@date-io/date-fns'

const vuetify = createVuetify({
  components,
  directives,
  locale: {
    locale: 'fr',
    fallback: 'en',
    messages: { fr }
  },
  date: {
    adapter: DateFnsAdapter,
  },
  theme: {
    defaultTheme: 'light'
  }
})

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(vuetify)

// Initialisation du store d'authentification
const authStore = useAuthStore()
authStore.init()

app.mount('#app')

console.log("Application initialisée")
