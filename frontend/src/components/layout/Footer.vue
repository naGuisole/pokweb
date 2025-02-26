<!-- src/components/layout/Footer.vue -->
<template>
    <v-footer app class="d-flex flex-column">
      <div class="d-flex w-100 align-center justify-space-between px-4">
        <span>&copy; {{ currentYear }} pokweb</span>
        <div class="text-center">
          <v-btn
            v-for="link in links"
            :key="link.text"
            variant="text"
            class="mx-2"
            :to="link.to"
          >
            {{ link.text }}
          </v-btn>
        </div>
      </div>
    </v-footer>
  </template>
  
  <script setup>
  import { computed } from 'vue'
  
  const currentYear = computed(() => new Date().getFullYear())
  
  const links = [
    { text: 'Accueil', to: '/' },
    { text: 'À propos', to: '/about' },
    { text: 'Contact', to: '/contact' }
  ]
  </script>