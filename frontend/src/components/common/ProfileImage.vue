<!-- src/components/common/ProfileImage.vue -->
<template>
    <div 
      class="avatar-container"
      :style="{ 
        width: `${size}px`, 
        height: `${size}px` 
      }"
    >
      <img 
        v-if="imageUrl"
        :src="imageUrl" 
        :alt="alt"
        class="avatar-image"
        @error="handleImageError"
      />
      <div v-else class="avatar-placeholder">
        <v-icon :size="size * 0.75">mdi-account</v-icon>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, watch } from 'vue'
  
  const props = defineProps({
    path: {
      type: String,
      default: null
    },
    size: {
      type: Number,
      default: 48
    },
    alt: {
      type: String,
      default: 'Avatar'
    }
  })
  
  const imageUrl = ref(null)
  
  watch(() => props.path, (newPath) => {
    if (!newPath) {
      imageUrl.value = null
      return
    }
  
    // Si c'est une URL blob, l'utiliser directement sans timestamp
    if (newPath.startsWith('blob:')) {
        imageUrl.value = newPath
        return
    }
    
        // Si le chemin commence par http, ajouter le timestamp
    if (newPath.startsWith('http')) {
        imageUrl.value = `${newPath}?t=${Date.now()}`
        return
    }

    // Pour les chemins relatifs, préfixer avec l'URL de l'API et ajouter le timestamp
    imageUrl.value = `${import.meta.env.VITE_API_URL}/${newPath}?t=${Date.now()}`
    }, { immediate: true })
  
  const handleImageError = () => {
    imageUrl.value = null
  }
  </script>
  
  <style scoped>
  .avatar-container {
    position: relative;
    border-radius: 50%;
    overflow: hidden;
    background-color: rgb(var(--v-theme-surface-variant));
  }
  
  .avatar-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .avatar-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: rgba(var(--v-theme-on-surface), 0.6);
  }
  </style>