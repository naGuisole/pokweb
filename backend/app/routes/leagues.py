# routes/leagues.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func, distinct

from ..database import get_db
from ..models.models import League, LeagueAdmin, User
from .auth import get_current_user
from ..schemas.schemas import LeagueResponse, LeagueCreate, UserResponse
from ..crud import league as league_crud

router = APIRouter()


@router.post("/", response_model=LeagueResponse)
async def create_league(
        league: LeagueCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    print("création ligue")

    """Crée une nouvelle ligue avec l'utilisateur courant comme admin"""
    # La fonction create_league ajoute déjà l'utilisateur courant comme admin
    db_league = league_crud.create_league(db, league, current_user.id)

    return db_league


@router.get("/", response_model=List[LeagueResponse])
async def get_leagues(
        db: Session = Depends(get_db),
):
    """Liste toutes les ligues avec leur membres et administrateurs"""
    # Récupération de toutes les ligues
    leagues = db.query(League).all()

    # Pour chaque ligue, récupérer les membres et les administrateurs
    league_responses = []
    for league in leagues:
        # Récupérer la ligue avec ses membres
        league_data = league_crud.get_league_with_members(db, league.id)

        # Récupérer les IDs des administrateurs séparément
        admin_records = db.query(LeagueAdmin).filter(LeagueAdmin.league_id == league.id).all()
        admin_ids = [admin.user_id for admin in admin_records]

        # Créer un objet de réponse compatible avec LeagueResponse
        # au lieu de modifier directement l'objet SQLAlchemy
        league_dict = {
            "id": league_data.id,
            "name": league_data.name,
            "description": league_data.description,
            "members": league_data.members,
            "admins": admin_ids  # Ajouter les admins ici
        }

        league_responses.append(league_dict)

    return league_responses


@router.get("/{league_id}", response_model=LeagueResponse)
async def get_league(
        league_id: int,
        db: Session = Depends(get_db)
):
    """Récupère une ligue spécifique avec ses membres et administrateurs"""
    # Récupérer la ligue avec ses membres
    league = league_crud.get_league_with_members(db, league_id)
    if not league:
        raise HTTPException(status_code=404, detail="Ligue non trouvée")

    # Récupérer les IDs des administrateurs séparément
    admin_records = db.query(LeagueAdmin).filter(LeagueAdmin.league_id == league_id).all()
    admin_ids = [admin.user_id for admin in admin_records]

    # Créer un dictionnaire de réponse
    league_dict = {
        "id": league.id,
        "name": league.name,
        "description": league.description,
        "members": league.members,
        "admins": admin_ids
    }

    return league_dict


@router.post("/{league_id}/join")
async def join_league(
        league_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Demande à rejoindre une ligue"""
    # Vérifier que l'utilisateur n'est pas déjà dans une ligue
    if current_user.league_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous êtes déjà membre d'une ligue"
        )

    # Vérifier que la ligue existe
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ligue non trouvée"
        )

    # Mettre l'utilisateur en statut "en attente" pour cette ligue
    current_user.league_id = league_id
    current_user.member_status = "PENDING"
    db.commit()

    return {"status": "success", "message": "Demande d'adhésion envoyée"}


@router.post("/{league_id}/approve/{user_id}")
async def approve_member(
        league_id: int,
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Approuve un membre en attente (admin uniquement)"""
    # Vérifier si l'utilisateur actuel est admin de la ligue
    is_admin = db.query(LeagueAdmin).filter(
        LeagueAdmin.league_id == league_id,
        LeagueAdmin.user_id == current_user.id
    ).first()

    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs peuvent approuver des membres"
        )

    # Vérifier si l'utilisateur à approuver est en attente
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.league_id != league_id or user.member_status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé ou non en attente"
        )

    # Approuver l'utilisateur
    user.member_status = "APPROVED"
    db.commit()

    return {"status": "success", "message": "Membre approuvé avec succès"}


@router.post("/{league_id}/reject/{user_id}")
async def reject_member(
        league_id: int,
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Rejette un membre en attente (admin uniquement)"""
    # Vérifier si l'utilisateur actuel est admin de la ligue
    is_admin = db.query(LeagueAdmin).filter(
        LeagueAdmin.league_id == league_id,
        LeagueAdmin.user_id == current_user.id
    ).first()

    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs peuvent rejeter des membres"
        )

    # Vérifier si l'utilisateur à rejeter est en attente
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.league_id != league_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )

    # Retirer l'utilisateur de la ligue
    user.league_id = None
    user.member_status = None
    db.commit()

    return {"status": "success", "message": "Membre rejeté avec succès"}