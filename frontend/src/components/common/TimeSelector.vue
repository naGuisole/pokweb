<!-- src/components/common/TimeSelector.vue -->
<template>
    <v-menu
      v-model="showPicker"
      :close-on-content-click="false"
    >
      <template v-slot:activator="{ props }">
        <v-text-field
          :model-value="modelValue"
          :label="label"
          readonly
          v-bind="props"
          prepend-icon="mdi-clock"
          :rules="rules"
        ></v-text-field>
      </template>
  
      <v-card min-width="300px">
        <v-card-title class="text-subtitle-1">Sélectionner l'heure</v-card-title>
        <v-card-text>
          <v-row align="center" no-gutters>
            <v-col>
              <v-select
                v-model="selectedHour"
                :items="hours"
                label="Heure"
                density="compact"
                menu-props="{ maxHeight: 400 }"
              ></v-select>
            </v-col>
            <v-col class="mx-2 text-center">:</v-col>
            <v-col>
              <v-select
                v-model="selectedMinute"
                :items="minutes"
                label="Minutes"
                density="compact"
                menu-props="{ maxHeight: 400 }"
              ></v-select>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            variant="text"
            @click="showPicker = false"
          >
            Annuler
          </v-btn>
          <v-btn
            color="primary"
            @click="confirmTime"
          >
            Confirmer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-menu>
  </template>
  
  <script setup>
  import { ref, watch } from 'vue'
  
  const props = defineProps({
    modelValue: {
      type: String,
      default: '20:00'  // Valeur par défaut 20h
    },
    label: {
      type: String,
      default: 'Heure'
    },
    rules: {
      type: Array,
      default: () => []
    }
  })
  
  const emit = defineEmits(['update:modelValue'])
  
  const showPicker = ref(false)
  const selectedHour = ref('20')
  const selectedMinute = ref('00')
  
  // Heures au format 24h (00-23)
  const hours = Array.from({ length: 24 }, (_, i) => 
    i.toString().padStart(2, '0')
  )
  
  // Minutes (00-59)
  const minutes = Array.from({ length: 60 }, (_, i) => 
    i.toString().padStart(2, '0')
  )
  
  // Initialisation des valeurs
  watch(() => props.modelValue, (newVal) => {
    if (newVal) {
      const [hour, minute] = newVal.split(':')
      selectedHour.value = hour
      selectedMinute.value = minute
    } else {
      // Si pas de valeur, initialiser à 20:00
      selectedHour.value = '20'
      selectedMinute.value = '00'
    }
  }, { immediate: true })
  
  // Confirmation de la sélection
  const confirmTime = () => {
    const formattedTime = `${selectedHour.value}:${selectedMinute.value}`
    emit('update:modelValue', formattedTime)
    showPicker.value = false
  }
  </script>