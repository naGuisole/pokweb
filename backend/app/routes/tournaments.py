# backend/app/routes/tournaments.py
from typing import List, Optional
import logging

from ..schemas.schemas import (
    TournamentCreate, 
    TournamentResponse, 
    RebuyRequest
)
from ..models.models import TournamentType, TournamentStatus

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db
from ..crud import tournament as tournament_crud
from ..schemas.schemas import TournamentStateUpdate
from .auth import get_current_user
from ..models.models import User
from .websockets import (
    notify_tournament_started,
    notify_level_change,
    notify_pause_status,
    notify_player_eliminated,
    notify_rebuy,
    notify_table_update
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=TournamentResponse)
async def create_tournament(
    tournament: TournamentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crée un nouveau tournoi"""
    try:
        print("Création d'un tournoi")
        return tournament_crud.create_tournament(db, tournament, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[TournamentResponse])
async def list_tournaments(
    skip: int = 0,
    limit: int = 100,
    status: Optional[TournamentStatus] = None,
    tournament_type: Optional[TournamentType] = None,
    db: Session = Depends(get_db)
):
    """Liste les tournois avec filtres optionnels"""
    logger.debug("Recherche de la liste des tournois")

    return tournament_crud.list_tournaments(
        db, 
        skip=skip, 
        limit=limit,
        status=status,
        tournament_type=tournament_type
    )

@router.get("/{tournament_id}", response_model=TournamentResponse)
async def get_tournament(
    tournament_id: int,
    db: Session = Depends(get_db)
):
    """Récupère les détails d'un tournoi spécifique"""
    tournament = tournament_crud.get_tournament(db, tournament_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournoi non trouvé"
        )
    return tournament

@router.post("/{tournament_id}/register")
async def register_to_tournament(
    tournament_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Inscrit le joueur courant au tournoi"""
    try:
        participation = tournament_crud.register_player(
            db, 
            tournament_id, 
            current_user.id
        )
        return {"status": "success", "message": "Inscription réussie"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{tournament_id}/start")
async def start_tournament(
        tournament_id: int,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Démarre le tournoi (admin uniquement)"""
    tournament = tournament_crud.update_tournament_status(
        db,
        tournament_id,
        TournamentStatus.IN_PROGRESS,
        current_user.id
    )
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournoi non trouvé ou permissions insuffisantes"
        )

    # Ajouter la notification dans une tâche d'arrière-plan
    background_tasks.add_task(notify_tournament_started, tournament_id, db)

    return tournament


@router.post("/{tournament_id}/pause")
async def pause_tournament(
        tournament_id: int,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Met en pause le tournoi"""
    tournament = tournament_crud.get_tournament(db, tournament_id)
    if not tournament or tournament.admin_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes"
        )

    # Si déjà en pause, ne rien faire
    if tournament.paused_at:
        return {"status": "success", "message": "Tournoi déjà en pause"}

    # Mettre à jour le temps restant avant de mettre en pause
    if tournament.last_timer_update and not tournament.paused_at:
        now = datetime.utcnow()
        elapsed_since_update = int((now - tournament.last_timer_update).total_seconds())

        # Ne jamais laisser le temps restant devenir négatif
        tournament.seconds_remaining = max(0, tournament.seconds_remaining - elapsed_since_update)
        tournament.last_timer_update = now

    # Marquer comme en pause
    tournament.paused_at = datetime.utcnow()
    db.commit()

    # Notifier de la pause
    background_tasks.add_task(
        notify_pause_status,
        tournament_id,
        True,
        tournament.seconds_remaining,
        tournament.level_duration
    )

    return {"status": "success", "message": "Tournoi en pause"}


@router.post("/{tournament_id}/resume")
async def resume_tournament(
        tournament_id: int,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Reprend le tournoi après une pause"""
    tournament = tournament_crud.get_tournament(db, tournament_id)
    if not tournament or tournament.admin_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes"
        )

    # Si déjà en marche, ne rien faire
    if not tournament.paused_at:
        return {"status": "success", "message": "Tournoi déjà en marche"}

    # Mettre à jour le timestamp
    tournament.last_timer_update = datetime.utcnow()
    tournament.paused_at = None
    db.commit()

    # Notifier de la reprise
    background_tasks.add_task(
        notify_pause_status,
        tournament_id,
        False,
        tournament.seconds_remaining,
        tournament.level_duration
    )

    return {"status": "success", "message": "Tournoi repris"}


@router.post("/{tournament_id}/levels/{level_number}")
async def update_tournament_level(
        tournament_id: int,
        level_number: int,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Met à jour le niveau actuel du tournoi"""
    tournament = tournament_crud.get_tournament(db, tournament_id)
    if not tournament or tournament.admin_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes"
        )

    # Récupérer les données du niveau
    level_data = None
    if tournament.configuration and tournament.configuration.blinds_structure:
        level_data = next((level for level in tournament.configuration.blinds_structure
                           if level.get("level") == level_number), None)

    if not level_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Niveau invalide"
        )

    # Mettre à jour le niveau et le timer
    tournament.current_level = level_number
    tournament.seconds_remaining = level_data.get("duration", 15) * 60  # Convertir en secondes
    tournament.level_duration = level_data.get("duration", 15) * 60
    tournament.last_timer_update = datetime.utcnow()
    db.commit()

    # Notifier du changement de niveau
    background_tasks.add_task(
        notify_level_change,
        tournament_id,
        level_number,
        tournament.seconds_remaining,
        tournament.level_duration
    )

    return {"status": "success", "message": f"Niveau mis à jour: {level_number}"}


@router.post("/{tournament_id}/eliminate")
async def eliminate_player(
        tournament_id: int,
        player_id: int,
        position: int,
        prize_amount: float = 0,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Élimine un joueur du tournoi"""
    tournament = tournament_crud.get_tournament(db, tournament_id)
    if not tournament or tournament.admin_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes"
        )

    result = tournament_crud.process_elimination(
        db,
        tournament_id,
        player_id,
        position,
        prize_amount
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erreur lors de l'élimination du joueur"
        )

    # Notifier de l'élimination
    background_tasks.add_task(notify_player_eliminated, tournament_id, player_id, position)

    return {"status": "success", "message": "Joueur éliminé"}


@router.post("/{tournament_id}/rebuy")
async def process_rebuy(
        tournament_id: int,
        player_id: int,
        amount: float,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Traite un rebuy pour un joueur"""
    tournament = tournament_crud.get_tournament(db, tournament_id)
    if not tournament or tournament.admin_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes"
        )

    result = tournament_crud.process_rebuy(
        db,
        tournament_id,
        player_id,
        amount
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erreur lors du rebuy"
        )

    # Notifier du rebuy
    background_tasks.add_task(
        notify_rebuy,
        tournament_id,
        player_id,
        tournament.configuration.starting_chips
    )

    return {"status": "success", "message": "Rebuy effectué"}


# Nouvelle route pour mettre à jour manuellement le timer
@router.post("/{tournament_id}/timer")
async def update_timer(
        tournament_id: int,
        seconds_remaining: int,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Met à jour manuellement le temps restant du timer"""
    tournament = tournament_crud.get_tournament(db, tournament_id)
    if not tournament or tournament.admin_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes"
        )

    # Valider les données
    if seconds_remaining < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le temps restant ne peut pas être négatif"
        )

    # Mettre à jour le timer
    tournament.seconds_remaining = seconds_remaining
    tournament.last_timer_update = datetime.utcnow()
    db.commit()

    # Notifier de la mise à jour
    background_tasks.add_task(
        notify_timer_update,
        tournament_id,
        seconds_remaining,
        tournament.level_duration
    )

    return {"status": "success", "message": "Timer mis à jour"}


@router.post("/{tournament_id}/tables")
async def update_tables_state(
        tournament_id: int,
        tables_state: dict,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Met à jour l'état des tables"""
    result = tournament_crud.update_table_state(
        db,
        tournament_id,
        tables_state,
        current_user.id
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournoi non trouvé ou permissions insuffisantes"
        )

    # Notifier de la mise à jour des tables
    background_tasks.add_task(notify_table_update, tournament_id, tables_state)

    return {"status": "success", "message": "État des tables mis à jour"}

@router.post("/{tournament_id}/complete")
async def complete_tournament(
    tournament_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Termine le tournoi"""
    tournament = tournament_crud.update_tournament_status(
        db,
        tournament_id,
        TournamentStatus.COMPLETED,
        current_user.id
    )
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournoi non trouvé ou permissions insuffisantes"
        )
    return {"status": "success", "message": "Tournoi terminé"}

@router.post("/{tournament_id}/clay-token")
async def update_clay_token_holder(
    tournament_id: int,
    player_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Met à jour le détenteur du jeton d'argile"""
    tournament = tournament_crud.get_tournament(db, tournament_id)
    if not tournament or tournament.admin_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes"
        )
        
    result = tournament_crud.update_clay_token_holder(
        db,
        tournament_id,
        player_id
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erreur lors de la mise à jour du détenteur du jeton"
        )
    return {"status": "success", "message": "Détenteur du jeton mis à jour"}

@router.get("/{tournament_id}/statistics")
async def get_tournament_statistics(
    tournament_id: int,
    db: Session = Depends(get_db)
):
    """Récupère les statistiques du tournoi"""
    stats = tournament_crud.get_tournament_statistics(db, tournament_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournoi non trouvé"
        )
    return stats
