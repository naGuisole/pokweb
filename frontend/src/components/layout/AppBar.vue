<template>
  <v-app-bar elevation="4" :elevation="2">
    <template v-slot:prepend>
      <v-app-bar-nav-icon @click="toggleDrawer"></v-app-bar-nav-icon>
    </template>

    <v-app-bar-title>
      Pokweb
      <template v-if="isAuthenticated">
        <span v-if="user?.league" class="text-subtitle-0">
          - {{ user.league.name }}
        </span>
        <span v-else class="text-subtitle-0 text-grey">
          - Aucune ligue
        </span>
      </template>
    </v-app-bar-title>

    <template v-slot:append>
    <v-btn icon @click="showProfile">
      <profile-image 
        :path="user?.profile_image_path"
        :size="32"
        :alt="user?.username"
      />
    </v-btn>
  </template>
  </v-app-bar>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import ProfileImage from '@/components/common/ProfileImage.vue';

const props = defineProps({
  modelValue: Boolean  // Pour le drawer
})

const emit = defineEmits(['update:modelValue'])

const router = useRouter()
const authStore = useAuthStore()

const user = computed(() => authStore.user)
const isAuthenticated = computed(() => authStore.isAuthenticated)


const toggleDrawer = () => {
  emit('update:modelValue', !props.modelValue)
}

const showProfile = () => {
  if (!isAuthenticated.value) {
    router.push('/login')
  } else {
    router.push('/profile')
  }
}
</script>