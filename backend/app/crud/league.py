from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
import bcrypt
from typing import Optional

from ..models.models import League, LeagueAdmin, User
from ..schemas.schemas import LeagueCreate, LeagueResponse

# crud/leagues.py
def create_league(db: Session, league: LeagueCreate, admin_id: int) -> League:
    # Création de la ligue
    db_league = League(
        name=league.name,
        description=league.description
    )
    db.add(db_league)
    db.commit()
    db.refresh(db_league)

    # Ajout de l'administrateur
    admin = db.query(User).filter(User.id == admin_id).first()
    if not admin:
        raise ValueError("Utilisateur administrateur non trouvé")

    # Association admin-league
    league_admin = LeagueAdmin(
        league_id=db_league.id,
        user_id=admin_id
    )
    db.add(league_admin)

    # Mettre à jour la ligue de l'admin
    admin.league_id = db_league.id

    db.commit()
    return db_league

def get_league_with_members(db: Session, league_id: int):
    # Récupérer la ligue avec ses membres et admins
    print("Loading league : " + str(league_id))
    league = (
        db.query(League)
        .options(joinedload(League.members))  # Charge les membres
        .options(joinedload(League.admins))   # Charge les admins
        .filter(League.id == league_id)
        .first()
    )
    print("league : " + str(league))
    if league:
        # Utiliser directement les listes chargées pour les compteurs
        setattr(league, 'member_count', len(league.members))
        setattr(league, 'admin_count', len(league.admins))
        print(league.member_count)

    return league


def add_league_admin(db: Session, league_id: int, user_id: int) -> bool:
    # Vérifier que l'utilisateur existe et appartient à la ligue
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.league_id != league_id:
        raise ValueError("L'utilisateur doit être membre de la ligue")

    # Ajouter l'administrateur
    league_admin = LeagueAdmin(league_id=league_id, user_id=user_id)
    db.add(league_admin)
    db.commit()
    return True