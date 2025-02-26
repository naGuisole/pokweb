<template>
  <v-app>
    <app-bar v-model="drawer" />
    
    <navigation-drawer 
      v-model="drawer"
      @logout="handleLogout"
    />

    <v-main>
      <v-container fluid>
        <router-view></router-view>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import NavigationDrawer from '@/components/layout/NavigationDrawer.vue'
import AppBar from '@/components/layout/AppBar.vue'

const router = useRouter()
const authStore = useAuthStore()
const drawer = ref(false)

const handleLogout = async () => {
  drawer.value = false
  await authStore.logout()
  router.push('/login')
}
</script>