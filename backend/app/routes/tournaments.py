# backend/app/routes/tournaments.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from ..database import get_db
from ..crud import tournament as tournament_crud
from ..schemas.schemas import (
    TournamentCreate, 
    TournamentResponse, 
    TournamentUpdate,
    TournamentStateUpdate,
    ParticipationCreate,
    RebuyRequest
)
from .auth import get_current_user
from ..models.models import TournamentType, TournamentStatus
from ..models.models import User

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
    return tournament

@router.post("/{tournament_id}/pause")
async def pause_tournament(
    tournament_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Met en pause le tournoi"""
    state_update = TournamentStateUpdate(paused_at=datetime.utcnow())
    updated = tournament_crud.update_tournament_state(
        db,
        tournament_id,
        state_update,
        current_user.id
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournoi non trouvé ou permissions insuffisantes"
        )
    return {"status": "success", "message": "Tournoi en pause"}

@router.post("/{tournament_id}/resume")
async def resume_tournament(
    tournament_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reprend le tournoi après une pause"""
    state_update = TournamentStateUpdate(paused_at=None)
    updated = tournament_crud.update_tournament_state(
        db,
        tournament_id,
        state_update,
        current_user.id
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournoi non trouvé ou permissions insuffisantes"
        )
    return {"status": "success", "message": "Tournoi repris"}

@router.post("/{tournament_id}/eliminate")
async def eliminate_player(
    tournament_id: int,
    player_id: int,
    position: int,
    prize_amount: float = 0,
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
    return {"status": "success", "message": "Joueur éliminé"}

@router.post("/{tournament_id}/rebuy")
async def process_rebuy(
    tournament_id: int,
    rebuy_request: RebuyRequest,
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
        rebuy_request.player_id,
        rebuy_request.amount
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erreur lors du rebuy"
        )
    return {"status": "success", "message": "Rebuy effectué"}

@router.post("/{tournament_id}/tables")
async def update_tables_state(
    tournament_id: int,
    tables_state: dict,
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
