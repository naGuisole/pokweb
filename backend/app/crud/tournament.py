# backend/app/crud/tournament.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from typing import Optional, List, Dict
from datetime import datetime

from ..models.models import Tournament, TournamentParticipation, TournamentStatus, TournamentType
from ..schemas.schemas import TournamentCreate, TournamentUpdate, ParticipationCreate, ParticipationUpdate
from ..models.models import User

def create_tournament(db: Session, tournament: TournamentCreate, admin_id: int) -> Tournament:
    """
    Crée un nouveau tournoi
    
    Args:
        db (Session): Session de base de données
        tournament (TournamentCreate): Données du tournoi
        admin_id (int): ID de l'administrateur
    
    Returns:
        Tournament: Tournoi créé
    """

    print("Début création tournoi dans la bd !")
    # Vérifier que l'admin appartient à la ligue
    admin = db.query(User).filter(User.id == admin_id).first()
    if not admin or admin.league_id != tournament.league_id:
        raise ValueError("L'administrateur doit appartenir à la ligue")

    # Vérifier que le tournoi n'existe pas déja (sous le meme nom)
    if db.query(Tournament).filter(Tournament.name == tournament.name).first():
        raise ValueError("Un tournoi existe déja avec ce nom : " + tournament.name)


    db_tournament = Tournament(
        **tournament.dict(),
        admin_id=admin_id,
        status=TournamentStatus.PLANNED
    )

    db.add(db_tournament)
    db.commit()
    db.refresh(db_tournament)

    print ("tournoi créé dans la bd !")
    return db_tournament

def get_tournament(db: Session, tournament_id: int) -> Optional[Tournament]:
    """
    Récupère un tournoi par son ID avec ses participations
    """
    return db.query(Tournament).options(
        joinedload(Tournament.participations).joinedload(TournamentParticipation.user)
    ).filter(Tournament.id == tournament_id).first()



def list_tournaments(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[TournamentStatus] = None,
        tournament_type: Optional[TournamentType] = None
) -> List[Tournament]:
    """
    Liste les tournois avec filtres optionnels
    """
    query = db.query(Tournament).options(
        joinedload(Tournament.participations).joinedload(TournamentParticipation.user)
    ).order_by(desc(Tournament.date))

    if status:
        query = query.filter(Tournament.status == status)
    if tournament_type:
        query = query.filter(Tournament.tournament_type == tournament_type)

    return query.offset(skip).limit(limit).all()

def update_tournament_status(
    db: Session, 
    tournament_id: int, 
    new_status: TournamentStatus, 
    admin_id: int
) -> Optional[Tournament]:
    """
    Met à jour le statut d'un tournoi
    """
    tournament = get_tournament(db, tournament_id)
    
    if not tournament or tournament.admin_id != admin_id:
        return None
        
    if new_status == TournamentStatus.IN_PROGRESS:
        tournament.start_time = datetime.utcnow()
    elif new_status == TournamentStatus.COMPLETED:
        tournament.end_time = datetime.utcnow()
        
    tournament.status = new_status
    db.commit()
    db.refresh(tournament)
    return tournament

def register_player(db: Session, tournament_id: int, user_id: int) -> TournamentParticipation:
    """
    Inscrit un joueur à un tournoi
    """
    tournament = get_tournament(db, tournament_id)
    print("tournament = " + str(tournament))
    if not tournament or tournament.status != TournamentStatus.PLANNED:
        raise ValueError("Tournoi non trouvé ou inscriptions closes")

    # Vérifier que le tournoi et l'utilisateur existent et sont dans la même ligue
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    user = db.query(User).filter(User.id == user_id).first()
    print("user = " + str(user))

    if not tournament or not user:
        raise ValueError("Utilisateur non trouvé")

    if user.league_id != tournament.league_id:
        raise ValueError("L'utilisateur doit appartenir à la même ligue que le tournoi")


    # Vérifier si le joueur n'est pas déjà inscrit
    existing = db.query(TournamentParticipation).filter(
        and_(
            TournamentParticipation.tournament_id == tournament_id,
            TournamentParticipation.user_id == user_id
        )
    ).first()
    print("existing = " + str(existing))
    if existing:
        raise ValueError("Joueur déjà inscrit")
        
    # Vérifier le nombre maximum de joueurs
    current_players = db.query(TournamentParticipation).filter(
        TournamentParticipation.tournament_id == tournament_id
    ).count()
    
    if current_players >= tournament.max_players:
        raise ValueError("Nombre maximum de joueurs atteint")
        
    # Créer la participation
    participation = TournamentParticipation(
        tournament_id=tournament_id,
        user_id=user_id,
        total_buyin=tournament.buy_in
    )
    print("participation = " + str(participation))
    db.add(participation)
    db.commit()
    db.refresh(participation)
    
    return participation

def process_elimination(
    db: Session,
    tournament_id: int,
    player_id: int,
    final_position: int,
    prize_amount: float = 0
) -> Optional[TournamentParticipation]:
    """
    Traite l'élimination d'un joueur
    """
    participation = db.query(TournamentParticipation).filter(
        and_(
            TournamentParticipation.tournament_id == tournament_id,
            TournamentParticipation.user_id == player_id,
            TournamentParticipation.is_active == True
        )
    ).first()
    
    if not participation:
        return None
        
    participation.is_active = False
    participation.elimination_time = datetime.utcnow()
    participation.current_position = final_position
    participation.prize_won = prize_amount

    db.commit()
    db.refresh(participation)
    return participation

def process_rebuy(
    db: Session,
    tournament_id: int,
    player_id: int,
    rebuy_amount: float
) -> Optional[TournamentParticipation]:
    """
    Traite un rebuy pour un joueur
    """
    participation = db.query(TournamentParticipation).filter(
        and_(
            TournamentParticipation.tournament_id == tournament_id,
            TournamentParticipation.user_id == player_id,
            TournamentParticipation.is_active == True
        )
    ).first()
    
    if not participation:
        return None
        
    # Mettre à jour les statistiques du rebuy
    participation.num_rebuys += 1
    participation.total_buyin += rebuy_amount

    # Mettre à jour les totaux du tournoi
    tournament = participation.tournament
    tournament.total_buyin += rebuy_amount
    tournament.total_rebuys += 1
    tournament.prize_pool = tournament.total_buyin  # Ou appliquer une formule spécifique
    
    db.commit()
    db.refresh(participation)
    return participation

def update_table_state(
    db: Session,
    tournament_id: int,
    new_state: Dict,
    admin_id: int
) -> Optional[Tournament]:
    """
    Met à jour l'état des tables
    """
    tournament = get_tournament(db, tournament_id)
    
    if not tournament or tournament.admin_id != admin_id:
        return None
        
    tournament.tables_state = new_state
    db.commit()
    db.refresh(tournament)
    return tournament
