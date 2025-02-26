<!-- src/components/league/LeagueSelector.vue -->
<template>
  <div>
    <v-autocomplete
      v-model="selectedLeague"
      :items="leagues"
      :loading="loading"
      item-title="name"
      item-value="id"
      label="Sélectionner une ligue"
      :rules="[v => !!v || 'Veuillez sélectionner une ligue']"
      :filter="filterLeagues"
      :no-data-text="noDataText"
      required
    >
      <template v-slot:item="{ props, item }">
        <v-list-item v-bind="props">
          <v-list-item-title>{{ item.raw.name }}</v-list-item-title>
          <v-list-item-subtitle>{{ item.raw.description }}</v-list-item-subtitle>
        </v-list-item>
      </template>
    </v-autocomplete>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useLeagueStore } from '@/stores/league'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue'])

const leagueStore = useLeagueStore()
const loading = ref(false)
const selectedLeague = ref(null)

// Liste des ligues disponibles
const leagues = computed(() => leagueStore.getAvailableLeagues)

// Texte affiché quand aucune ligue ne correspond à la recherche
const noDataText = computed(() => {
  if (loading.value) return 'Chargement...'
  return 'Aucune ligue trouvée'
})

// Filtrage des ligues
const filterLeagues = (item, queryText) => {
  if (!queryText) return true
  const searchText = queryText.toLowerCase()
  return (
    item.name.toLowerCase().includes(searchText) ||
    (item.description && item.description.toLowerCase().includes(searchText))
  )
}

// Chargement des ligues
const loadLeagues = async () => {
  loading.value = true
  try {
    await leagueStore.fetchLeagues()
  } catch (error) {
    console.error('Erreur lors du chargement des ligues:', error)
  } finally {
    loading.value = false
  }
}

// Mise à jour de la valeur
const updateValue = () => {
  emit('update:modelValue', {
    id: selectedLeague.value
  })
}

// Watch sur les changements de valeur
watch(selectedLeague, updateValue)

onMounted(() => {
  loadLeagues()
})
</script>