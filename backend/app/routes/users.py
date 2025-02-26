# backend/app/routes/users.py
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import logging
from pathlib import Path
from datetime import datetime


from ..database import get_db
from ..crud import user as user_crud
from ..models.models import Tournament, TournamentParticipation

from ..schemas.schemas import (
    UserResponse,
    UserCreate,
    UserUpdateProfile,
    BountyHunterResponse,
    ClayTokenHistoryResponse
)
from .auth import get_current_user
from ..models.models import User

router = APIRouter()
logger = logging.getLogger(__name__)

PROFILE_IMAGES_DIR = Path("uploads/profile_images")
PROFILE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# @router.get("/", response_model=List[UserResponse])
# async def list_users(
#     skip: int = 0,
#     limit: int = 100,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Liste tous les utilisateurs appartenant à la ligue de l'utilisateur connecté
#     (Accessible uniquement aux utilisateurs connectés)
#     """
#     users = user_crud.list_users(db, skip=skip, limit=limit)
#     return users


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Endpoint pour récupérer les informations de l'utilisateur connecté
    """
    user = user_crud.get_user_with_league(db, current_user.id)
    return user


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserUpdateProfile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Met à jour le profil de l'utilisateur connecté
    """
    updated_user = user_crud.update_user_profile(
        db, 
        current_user.id, 
        profile_data
    )
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erreur lors de la mise à jour du profil"
        )
    return updated_user

@router.post("/profile/image")
async def upload_profile_image(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload une nouvelle image de profil
    """
    # Vérification du format de l'image
    if not image.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier doit être une image"
        )
    
    # Création du nom de fichier unique
    file_extension = image.filename.split('.')[-1]
    image_path = PROFILE_IMAGES_DIR / f"profile_{current_user.id}.{file_extension}"
    
    # Sauvegarde de l'image
    try:
        with image_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la sauvegarde de l'image"
        )
    
    # Mise à jour du chemin de l'image dans le profil
    profile_update = UserUpdateProfile(profile_image_path=str(image_path))
    updated_user = user_crud.update_user_profile(
        db, 
        current_user.id, 
        profile_update
    )
    
    if not updated_user:
        # Suppression de l'image si la mise à jour échoue
        image_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour du profil"
        )
    
    return {
        "status": "success",
        "message": "Image de profil mise à jour",
        "path": str(image_path)
    }



@router.get("/current-clay-token-holder", response_model=ClayTokenHistoryResponse)
async def get_current_clay_token_holder(db: Session = Depends(get_db)):
    """Récupère l'utilisateur qui détient actuellement le jeton d'argile"""
    # On cherche le dernier tournoi terminé de type JAPT
    print("Route called")

    last_tournament = (
        db.query(Tournament)
        .filter(
                Tournament.tournament_type == 'JAPT',
                Tournament.status == 'COMPLETED',
                Tournament.clay_token_holder_id.isnot(None)
        )
        .order_by(Tournament.end_time.desc())
        .first()
    )


    if not last_tournament:
        return ClayTokenHistoryResponse(
            tournament_id=0,
            holder_id=0,
            holder_username="Aucun détenteur !",
            holder_profile_image=None,
            date=datetime.now(),
            tournament_name="Aucun tournoi"
        )


    # Construction de la réponse
    return ClayTokenHistoryResponse(
        tournament_id=last_tournament.id,
        holder_id=last_tournament.clay_token_holder_id,
        holder_username=last_tournament.clay_token_holder.username,
        holder_profile_image=last_tournament.clay_token_holder.profile_image_path,
        date=last_tournament.end_time,
        tournament_name=last_tournament.name
    )


@router.get("/bounty-hunters", response_model=List[BountyHunterResponse])
async def get_bounty_hunters_ranking(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Récupère le classement des chasseurs de primes"""
    # Calcul du nombre de primes obtenues par joueur
    bounty_hunters = (
        db.query(
            User,
            func.count(Tournament.bounty_hunter_id).label('bounty_count'),
            func.sum(Tournament.prize_pool * 0.1).label('bounty_earnings')  # 10% du prize pool
        )
        .join(Tournament, Tournament.bounty_hunter_id == User.id)
        .filter(Tournament.status == 'COMPLETED')
        .group_by(User.id)
        .order_by(desc('bounty_count'), desc('bounty_earnings'))
        .limit(limit)
        .all()
    )

    return [
        BountyHunterResponse(
            id=hunter.User.id,
            username=hunter.User.username,
            profile_image_path=hunter.User.profile_image_path,
            bounty_count=hunter.bounty_count,
            bounty_earnings=hunter.bounty_earnings
        )
        for hunter in bounty_hunters
    ]

@router.get("/clay-token/history", response_model=List[ClayTokenHistoryResponse])
async def get_clay_token_history(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Récupère l'historique des détenteurs du jeton d'argile"""
    history = (
        db.query(Tournament)
        .filter(
            Tournament.tournament_type == 'JAPT',
            Tournament.status == 'COMPLETED',
            Tournament.clay_token_holder_id.isnot(None)
        )
        .order_by(Tournament.end_time.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        ClayTokenHistoryResponse(
            tournament_id=tournament.id,
            holder_id=tournament.clay_token_holder_id,
            holder_username=tournament.clay_token_holder.username,
            holder_profile_image=tournament.clay_token_holder.profile_image_path,
            date=tournament.end_time,
            tournament_name=tournament.name
        )
        for tournament in history
    ]

@router.get("/statistics/{user_id}", response_model=dict)
async def get_user_statistics(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère les statistiques d'un joueur"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )

    # Statistiques générales
    participations = (
        db.query(TournamentParticipation)
        .filter(TournamentParticipation.user_id == user_id)
        .join(Tournament)
        .filter(Tournament.status == 'COMPLETED')
        .all()
    )

    total_games = len(participations)
    if total_games == 0:
        return {
            "total_games": 0,
            "total_earnings": 0,
            "roi": 0,
            "average_position": 0,
            "victories": 0,
            "bounties": 0
        }

    total_buyin = sum(p.total_buyin for p in participations)
    total_earnings = sum(p.prize_won for p in participations)
    roi = ((total_earnings - total_buyin) / total_buyin * 100) if total_buyin > 0 else 0

    # Nombre de victoires
    victories = sum(1 for p in participations if p.current_position == 1)

    # Nombre de primes obtenues
    bounties = (
        db.query(func.count(Tournament.id))
        .filter(Tournament.bounty_hunter_id == user_id)
        .scalar()
    )

    # Position moyenne
    avg_position = sum(p.current_position for p in participations) / total_games

    return {
        "total_games": total_games,
        "total_earnings": total_earnings,
        "roi": roi,
        "average_position": avg_position,
        "victories": victories,
        "bounties": bounties
    }

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les informations d'un utilisateur spécifique
    """
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    return user