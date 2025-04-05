# backend/app/routes/websockets.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Path, Query
from sqlalchemy.orm import Session, joinedload
from typing import Dict, List, Optional
import asyncio
import json
import datetime
import logging


from ..database import get_db
from ..models.configuration import TournamentConfiguration
from ..models.models import Tournament, TournamentStatus, TournamentParticipation

router = APIRouter()

# Configuration basique du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Gestionnaire de connexions WebSocket
class TournamentConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.connection_count: Dict[int, int] = {}  # Nouveau: compteur de connexions par tournoi

    async def connect(self, websocket: WebSocket, tournament_id: int):
        await websocket.accept()

        if tournament_id not in self.active_connections:
            self.active_connections[tournament_id] = []
            self.connection_count[tournament_id] = 0

        self.active_connections[tournament_id].append(websocket)
        self.connection_count[tournament_id] += 1

        # Journaliser les informations de connexion
        logger.info(
            f"WebSocket connected to tournament {tournament_id}. Active connections: {self.connection_count[tournament_id]}")

    def disconnect(self, websocket: WebSocket, tournament_id: int):
        if tournament_id in self.active_connections:
            if websocket in self.active_connections[tournament_id]:
                self.active_connections[tournament_id].remove(websocket)
                self.connection_count[tournament_id] -= 1

                logger.info(
                    f"WebSocket disconnected from tournament {tournament_id}. Remaining connections: {self.connection_count[tournament_id]}")

            if not self.active_connections[tournament_id]:
                del self.active_connections[tournament_id]
                del self.connection_count[tournament_id]

    async def broadcast(self, message: dict, tournament_id: int):
        """Envoie un message à tous les clients connectés à un tournoi spécifique"""
        if tournament_id in self.active_connections:
            disconnected_clients = []
            success_count = 0

            for connection in self.active_connections[tournament_id]:
                try:
                    await connection.send_json(message)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Error sending message to client: {e}")
                    disconnected_clients.append(connection)

            # Nettoyer les connexions déconnectées
            for connection in disconnected_clients:
                self.disconnect(connection, tournament_id)

            logger.debug(
                f"Broadcast to tournament {tournament_id}: {success_count} clients received message, {len(disconnected_clients)} disconnected")


# Créer une instance unique du gestionnaire de connexions
connection_manager = TournamentConnectionManager()


@router.websocket("/tournaments/{tournament_id}")
async def tournament_websocket(
        websocket: WebSocket,
        tournament_id: int = Path(...),
        db: Session = Depends(get_db)
):
    """Point de terminaison WebSocket pour les mises à jour en temps réel des tournois"""
    # Vérifier que le tournoi existe avec toutes les relations nécessaires
    tournament = db.query(Tournament).options(
        joinedload(Tournament.participations).joinedload(TournamentParticipation.user),
        joinedload(Tournament.configuration).joinedload(TournamentConfiguration.blinds_structure),
        joinedload(Tournament.sound_configuration)
    ).filter(Tournament.id == tournament_id).first()

    if not tournament:
        await websocket.close(code=4004, reason="Tournament not found")
        return

    # Accepter la connexion
    await connection_manager.connect(websocket, tournament_id)

    try:
        # Envoyer l'état initial complet
        blinds_structure = None
        if tournament.configuration and tournament.configuration.blinds_structure:
            blinds_structure = tournament.configuration.blinds_structure.structure

        initial_state = {
            "type": "initial_state",
            "data": {
                "id": tournament.id,
                "name": tournament.name,
                "status": tournament.status.value,
                "current_level": tournament.current_level or 1,  # Utiliser 1 comme valeur par défaut
                "seconds_remaining": tournament.seconds_remaining or 0,
                "level_duration": tournament.level_duration or 0,
                "players_count": len(tournament.participations),
                "active_players_count": sum(1 for p in tournament.participations if p.is_active),
                "paused": tournament.paused_at is not None,
                "tables_state": tournament.tables_state or {},
                "blinds_structure": blinds_structure,  # Inclure la structure complète des blindes
                "last_update_time": tournament.last_timer_update.isoformat() if tournament.last_timer_update else None
            }
        }
        await websocket.send_json(initial_state)

        # Boucle principale pour recevoir les messages des clients
        while True:
            # Attendre un message du client
            data = await websocket.receive_json()

            # Traiter certains types de messages
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif data.get("type") == "request_sync":
                # Permettre au client de demander une synchronisation
                # Récupérer l'état actuel du tournoi
                current_tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
                if current_tournament:
                    # Envoyer un état actualisé
                    sync_state = {
                        "type": "sync_state",
                        "data": {
                            "current_level": current_tournament.current_level,
                            "seconds_remaining": current_tournament.seconds_remaining,
                            "level_duration": current_tournament.level_duration,
                            "paused": current_tournament.paused_at is not None,
                            "tables_state": current_tournament.tables_state or {},
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    }
                    await websocket.send_json(sync_state)

    except WebSocketDisconnect:
         # Gérer la déconnexion
        connection_manager.disconnect(websocket, tournament_id)
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {e}")
        # Tenter de fermer proprement la connexion
        try:
            await websocket.close(code=1011, reason=f"Internal error: {str(e)[:100]}")
        except:
            pass
        connection_manager.disconnect(websocket, tournament_id)


# Fonction utilitaire pour diffuser un événement aux clients connectés
async def broadcast_tournament_event(tournament_id: int, event_type: str, data: dict):
    """
    Diffuse un événement aux clients connectés à un tournoi
    À appeler depuis d'autres routes lorsqu'un changement se produit
    """
    message = {
        "type": event_type,
        "data": data
    }
    await connection_manager.broadcast(message, tournament_id)


# Événements du tournoi à diffuser
async def notify_tournament_started(tournament_id: int, db: Session):
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if tournament:
        await broadcast_tournament_event(
            tournament_id,
            "tournament_started",
            {"start_time": tournament.start_time.isoformat() if tournament.start_time else None}
        )


async def notify_level_change(tournament_id: int, new_level: int, level_data: dict = None, start_time: str = None):
    """Notification améliorée avec données complètes du niveau"""

    # Enrichir les données envoyées
    level_info = {
        "level": new_level,
        "small_blind": level_data.get("small_blind") if level_data else None,
        "big_blind": level_data.get("big_blind") if level_data else None,
        "duration": level_data.get("duration") if level_data else None,
        "seconds_remaining": level_data.get("duration", 15) * 60 if level_data else None,
        "level_duration": level_data.get("duration", 15) * 60 if level_data else None,
        "level_start_time": start_time
    }

    await broadcast_tournament_event(
        tournament_id,
        "level_changed",
        level_info
    )


async def notify_pause_status(tournament_id: int, is_paused: bool, seconds_remaining: int = None, level_duration: int = None):
    """Notification de pause améliorée avec données du timer"""
    await broadcast_tournament_event(
        tournament_id,
        "pause_status_changed",
        {
            "paused": is_paused,
            "seconds_remaining": seconds_remaining,
            "level_duration": level_duration,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


async def notify_player_eliminated(tournament_id: int, player_id: int, position: int):
    await broadcast_tournament_event(
        tournament_id,
        "player_eliminated",
        {
            "player_id": player_id,
            "position": position,
            "time": datetime.now().isoformat()
        }
    )


async def notify_rebuy(tournament_id: int, player_id: int, new_chips: float):
    await broadcast_tournament_event(
        tournament_id,
        "player_rebuy",
        {
            "player_id": player_id,
            "chips_added": new_chips,
            "time": datetime.now().isoformat()
        }
    )


async def notify_table_update(tournament_id: int, tables_state: dict):
    await broadcast_tournament_event(
        tournament_id,
        "tables_updated",
        {"tables_state": tables_state}
    )

# Fonction de notification de timer (envoyée périodiquement)
async def notify_timer_tick(tournament_id: int, seconds_remaining: int, total_seconds: int, is_paused: bool = False, current_level: int = 0):
    """Notification améliorée incluant le niveau actuel"""
    await broadcast_tournament_event(
        tournament_id,
        "timer_tick",
        {
            "seconds_remaining": seconds_remaining,
            "total_seconds": total_seconds,
            "percentage": (total_seconds - seconds_remaining) / total_seconds * 100 if total_seconds > 0 else 0,
            "paused": is_paused,
            "current_level": current_level
        }
    )