<!-- src/components/layout/NavigationDrawer.vue -->
<template>
    <v-navigation-drawer v-model="drawer" temporary>
      <v-list>
        <v-list-item
          prepend-icon="mdi-home"
          title="Accueil"
          to="/"
        ></v-list-item>

        <v-list-item
          prepend-icon="mdi-poker-chip"
          title="Tournois"
          @click="handleNavigation('/tournaments')"
          :disabled="!isAuthenticated"
        >
          <template v-slot:append>
            <v-icon v-if="!isAuthenticated" color="grey" size="small">
              mdi-lock
            </v-icon>
          </template>
        </v-list-item>

        <v-list-item
          prepend-icon="mdi-chart-box"
          title="Statistiques"
          @click="handleNavigation('/stats')"
          :disabled="!isAuthenticated"
        >
          <template v-slot:append>
            <v-icon v-if="!isAuthenticated" color="grey" size="small">
              mdi-lock
            </v-icon>
          </template>
        </v-list-item>

        <v-list-item
          prepend-icon="mdi-post"
          title="Blog"
          @click="handleNavigation('/blog')"
          :disabled="!isAuthenticated"
        >
          <template v-slot:append>
            <v-icon v-if="!isAuthenticated" color="grey" size="small">
              mdi-lock
            </v-icon>
          </template>
        </v-list-item>

        <v-list-item
          prepend-icon="mdi-cog"
          title="Configuration"
          @click="handleNavigation('/config')"
          :disabled="!isAuthenticated"
        >
          <template v-slot:append>
            <v-icon v-if="!isAuthenticated" color="grey" size="small">
              mdi-lock
            </v-icon>
          </template>
        </v-list-item>

        <v-list-item
          prepend-icon="mdi-cards-playing"
          title="Ligues"
          @click="handleNavigation('/leagues')"
          :disabled="!isAuthenticated"
        >
          <template v-slot:append>
            <v-icon v-if="!isAuthenticated" color="grey" size="small">
              mdi-lock
            </v-icon>
          </template>
        </v-list-item>

        <!-- Option de connexion/déconnexion -->
        <v-divider class="my-2"></v-divider>
        <v-list-item
          v-if="!isAuthenticated"
          prepend-icon="mdi-login"
          title="Se connecter"
          to="/login"
        ></v-list-item>
        <v-list-item
          v-else
          prepend-icon="mdi-logout"
          title="Se déconnecter"
          @click="handleLogout"
        ></v-list-item>
      </v-list>
    </v-navigation-drawer>
  </template>
  
  <script setup>
  import { computed } from 'vue'
  import { useAuthStore } from '@/stores/auth'
  import { useRouter } from 'vue-router'
  
  const props = defineProps({
    modelValue: {
      type: Boolean,
      required: true
    }
  })
  
  // Emit pour le v-model et logout
  const emit = defineEmits(['update:modelValue', 'logout'])
  
  const authStore = useAuthStore()
  const router = useRouter()
  
  // v-model binding
  const drawer = computed({
    get: () => props.modelValue,
    set: (value) => emit('update:modelValue', value)
  })

  // Redirection si l'utilisateur n'est pas loggé
  const handleNavigation = (route) => {
    if (!isAuthenticated.value) {
      drawer.value = false
      router.push({
        path: '/login',
        query: { redirect: route }
      })
    } else {
      router.push(route)
    }
  }
  
  const isAuthenticated = computed(() => authStore.isAuthenticated)
  const isAdmin = computed(() => authStore.isAdmin)
  
  const handleLogout = async () => {
    drawer.value = false
    await authStore.logout()
    router.push('/login')
  }
  </script>