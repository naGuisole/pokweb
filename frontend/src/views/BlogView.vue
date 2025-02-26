<!-- src/views/BlogView.vue -->
<template>
    <v-container>
      <!-- En-tête avec bouton de création -->
      <v-row>
        <v-col cols="12" class="d-flex align-center">
          <h1 class="text-h4">Les Aventures du Jeton d'Argile</h1>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            prepend-icon="mdi-plus"
            @click="showCreatePost = true"
          >
            Nouveau post
          </v-btn>
        </v-col>
      </v-row>
  
      <!-- Grille des posts -->
      <v-row>
        <v-col 
          v-for="post in posts" 
          :key="post.id" 
          cols="12" 
          md="6"
        >
          <v-card class="blog-card">
            <!-- Carousel des images -->
            <v-carousel
              v-if="post.images && post.images.length > 0"
              hide-delimiter-background
              show-arrows="hover"
              height="300"
            >
              <v-carousel-item
                v-for="(image, index) in post.images"
                :key="index"
                :src="image"
                cover
              >
                <template v-slot:placeholder>
                  <v-row
                    class="fill-height ma-0"
                    align="center"
                    justify="center"
                  >
                    <v-progress-circular
                      indeterminate
                      color="primary"
                    ></v-progress-circular>
                  </v-row>
                </template>
              </v-carousel-item>
            </v-carousel>
  
            <v-card-title>{{ post.title }}</v-card-title>
  
            <v-card-subtitle class="d-flex align-center">
              <v-avatar size="32" class="mr-2">
                <v-img
                  v-if="post.author.profile_image_path"
                  :src="post.author.profile_image_path"
                  alt="avatar"
                ></v-img>
                <v-icon v-else>mdi-account</v-icon>
              </v-avatar>
              <span>{{ post.author.username }}</span>
              <v-spacer></v-spacer>
              <span class="text-caption">
                {{ formatDate(post.created_at) }}
              </span>
            </v-card-subtitle>
  
            <v-card-text>
              <div class="blog-content" v-html="formatContent(post.content)"></div>
            </v-card-text>
  
            <v-divider></v-divider>
  
            <v-card-actions>
              <v-btn
                variant="text"
                @click="expandPost(post.id)"
              >
                Lire plus
              </v-btn>
              <v-spacer></v-spacer>
              <v-btn
                v-if="canEditPost(post)"
                icon
                variant="text"
                @click="editPost(post)"
              >
                <v-icon>mdi-pencil</v-icon>
              </v-btn>
              <v-btn
                v-if="canEditPost(post)"
                icon
                variant="text"
                color="error"
                @click="confirmDelete(post)"
              >
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
  
      <!-- Dialogue de création/édition de post -->
      <v-dialog
        v-model="showCreatePost"
        max-width="800px"
        persistent
      >
        <v-card>
          <v-card-title>
            {{ editingPost ? 'Modifier le post' : 'Nouveau post' }}
          </v-card-title>
          <v-card-text>
            <v-form ref="postForm" v-model="formValid">
              <v-text-field
                v-model="postData.title"
                label="Titre"
                :rules="titleRules"
                required
              ></v-text-field>
  
              <v-textarea
                v-model="postData.content"
                label="Contenu"
                :rules="contentRules"
                required
                rows="6"
              ></v-textarea>
  
              <v-file-input
                v-model="postImages"
                label="Images"
                multiple
                accept="image/*"
                :rules="imageRules"
                prepend-icon="mdi-camera"
                show-size
                counter
              >
                <template v-slot:selection="{ fileNames }">
                  <template v-for="(fileName, index) in fileNames" :key="fileName">
                    <v-chip
                      v-if="index < 2"
                      size="small"
                      label
                      color="primary"
                      class="mr-2"
                    >
                      {{ fileName }}
                    </v-chip>
                    <span
                      v-else-if="index === 2"
                      class="text-caption text-grey-darken-1"
                    >
                      +{{ fileNames.length - 2 }} autres fichiers
                    </span>
                  </template>
                </template>
              </v-file-input>
  
              <!-- Prévisualisation des images existantes en édition -->
              <v-row v-if="editingPost && postData.images?.length > 0" class="mt-4">
                <v-col 
                  v-for="(image, index) in postData.images" 
                  :key="index"
                  cols="4"
                  class="d-flex align-center"
                >
                  <v-img
                    :src="image"
                    aspect-ratio="16/9"
                    cover
                    class="rounded"
                  >
                    <template v-slot:placeholder>
                      <v-row
                        class="fill-height ma-0"
                        align="center"
                        justify="center"
                      >
                        <v-progress-circular
                          indeterminate
                          color="primary"
                        ></v-progress-circular>
                      </v-row>
                    </template>
                  </v-img>
                  <v-btn
                    icon="mdi-close"
                    size="small"
                    color="error"
                    variant="text"
                    class="remove-image-btn"
                    @click="removeImage(index)"
                  ></v-btn>
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
  
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="grey-lighten-1"
              variant="text"
              @click="closeDialog"
            >
              Annuler
            </v-btn>
            <v-btn
              color="primary"
              :disabled="!formValid"
              :loading="saving"
              @click="savePost"
            >
              {{ editingPost ? 'Modifier' : 'Publier' }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
  
      <!-- Dialogue de confirmation de suppression -->
      <v-dialog
        v-model="showDeleteDialog"
        max-width="400px"
      >
        <v-card>
          <v-card-title>Confirmer la suppression</v-card-title>
          <v-card-text>
            Êtes-vous sûr de vouloir supprimer ce post ?
            Cette action est irréversible.
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="grey-lighten-1"
              variant="text"
              @click="showDeleteDialog = false"
            >
              Annuler
            </v-btn>
            <v-btn
              color="error"
              @click="deletePost"
            >
              Supprimer
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
  
      <!-- Snackbar pour les notifications -->
      <v-snackbar
        v-model="snackbar.show"
        :color="snackbar.color"
        :timeout="3000"
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
  import { ref, computed, onMounted } from 'vue'
  import { useAuthStore } from '@/stores/auth'
  import { useBlogStore } from '@/stores/blog'
  import { format, formatDistance } from 'date-fns'
  import { fr } from 'date-fns/locale'
  import DOMPurify from 'dompurify'
  import { marked } from 'marked'
  
  const authStore = useAuthStore()
  const blogStore = useBlogStore()
  
  // État du composant
  const posts = ref([])
  const showCreatePost = ref(false)
  const showDeleteDialog = ref(false)
  const formValid = ref(false)
  const saving = ref(false)
  const postForm = ref(null)
  const editingPost = ref(null)
  const postToDelete = ref(null)
  const postImages = ref([])
  
  // Données du formulaire
  const postData = ref({
    title: '',
    content: '',
    images: []
  })
  
  // Règles de validation
  const titleRules = [
    v => !!v || 'Le titre est requis',
    v => v.length >= 3 || 'Le titre doit contenir au moins 3 caractères'
  ]
  
  const contentRules = [
    v => !!v || 'Le contenu est requis',
    v => v.length >= 10 || 'Le contenu doit contenir au moins 10 caractères'
  ]
  
  const imageRules = [
    files => !files || !files.length || files.length <= 10 || 'Maximum 10 images',
    files => {
      if (!files) return true
      return !Array.from(files).some(file => file.size > 5000000) || 'Les images doivent faire moins de 5MB'
    }
  ]
  
  // Notifications
  const snackbar = ref({
    show: false,
    text: '',
    color: 'success'
  })
  
  // Computed properties
  const currentUser = computed(() => authStore.user)
  
  // Méthodes utilitaires
  const formatDate = (date) => {
    const postDate = new Date(date)
    const now = new Date()
    
    return formatDistance(postDate, now, {
      addSuffix: true,
      locale: fr
    })
  }
  
  const formatContent = (content) => {
    // Conversion Markdown en HTML et nettoyage
    const html = marked(content)
    return DOMPurify.sanitize(html)
  }
  
  const canEditPost = (post) => {
    return currentUser.value && (
      post.author_id === currentUser.value.id || 
      currentUser.value.is_admin
    )
  }
  
  // Actions
  const loadPosts = async () => {
    try {
      const loadedPosts = await blogStore.fetchPosts()
      posts.value = loadedPosts
    } catch (error) {
      showError('Erreur lors du chargement des posts')
    }
  }
  
  const expandPost = (postId) => {
    // TODO: Implémenter la vue détaillée d'un post
  }
  
  const editPost = (post) => {
    editingPost.value = post
    postData.value = {
      title: post.title,
      content: post.content,
      images: [...post.images]
    }
    showCreatePost.value = true
  }
  
  const removeImage = (index) => {
    if (editingPost.value) {
      postData.value.images.splice(index, 1)
    }
  }
  
  const savePost = async () => {
    if (!postForm.value.validate()) return
  
    saving.value = true
    try {
      const formData = new FormData()
      formData.append('title', postData.value.title)
      formData.append('content', postData.value.content)
  
      // Ajout des nouvelles images
      if (postImages.value) {
        Array.from(postImages.value).forEach(file => {
          formData.append('images', file)
        })
      }
  
      // Ajout des images existantes en mode édition
      if (editingPost.value) {
        postData.value.images.forEach(image => {
          formData.append('existing_images', image)
        })
      }
  
      if (editingPost.value) {
        await blogStore.updatePost(editingPost.value.id, formData)
        showSuccess('Post modifié avec succès')
      } else {
        await blogStore.createPost(formData)
        showSuccess('Post créé avec succès')
      }
  
      closeDialog()
      loadPosts()
    } catch (error) {
      showError('Erreur lors de l\'enregistrement du post')
    } finally {
      saving.value = false
    }
  }
  
  const confirmDelete = (post) => {
    postToDelete.value = post
    showDeleteDialog.value = true
  }
  
  const deletePost = async () => {
    if (!postToDelete.value) return
  
    try {
      await blogStore.deletePost(postToDelete.value.id)
      showSuccess('Post supprimé avec succès')
      showDeleteDialog.value = false
      loadPosts()
    } catch (error) {
      showError('Erreur lors de la suppression du post')
    }
  }
  
  const closeDialog = () => {
    showCreatePost.value = false
    editingPost.value = null
    postData.value = {
      title: '',
      content: '',
      images: []
    }
    postImages.value = []
  }
  
  // Notifications
  const showSuccess = (text) => {
    snackbar.value = {
      show: true,
      text,
      color: 'success'
    }
  }
  
  const showError = (text) => {
    snackbar.value = {
      show: true,
      text,
      color: 'error'
    }
  }
  
  // Cycle de vie
  onMounted(() => {
    loadPosts()
  })
  </script>
  
  <style scoped>
  .blog-card {
    transition: transform 0.2s;
  }
  
  .blog-card:hover {
    transform: translateY(-2px);
  }
  
  .blog-content {
    max-height: 150px;
    overflow: hidden;
    position: relative;
  }
  
  .blog-content::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 50px;
    background: linear-gradient(transparent, var(--v-theme-surface));
  }
  
  .remove-image-btn {
    position: absolute;
    top: 8px;
    right: 8px;
    background: rgba(0, 0, 0, 0.6);
  }
  
  :deep(.v-carousel .v-carousel__controls) {
    background: linear-gradient(transparent, rgba(0, 0, 0, 0.5));
  }
  </style>