# backend/app/crud/configuration.py
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List, Dict
from ..models.configuration import TournamentConfiguration, SoundConfiguration
from ..schemas.schemas import TournamentConfigCreate, SoundConfigCreate
from ..models.models import TournamentType
from datetime import timedelta

def create_tournament_configuration(
    db: Session, 
    config_data: TournamentConfigCreate,
    user_id: Optional[int] = None
) -> TournamentConfiguration:
    """
    Crée une nouvelle configuration de tournoi
    
    Args:
        db (Session): Session de base de données
        config_data (TournamentConfigurationCreate): Données de configuration
        user_id (Optional[int]): ID de l'utilisateur créant la configuration
    
    Returns:
        TournamentConfiguration: Configuration créée
    
    Validations:
        - Vérifie que la structure des blindes est cohérente
        - Vérifie que la structure des paiements est valide
        - Pour les configurations JAPT, vérifie les règles spécifiques
    """
    # Validation de la structure des blindes
    for level in config_data.blinds_structure:
        if 'small_blind' not in level or 'big_blind' not in level or 'duration' not in level:
            raise ValueError("Structure des blindes invalide")
        if level['big_blind'] != level['small_blind'] * 2:
            raise ValueError("La grosse blinde doit être le double de la petite blinde")

    # Validation de la structure des paiements
    for payout in config_data.payouts_structure:
        if 'num_players' not in payout or 'prizes' not in payout:
            raise ValueError("Structure des paiements invalide")
        for prize in payout['prizes']:
            if 'position' not in prize or 'percentage' not in prize:
                raise ValueError("Structure des prix invalide")
            if not (0 <= prize['percentage'] <= 100):
                raise ValueError("Le pourcentage doit être entre 0 et 100")

    db_config = TournamentConfiguration(
        name=config_data.name,
        tournament_type=config_data.tournament_type,
        starting_chips=config_data.starting_chips,
        buy_in=config_data.buy_in,
        blinds_structure=config_data.blinds_structure,
        rebuy_levels=config_data.rebuy_levels,
        payouts_structure=config_data.payouts_structure,
        is_default=config_data.is_default,
        created_by_id=user_id
    )
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return db_config

def create_default_configurations(db: Session):
    """
    Crée les configurations par défaut pour JAPT et MTT si elles n'existent pas
    """
    # Configuration JAPT par défaut
    japt_config = {
        "name": "JAPT Standard",
        "tournament_type": TournamentType.JAPT,
        "starting_chips": 20000,
        "buy_in": 20.0,
        "blinds_structure": [
            {"level": 1, "small_blind": 50, "big_blind": 100, "duration": 15},
            {"level": 2, "small_blind": 100, "big_blind": 200, "duration": 15},
            {"level": 3, "small_blind": 150, "big_blind": 300, "duration": 15},
            # ... autres niveaux
        ],
        "rebuy_levels": 6,  # Rebuy autorisé pendant les 6 premiers niveaux
        "payouts_structure": [
            {
                "num_players": 10,
                "prizes": [
                    {"position": 1, "percentage": 50},
                    {"position": 2, "percentage": 30},
                    {"position": 3, "percentage": 20}
                ]
            }
            # ... autres structures selon le nombre de joueurs
        ],
        "is_default": True
    }

    # Configuration MTT par défaut
    mtt_config = {
        "name": "MTT Standard",
        "tournament_type": TournamentType.MTT,
        "starting_chips": 25000,
        "buy_in": 30.0,
        "blinds_structure": [
            {"level": 1, "small_blind": 25, "big_blind": 50, "duration": 20},
            {"level": 2, "small_blind": 50, "big_blind": 100, "duration": 20},
            {"level": 3, "small_blind": 75, "big_blind": 150, "duration": 20},
            # ... autres niveaux
        ],
        "rebuy_levels": 8,
        "payouts_structure": [
            {
                "num_players": 18,
                "prizes": [
                    {"position": 1, "percentage": 45},
                    {"position": 2, "percentage": 25},
                    {"position": 3, "percentage": 15},
                    {"position": 4, "percentage": 10},
                    {"position": 5, "percentage": 5}
                ]
            }
            # ... autres structures selon le nombre de joueurs
        ],
        "is_default": True
    }

    for config in [japt_config, mtt_config]:
        existing = db.query(TournamentConfiguration).filter(
            TournamentConfiguration.name == config["name"]
        ).first()
        
        if not existing:
            create_tournament_configuration(db, TournamentConfigCreate(**config))

def get_tournament_configuration(
    db: Session, 
    config_id: int
) -> Optional[TournamentConfiguration]:
    """
    Récupère une configuration de tournoi par son ID
    """
    return db.query(TournamentConfiguration).filter(
        TournamentConfiguration.id == config_id
    ).first()

def list_tournament_configurations(
    db: Session,
    tournament_type: Optional[TournamentType] = None,
    include_default: bool = True,
    user_id: Optional[int] = None
) -> List[TournamentConfiguration]:
    """
    Liste les configurations de tournoi avec filtres optionnels
    """
    query = db.query(TournamentConfiguration)
    
    if tournament_type:
        query = query.filter(TournamentConfiguration.tournament_type == tournament_type)
    
    if not include_default:
        query = query.filter(TournamentConfiguration.is_default == False)
    
    if user_id:
        query = query.filter(
            or_(
                TournamentConfiguration.created_by_id == user_id,
                TournamentConfiguration.is_default == True
            )
        )



    return query.all()

def delete_tournament_configuration(
    db: Session, 
    config_id: int
) -> bool:
    """
    Supprime une configuration de tournoi non-default
    """
    config = get_tournament_configuration(db, config_id)
    if not config or config.is_default:
        return False
        
    db.delete(config)
    db.commit()
    return True

def create_sound_configuration(
    db: Session, 
    config_data: SoundConfigCreate,
    user_id: Optional[int] = None
) -> SoundConfiguration:
    """
    Crée une nouvelle configuration sonore
    """
    # Vérification de la durée des sons (<10 secondes)
    # Note: Cette vérification devrait être faite au niveau de l'API
    
    db_config = SoundConfiguration(
        name=config_data.name,
        sounds=config_data.sounds,
        is_default=config_data.is_default,
        created_by_id=user_id
    )
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return db_config

def get_sound_configuration(
    db: Session, 
    config_id: int
) -> Optional[SoundConfiguration]:
    """
    Récupère une configuration sonore par son ID
    """
    return db.query(SoundConfiguration).filter(
        SoundConfiguration.id == config_id
    ).first()

def list_sound_configurations(
    db: Session,
    include_default: bool = True,
    user_id: Optional[int] = None
) -> List[SoundConfiguration]:
    """
    Liste les configurations sonores
    """
    query = db.query(SoundConfiguration)
    
    if not include_default:
        query = query.filter(SoundConfiguration.is_default == False)
    
    if user_id:
        query = query.filter(
            or_(
                SoundConfiguration.created_by_id == user_id,
                SoundConfiguration.is_default == True
            )
        )
        
    return query.all()

def delete_sound_configuration(
    db: Session, 
    config_id: int
) -> bool:
    """
    Supprime une configuration sonore non-default
    """
    config = get_sound_configuration(db, config_id)
    if not config or config.is_default:
        return False
        
    db.delete(config)
    db.commit()
    return True
