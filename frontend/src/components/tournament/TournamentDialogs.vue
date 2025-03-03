<!-- src/components/tournament/TournamentDialogs.vue -->
<template>
  <div>
    <!-- Dialog de Rebuy -->
    <v-dialog v-model="showRebuy" max-width="500px">
      <v-card>
        <v-card-title>Rebuy pour {{ selectedPlayer?.username }}</v-card-title>
        <v-card-text>
          <v-form ref="rebuyForm" v-model="rebuyValid">
            <v-row>
              <v-col cols="12">
                <div class="text-subtitle-1 mb-2">Informations actuelles :</div>
                <div class="pl-4 mb-4">
                  <div>Rebuys précédents : {{ selectedPlayer?.num_rebuys || 0 }}</div>
                  <div>Total investi : {{ selectedPlayer?.total_buyin || 0 }}€</div>
                </div>
                
                <v-text-field
                  v-model.number="rebuyAmount"
                  label="Montant du rebuy"
                  type="number"
                  suffix="€"
                  :rules="[
                    v => !!v || 'Le montant est requis',
                    v => v > 0 || 'Le montant doit être positif'
                  ]"
                  required
                ></v-text-field>
  
                <v-text-field
                  v-model.number="chipAmount"
                  label="Jetons reçus"
                  type="number"
                  :rules="[
                    v => !!v || 'Le montant de jetons est requis',
                    v => v > 0 || 'Le montant doit être positif'
                  ]"
                  required
                ></v-text-field>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey-lighten-1"
            variant="text"
            @click="showRebuy = false"
          >
            Annuler
          </v-btn>
          <v-btn
            color="primary"
            :disabled="!rebuyValid"
            @click="confirmRebuy"
          >
            Confirmer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  
    <!-- Dialog d'Élimination -->
    <v-dialog v-model="showElimination" max-width="500px">
      <v-card>
        <v-card-title>Élimination de {{ selectedPlayer?.username }}</v-card-title>
        <v-card-text>
          <v-form ref="eliminationForm" v-model="eliminationValid">
            <v-row>
              <v-col cols="12">
                <div class="text-subtitle-1 mb-2">Position finale</div>
                <v-text-field
                  v-model.number="finalPosition"
                  label="Position"
                  type="number"
                  :rules="[
                    v => !!v || 'La position est requise',
                    v => v > 0 || 'La position doit être positive',
                    v => v <= totalPlayers || `La position ne peut pas dépasser ${totalPlayers}`
                  ]"
                  required
                ></v-text-field>
  
                <div class="text-subtitle-1 mb-2">Gains</div>
                <v-text-field
                  v-model.number="prizeAmount"
                  label="Montant"
                  type="number"
                  suffix="€"
                  :rules="[
                    v => v >= 0 || 'Le montant ne peut pas être négatif'
                  ]"
                ></v-text-field>
  
                <!-- Si c'est un tournoi JAPT -->
                <template v-if="isJAPTTournament">
                  <v-checkbox
                    v-model="hadClayToken"
                    label="Possédait le Jeton d'Argile"
                  ></v-checkbox>
  
                  <v-text-field
                    v-if="hadClayToken"
                    v-model="bountyHunter"
                    label="Chasseur de prime"
                    readonly
                  ></v-text-field>
                </template>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey-lighten-1"
            variant="text"
            @click="showElimination = false"
          >
            Annuler
          </v-btn>
          <v-btn
            color="primary"
            :disabled="!eliminationValid"
            @click="confirmElimination"
          >
            Confirmer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  
    <!-- Dialog de Rééquilibrage des Tables -->
    <v-dialog v-model="showRebalance" max-width="500px">
      <v-card>
        <v-card-title>Rééquilibrage des tables</v-card-title>
        <v-card-text>
          <div class="text-body-1 mb-4">
            Voulez-vous rééquilibrer les tables maintenant ?
          </div>
          <div class="text-caption">
            Cette action va redistribuer les joueurs équitablement entre les tables restantes.
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey-lighten-1"
            variant="text"
            @click="showRebalance = false"
          >
            Annuler
          </v-btn>
          <v-btn
            color="primary"
            @click="confirmRebalance"
          >
            Confirmer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>
  
<script setup>
import { ref, computed } from 'vue'
import { useTournamentStore } from '@/stores/tournament'
  
const props = defineProps({
  totalPlayers: {
    type: Number,
    default: 0
  },
  isJAPTTournament: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits([
  'rebuyConfirmed',
  'eliminationConfirmed',
  'tableRebalanceConfirmed'
]);

const tournamentStore = useTournamentStore()
  
// État des dialogues
const showRebuy = ref(false)
const showElimination = ref(false)
const showRebalance = ref(false)
  
// État des formulaires
const rebuyForm = ref(null)
const eliminationForm = ref(null)
const rebuyValid = ref(false)
const eliminationValid = ref(false)
  
// Données des formulaires
const selectedPlayer = ref(null)
const rebuyAmount = ref(null)
const chipAmount = ref(null)
const finalPosition = ref(null)
const prizeAmount = ref(0)
const hadClayToken = ref(false)
const bountyHunter = ref('')
  
// Méthodes pour ouvrir les dialogues
const showRebuyDialog = (player) => {
  selectedPlayer.value = player
  rebuyAmount.value = tournamentStore.currentTournament?.buy_in || 0
  chipAmount.value = tournamentStore.currentTournament?.configuration?.starting_chips || 0
  showRebuy.value = true
}
  
const showEliminationDialog = (player) => {
  selectedPlayer.value = player
  finalPosition.value = tournamentStore.getNextEliminationPosition
  prizeAmount.value = 0
  hadClayToken.value = false
  bountyHunter.value = ''
  showElimination.value = true
}
  
const showRebalanceDialog = () => {
  showRebalance.value = true
}
  
// Méthodes de confirmation
const confirmRebuy = () => {
  if (!rebuyForm.value?.validate()) return
  
  emit('rebuyConfirmed', {
    playerId: selectedPlayer.value.id,
    playerName: selectedPlayer.value.username,
    amount: rebuyAmount.value,
    chips: chipAmount.value
  });
  
  showRebuy.value = false;
}
  
const confirmElimination = () => {
  if (!eliminationForm.value?.validate()) return
  
  emit('eliminationConfirmed', {
    playerId: selectedPlayer.value.id,
    playerName: selectedPlayer.value.username,
    position: finalPosition.value,
    prize: prizeAmount.value,
    hadClayToken: hadClayToken.value,
    bountyHunterId: bountyHunter.value ? parseInt(bountyHunter.value) : null
  });
  
  showElimination.value = false;
}
  
const confirmRebalance = () => {
  emit('tableRebalanceConfirmed');
  showRebalance.value = false;
}
  
// Expose les méthodes pour le composant parent
defineExpose({
  showRebuyDialog,
  showEliminationDialog,
  showRebalanceDialog
});
</script>