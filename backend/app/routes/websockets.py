# backend/app/routes/websockets.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Path, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import asyncio
import json
import datetime

from ..database import get_db
from ..models.models import Tournament, TournamentStatus

router = APIRouter()


# Gestionnaire de connexions WebSocket
class TournamentConnectionManager:
    def __init__(self):
        # Dictionnaire des connexions actives par tournoi
        # {tournament_id: [websocket1, websocket2, ...]}
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, tournament_id: int):
        await websocket.accept()

        if tournament_id not in self.active_connections:
            self.active_connections[tournament_id] = []

        self.active_connections[tournament_id].append(websocket)

    def disconnect(self, websocket: WebSocket, tournament_id: int):
        if tournament_id in self.active_connections:
            if websocket in self.active_connections[tournament_id]:
                self.active_connections[tournament_id].remove(websocket)

            if not self.active_connections[tournament_id]:
                del self.active_connections[tournament_id]

    async def broadcast(self, message: dict, tournament_id: int):
        """Envoie un message à tous les clients connectés à un tournoi spécifique"""
        if tournament_id in self.active_connections:
            disconnected_clients = []

            for connection in self.active_connections[tournament_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected_clients.append(connection)

            # Nettoyer les connexions déconnectées
            for connection in disconnected_clients:
                self.disconnect(connection, tournament_id)


# Créer une instance unique du gestionnaire de connexions
connection_manager = TournamentConnectionManager()


@router.websocket("/tournaments/{tournament_id}")
async def tournament_websocket(
        websocket: WebSocket,
        tournament_id: int = Path(...),
        db: Session = Depends(get_db)
):
    """Point de terminaison WebSocket pour les mises à jour en temps réel des tournois"""
    # Vérifier que le tournoi existe
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        await websocket.close(code=4004, reason="Tournament not found")
        return

    # Accepter la connexion
    await connection_manager.connect(websocket, tournament_id)

    try:
        # Envoyer l'état initial
        initial_state = {
            "type": "initial_state",
            "data": {
                "id": tournament.id,
                "name": tournament.name,
                "status": tournament.status.value,
                "current_level": tournament.current_level,
                "players_count": len(tournament.participations),
                "active_players_count": sum(1 for p in tournament.participations if p.is_active),
                "paused": tournament.paused_at is not None,
                "tables_state": tournament.tables_state
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

    except WebSocketDisconnect:
        # Gérer la déconnexion
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


async def notify_level_change(tournament_id: int, new_level: int, db: Session):
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if tournament and tournament.configuration:
        blinds_structure = tournament.configuration.blinds_structure
        current_level_data = next((l for l in blinds_structure if l.get("level") == new_level), None)

        await broadcast_tournament_event(
            tournament_id,
            "level_changed",
            {
                "level": new_level,
                "small_blind": current_level_data["small_blind"] if current_level_data else None,
                "big_blind": current_level_data["big_blind"] if current_level_data else None,
                "duration": current_level_data["duration"] if current_level_data else None
            }
        )


async def notify_pause_status(tournament_id: int, is_paused: bool):
    await broadcast_tournament_event(
        tournament_id,
        "pause_status_changed",
        {"paused": is_paused}
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