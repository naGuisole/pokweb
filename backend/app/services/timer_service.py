# backend/app/services/timer_service.py (version améliorée)
import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models.models import Tournament, TournamentStatus
from ..routes.websockets import notify_timer_tick

logger = logging.getLogger(__name__)


class TournamentTimerService:
    """Service qui gère les timers pour tous les tournois actifs"""

    def __init__(self):
        self.running = False
        self.task = None
        self.update_interval = 1  # Mise à jour chaque seconde

    async def start(self):
        """Démarre le service de timer"""
        if self.running:
            return

        self.running = True
        self.task = asyncio.create_task(self._timer_loop())
        logger.info("Tournament timer service started")

    async def stop(self):
        """Arrête le service de timer"""
        if not self.running:
            return

        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Tournament timer service stopped")

    async def _timer_loop(self):
        """Boucle principale du service de timer"""
        while self.running:
            try:
                # Traiter tous les tournois actifs
                await self._process_active_tournaments()

                # Envoyer des mises à jour périodiques (moins fréquentes)
                if int(datetime.utcnow().timestamp()) % 5 == 0:  # Toutes les 5 secondes
                    await self._send_timer_updates()

            except Exception as e:
                logger.error(f"Error in timer service: {e}")

            # Attendre avant la prochaine itération
            await asyncio.sleep(self.update_interval)

    async def _process_active_tournaments(self):
        """Met à jour le temps restant pour tous les tournois actifs non pausés"""
        db = SessionLocal()
        try:
            # Récupérer tous les tournois actifs non pausés
            active_tournaments = db.query(Tournament).filter(
                Tournament.status == TournamentStatus.IN_PROGRESS,
                Tournament.paused_at.is_(None)
            ).all()

            now = datetime.utcnow()

            for tournament in active_tournaments:
                # Ignorer les tournois sans timer configuré
                if tournament.seconds_remaining is None or tournament.last_timer_update is None:
                    continue

                # Calculer le temps écoulé depuis la dernière mise à jour
                elapsed = (now - tournament.last_timer_update).total_seconds()

                # Mettre à jour le temps restant
                new_remaining = max(0, tournament.seconds_remaining - elapsed)

                # Vérifier si le temps a changé significativement (au moins 1 seconde)
                if int(new_remaining) != int(tournament.seconds_remaining):
                    tournament.seconds_remaining = new_remaining
                    tournament.last_timer_update = now

                    # Si le temps est écoulé, on pourrait automatiquement passer au niveau suivant
                    # ou envoyer une notification (logique à implémenter selon les besoins)
                    if new_remaining == 0:
                        logger.info(f"Timer completed for tournament {tournament.id}, level {tournament.current_level}")

            # Sauvegarder les modifications
            db.commit()

        except Exception as e:
            logger.error(f"Error processing active tournaments: {e}")
            db.rollback()
        finally:
            db.close()

    async def _send_timer_updates(self):
        """Envoie des mises à jour du timer à tous les clients connectés"""
        db = SessionLocal()
        try:
            # Récupérer tous les tournois actifs
            tournaments = db.query(Tournament).filter(
                Tournament.status == TournamentStatus.IN_PROGRESS
            ).all()

            for tournament in tournaments:
                # Ignorer les tournois sans timer configuré
                if tournament.seconds_remaining is None or tournament.level_duration is None:
                    continue

                # Envoyer une mise à jour WebSocket
                await notify_timer_tick(
                    tournament.id,
                    max(0, int(tournament.seconds_remaining)),
                    tournament.level_duration,
                    tournament.paused_at is not None
                )

        except Exception as e:
            logger.error(f"Error sending timer updates: {e}")
        finally:
            db.close()


# Créer une instance unique du service
timer_service = TournamentTimerService()


# Fonction pour démarrer le service lors du démarrage de l'application
async def start_timer_service():
    await timer_service.start()


# Fonction pour arrêter le service lors de l'arrêt de l'application
async def stop_timer_service():
    await timer_service.stop()