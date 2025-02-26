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
    db_league = league_crud.create_league(db, league, current_user.id)

    # Ajouter le créateur comme admin
    league_admin = LeagueAdmin(league_id=db_league.id, user_id=current_user.id)
    db.add(league_admin)

    db.commit()
    return db_league


@router.get("/", response_model=List[LeagueResponse])
async def get_leagues(
        db: Session = Depends(get_db)
):
    """Liste toutes les ligues avec leur membres"""
    # Récupération de toutes les ligues
    leagues = db.query(League).all()

    # Préparation de la réponse
    league_responses = []
    for league in leagues:
        league_loaded = league_crud.get_league_with_members(db, league.id)

        league_responses.append(league_loaded)
    return league_responses


@router.get("/{league_id}", response_model=LeagueResponse)
async def get_league(
    league_id: int,
    db: Session = Depends(get_db)
):
    league = league_crud.get_league_with_members(db, league_id)
    if not league:
        raise HTTPException(status_code=404, detail="Ligue non trouvée")
    return league


@router.get("/{league_id}/members", response_model=List[UserResponse])
async def get_league_members(
        league_id: int,
        db: Session = Depends(get_db)
):
    """Liste les membres d'une ligue"""
    return db.query(User).filter(User.league_id == league_id).all()