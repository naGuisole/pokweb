<!-- src/components/tournament/TournamentCard.vue -->
<template>
    <v-card :class="cardClasses">
      <v-card-title class="d-flex justify-space-between">
        {{ tournament.name }}
        <v-chip
          :color="getStatusColor"
          size="small"
        >
          {{ getStatusLabel }}
        </v-chip>
      </v-card-title>
  
      <v-card-text>
        <v-row>
          <v-col cols="6">
            <div class="text-caption">Date</div>
            <div class="text-body-2">{{ formattedDate }}</div>
          </v-col>
          <v-col cols="6">
            <div class="text-caption">Type</div>
            <div class="text-body-2">{{ tournament.tournament_type }}</div>
          </v-col>
        </v-row>
  
        <v-row class="mt-2">
          <v-col cols="6">
            <div class="text-caption">Participants</div>
            <div class="text-body-2">
              {{ tournament.registered_players?.length || 0 }} / {{ tournament.max_players }}
            </div>
          </v-col>
          <v-col cols="6">
            <div class="text-caption">Buy-in</div>
            <div class="text-body-2">{{ tournament.buy_in }}€</div>
          </v-col>
        </v-row>
  
        <template v-if="tournament.tournament_type === 'JAPT'">
          <v-row class="mt-2">
            <v-col cols="12">
              <div class="text-caption">Détenteur du Jeton</div>
              <div class="text-body-2 d-flex align-center">
                <v-avatar size="24" class="mr-2">
                  <v-img
                    v-if="tournament.clay_token_holder?.profile_image_path"
                    :src="tournament.clay_token_holder.profile_image_path"
                    alt="Profile"
                  ></v-img>
                  <v-icon v-else>mdi-account</v-icon>
                </v-avatar>
                {{ tournament.clay_token_holder?.username || 'Non attribué' }}
              </div>
            </v-col>
          </v-row>
        </template>
      </v-card-text>
  
      <v-divider></v-divider>
  
      <v-card-actions>
        <v-btn
          variant="text"
          color="primary"
          :to="`/tournaments/${tournament.id}`"
        >
          Détails
        </v-btn>
  
        <v-spacer></v-spacer>
  
        <!-- Actions selon le statut -->
        <template v-if="tournament.status === 'PLANNED'">
          <v-btn
            v-if="!isRegistered"
            variant="text"
            color="success"
            :loading="registering"
            @click="register"
          >
            S'inscrire
          </v-btn>
          <v-btn
            v-else
            variant="text"
            color="error"
            :loading="registering"
            @click="unregister"
          >
            Se désinscrire
          </v-btn>
        </template>
  
        <!-- Menu des actions admin -->
        <!-- Menu des actions admin -->
        <v-menu
          v-if="isAdmin"
          location="bottom end"
        >
          <template v-slot:activator="{ props }">
            <v-btn
              icon
              v-bind="props"
            >
              <v-icon>mdi-dots-vertical</v-icon>
            </v-btn>
          </template>

          <v-list>
            <template v-if="tournament.status === 'PLANNED'">
              <v-list-item
                @click="$emit('start', tournament.id)"
              >
                <template v-slot:prepend>
                  <v-icon>mdi-play</v-icon>
                </template>
                <v-list-item-title>Démarrer</v-list-item-title>
              </v-list-item>

              <v-list-item
                @click="$emit('edit', tournament)"
              >
                <template v-slot:prepend>
                  <v-icon>mdi-pencil</v-icon>
                </template>
                <v-list-item-title>Modifier</v-list-item-title>
              </v-list-item>

              <v-list-item
                @click="$emit('delete', tournament)"
              >
                <template v-slot:prepend>
                  <v-icon>mdi-delete</v-icon>
                </template>
                <v-list-item-title>Supprimer</v-list-item-title>
              </v-list-item>
            </template>

            <template v-if="tournament.status === 'IN_PROGRESS'">
              <v-list-item
                @click="$emit('pause', tournament.id)"
              >
                <template v-slot:prepend>
                  <v-icon>{{ tournament.paused ? 'mdi-play' : 'mdi-pause' }}</v-icon>
                </template>
                <v-list-item-title>{{ tournament.paused ? 'Reprendre' : 'Pause' }}</v-list-item-title>
              </v-list-item>
            </template>
          </v-list>
        </v-menu>
      </v-card-actions>
    </v-card>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue'
  import { useAuthStore } from '@/stores/auth'
  import { format } from 'date-fns'
  import { fr } from 'date-fns/locale'
  
  const props = defineProps({
    tournament: {
      type: Object,
      required: true
    }
  })
  
  const emit = defineEmits(['register', 'unregister', 'start', 'edit', 'delete', 'pause'])
  
  const authStore = useAuthStore()
  const registering = ref(false)
  
  // Computed
  const isAdmin = computed(() => {
    console.log("User ID:", authStore.user?.id);
    console.log("Tournament admin ID:", props.tournament.admin_id);
    return authStore.user?.id === props.tournament.admin_id;
  })
  
  const isRegistered = computed(() => {
    return props.tournament.registered_players?.some(
      player => player.id === authStore.user?.id
    )
  })
  
  const formattedDate = computed(() => {
    return format(new Date(props.tournament.date), 'PPP à HH:mm', { locale: fr })
  })
  
  const getStatusColor = computed(() => {
    const colors = {
      PLANNED: 'success',
      IN_PROGRESS: 'primary',
      COMPLETED: 'grey'
    }
    return colors[props.tournament.status] || 'grey'
  })
  
  const getStatusLabel = computed(() => {
    const labels = {
      PLANNED: 'Planifié',
      IN_PROGRESS: 'En cours',
      COMPLETED: 'Terminé'
    }
    return labels[props.tournament.status] || props.tournament.status
  })
  
  const cardClasses = computed(() => ({
    'elevation-2': true,
    'tournament-card': true,
    'border-primary': props.tournament.status === 'IN_PROGRESS',
    'border-success': props.tournament.status === 'PLANNED',
    'border-grey': props.tournament.status === 'COMPLETED'
  }))
  
  // Actions
  const register = async () => {
    if (registering.value) return
    registering.value = true
    try {
      await emit('register')
    } finally {
      registering.value = false
    }
  }
  
  const unregister = async () => {
    if (registering.value) return
    registering.value = true
    try {
      await emit('unregister')
    } finally {
      registering.value = false
    }
  }
  </script>
  
  <style scoped>
  .tournament-card {
    transition: transform 0.2s;
  }
  
  .tournament-card:hover {
    transform: translateY(-2px);
  }
  
  .border-primary {
    border-left: 4px solid var(--v-primary-base) !important;
  }
  
  .border-success {
    border-left: 4px solid var(--v-success-base) !important;
  }
  
  .border-grey {
    border-left: 4px solid var(--v-grey-base) !important;
  }
  </style>