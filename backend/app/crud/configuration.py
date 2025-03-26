# backend/app/crud/configuration.py
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List, Dict
from ..models.configuration import TournamentConfiguration, SoundConfiguration, BlindsStructure, PayoutStructure
from ..schemas.schemas import (
    TournamentConfigCreate, SoundConfigCreate, BlindsStructureCreate, PayoutStructureCreate,
    TournamentConfigResponse, SoundConfigResponse, BlindsStructureResponse, PayoutStructureResponse
)
from ..models.models import TournamentType


# ---------------------- Fonctions CRUD pour BlindsStructure ----------------------

def create_blinds_structure(
        db: Session,
        blinds_structure_data: BlindsStructureCreate,
        user_id: Optional[int] = None
) -> BlindsStructure:
    """
    Crée une nouvelle structure de blindes
    """
    db_blinds_structure = BlindsStructure(
        name=blinds_structure_data.name,
        structure=blinds_structure_data.structure,
        created_by_id=user_id
    )

    db.add(db_blinds_structure)
    db.commit()
    db.refresh(db_blinds_structure)

    return db_blinds_structure


def get_blinds_structure(db: Session, structure_id: int) -> Optional[BlindsStructure]:
    """
    Récupère une structure de blindes par son ID
    """
    return db.query(BlindsStructure).filter(BlindsStructure.id == structure_id).first()


def list_blinds_structures(
        db: Session,
        user_id: Optional[int] = None
) -> List[BlindsStructure]:
    """
    Liste les structures de blindes
    """
    query = db.query(BlindsStructure)

    if user_id:
        query = query.filter(
            or_(
                BlindsStructure.created_by_id == user_id,
                BlindsStructure.id.in_(
                    db.query(TournamentConfiguration.blinds_structure_id)
                    .filter(TournamentConfiguration.is_default == True)
                )
            )
        )

    return query.all()


def update_blinds_structure(
        db: Session,
        structure_id: int,
        blinds_structure_data: BlindsStructureCreate
) -> Optional[BlindsStructure]:
    """
    Met à jour une structure de blindes
    """
    db_blinds_structure = get_blinds_structure(db, structure_id)
    if not db_blinds_structure:
        return None

    # Mise à jour des attributs
    db_blinds_structure.name = blinds_structure_data.name
    db_blinds_structure.structure = blinds_structure_data.structure

    db.commit()
    db.refresh(db_blinds_structure)

    return db_blinds_structure


def delete_blinds_structure(
        db: Session,
        structure_id: int
) -> bool:
    """
    Supprime une structure de blindes
    """
    db_blinds_structure = get_blinds_structure(db, structure_id)
    if not db_blinds_structure:
        return False

    # Vérifier si des configurations utilisent cette structure
    configs_using_structure = db.query(TournamentConfiguration).filter(
        TournamentConfiguration.blinds_structure_id == structure_id
    ).count()

    if configs_using_structure > 0:
        return False  # Ne pas supprimer si utilisée

    db.delete(db_blinds_structure)
    db.commit()

    return True


# ---------------------- Fonctions CRUD pour PayoutStructure ----------------------

def create_payout_structure(
        db: Session,
        payout_structure_data: PayoutStructureCreate,
        user_id: Optional[int] = None
) -> PayoutStructure:
    """
    Crée une nouvelle structure de paiements
    """
    db_payout_structure = PayoutStructure(
        name=payout_structure_data.name,
        starting_chips=payout_structure_data.starting_chips,
        rebuy_levels=payout_structure_data.rebuy_levels,
        structure=payout_structure_data.structure,
        created_by_id=user_id
    )

    db.add(db_payout_structure)
    db.commit()
    db.refresh(db_payout_structure)

    return db_payout_structure


def get_payout_structure(db: Session, structure_id: int) -> Optional[PayoutStructure]:
    """
    Récupère une structure de paiements par son ID
    """
    return db.query(PayoutStructure).filter(PayoutStructure.id == structure_id).first()


def list_payout_structures(
        db: Session,
        user_id: Optional[int] = None
) -> List[PayoutStructure]:
    """
    Liste les structures de paiements
    """
    query = db.query(PayoutStructure)

    if user_id:
        query = query.filter(
            or_(
                PayoutStructure.created_by_id == user_id,
                PayoutStructure.id.in_(
                    db.query(TournamentConfiguration.payout_structure_id)
                    .filter(TournamentConfiguration.is_default == True)
                )
            )
        )

    return query.all()


def update_payout_structure(
        db: Session,
        structure_id: int,
        payout_structure_data: PayoutStructureCreate
) -> Optional[PayoutStructure]:
    """
    Met à jour une structure de paiements
    """
    db_payout_structure = get_payout_structure(db, structure_id)
    if not db_payout_structure:
        return None

    # Mise à jour des attributs
    db_payout_structure.name = payout_structure_data.name
    db_payout_structure.starting_chips = payout_structure_data.starting_chips
    db_payout_structure.rebuy_levels = payout_structure_data.rebuy_levels
    db_payout_structure.structure = payout_structure_data.structure

    db.commit()
    db.refresh(db_payout_structure)

    return db_payout_structure


def delete_payout_structure(
        db: Session,
        structure_id: int
) -> bool:
    """
    Supprime une structure de paiements
    """
    db_payout_structure = get_payout_structure(db, structure_id)
    if not db_payout_structure:
        return False

    # Vérifier si des configurations utilisent cette structure
    configs_using_structure = db.query(TournamentConfiguration).filter(
        TournamentConfiguration.payout_structure_id == structure_id
    ).count()

    if configs_using_structure > 0:
        return False  # Ne pas supprimer si utilisée

    db.delete(db_payout_structure)
    db.commit()

    return True


# ---------------------- Fonctions CRUD pour TournamentConfiguration ----------------------

def create_tournament_configuration(
        db: Session,
        config_data: TournamentConfigCreate,
        user_id: Optional[int] = None
) -> TournamentConfiguration:
    """
    Crée une nouvelle configuration de tournoi
    """
    # Vérifier que les structures existent
    blinds_structure = get_blinds_structure(db, config_data.blinds_structure_id)
    if not blinds_structure:
        raise ValueError("Structure de blindes non trouvée")

    payout_structure = get_payout_structure(db, config_data.payout_structure_id)
    if not payout_structure:
        raise ValueError("Structure de paiements non trouvée")

    sound_config = None
    if config_data.sound_configuration_id:
        sound_config = get_sound_configuration(db, config_data.sound_configuration_id)
        if not sound_config:
            raise ValueError("Configuration sonore non trouvée")

    db_config = TournamentConfiguration(
        name=config_data.name,
        tournament_type=config_data.tournament_type,
        buy_in=config_data.buy_in,
        is_default=config_data.is_default,
        blinds_structure_id=config_data.blinds_structure_id,
        payout_structure_id=config_data.payout_structure_id,
        sound_configuration_id=config_data.sound_configuration_id,
        created_by_id=user_id
    )

    db.add(db_config)
    db.commit()
    db.refresh(db_config)

    return db_config


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


def update_tournament_configuration(
        db: Session,
        config_id: int,
        config_data: TournamentConfigCreate
) -> Optional[TournamentConfiguration]:
    """
    Met à jour une configuration de tournoi
    """
    db_config = get_tournament_configuration(db, config_id)
    if not db_config:
        return None

    # Vérifier que les structures existent
    blinds_structure = get_blinds_structure(db, config_data.blinds_structure_id)
    if not blinds_structure:
        raise ValueError("Structure de blindes non trouvée")

    payout_structure = get_payout_structure(db, config_data.payout_structure_id)
    if not payout_structure:
        raise ValueError("Structure de paiements non trouvée")

    if config_data.sound_configuration_id:
        sound_config = get_sound_configuration(db, config_data.sound_configuration_id)
        if not sound_config:
            raise ValueError("Configuration sonore non trouvée")

    # Mise à jour des attributs
    db_config.name = config_data.name
    db_config.tournament_type = config_data.tournament_type
    db_config.buy_in = config_data.buy_in
    db_config.is_default = config_data.is_default
    db_config.blinds_structure_id = config_data.blinds_structure_id
    db_config.payout_structure_id = config_data.payout_structure_id
    db_config.sound_configuration_id = config_data.sound_configuration_id

    db.commit()
    db.refresh(db_config)

    return db_config


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


# ---------------------- Fonctions CRUD pour SoundConfiguration ----------------------
# Ces fonctions peuvent rester largement inchangées

def create_sound_configuration(
        db: Session,
        config_data: SoundConfigCreate,
        user_id: Optional[int] = None
) -> SoundConfiguration:
    """
    Crée une nouvelle configuration sonore
    """
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


def create_default_blinds_structures(db: Session):
    """
    Crée les structures de blindes par défaut si elles n'existent pas
    """
    # Structure pour JAPT
    japt_blinds = {
        "name": "JAPT Standard Blinds",
        "structure": [
            {"level": 1, "small_blind": 25, "big_blind": 25, "duration": 20},
            {"level": 2, "small_blind": 25, "big_blind": 50, "duration": 20},
            {"level": 3, "small_blind": 50, "big_blind": 100, "duration": 20},
            {"level": 4, "small_blind": 75, "big_blind": 150, "duration": 20},
            {"level": 5, "small_blind": 100, "big_blind": 200, "duration": 20},
            {"level": 6, "small_blind": 150, "big_blind": 300, "duration": 20},
            {"level": 7, "small_blind": 200, "big_blind": 400, "duration": 20},
            {"level": 8, "small_blind": 250, "big_blind": 500, "duration": 20},
            {"level": 9, "small_blind": 300, "big_blind": 600, "duration": 20},
            {"level": 10, "small_blind": 400, "big_blind": 800, "duration": 20},
            {"level": 11, "small_blind": 500, "big_blind": 1000, "duration": 20},
            {"level": 12, "small_blind": 600, "big_blind": 1200, "duration": 20},
            {"level": 13, "small_blind": 800, "big_blind": 1600, "duration": 20},
            {"level": 14, "small_blind": 1000, "big_blind": 2000, "duration": 20},
            {"level": 15, "small_blind": 1500, "big_blind": 3000, "duration": 20},
            {"level": 16, "small_blind": 2000, "big_blind": 4000, "duration": 99}

        ]
    }

    # Structure pour MTT
    mtt_blinds = {
        "name": "MTT Standard Blinds",
        "structure": [
            {"level": 1, "small_blind": 25, "big_blind": 25, "duration": 20},
            {"level": 2, "small_blind": 25, "big_blind": 50, "duration": 20},
            {"level": 3, "small_blind": 50, "big_blind": 100, "duration": 20},
            {"level": 4, "small_blind": 75, "big_blind": 150, "duration": 20},
            {"level": 5, "small_blind": 100, "big_blind": 200, "duration": 25},
            {"level": 6, "small_blind": 150, "big_blind": 300, "duration": 25},
            {"level": 7, "small_blind": 200, "big_blind": 400, "duration": 25},
            {"level": 8, "small_blind": 250, "big_blind": 500, "duration": 25},
            {"level": 9, "small_blind": 300, "big_blind": 600, "duration": 30},
            {"level": 10, "small_blind": 400, "big_blind": 800, "duration": 30},
            {"level": 11, "small_blind": 500, "big_blind": 1000, "duration": 30},
            {"level": 12, "small_blind": 600, "big_blind": 1200, "duration": 30},
            {"level": 13, "small_blind": 800, "big_blind": 1600, "duration": 30},
            {"level": 14, "small_blind": 1000, "big_blind": 2000, "duration": 30},
            {"level": 15, "small_blind": 1500, "big_blind": 3000, "duration": 30},
            {"level": 16, "small_blind": 2000, "big_blind": 4000, "duration": 30},
            {"level": 17, "small_blind": 2500, "big_blind": 5000, "duration": 30},
            {"level": 18, "small_blind": 3000, "big_blind": 6000, "duration": 30},
            {"level": 19, "small_blind": 4000, "big_blind": 8000, "duration": 30},
            {"level": 20, "small_blind": 5000, "big_blind": 10000, "duration": 30},
            {"level": 21, "small_blind": 7500, "big_blind": 15000, "duration": 99}
        ]
    }

    # Structure pour Classique
    classic_blinds = {
        "name": "Classique Standard Blinds",
        "structure": [
            {"level": 1, "small_blind": 25, "big_blind": 25, "duration": 15},
            {"level": 2, "small_blind": 25, "big_blind": 50, "duration": 15},
            {"level": 3, "small_blind": 50, "big_blind": 100, "duration": 15},
            {"level": 4, "small_blind": 75, "big_blind": 150, "duration": 15},
            {"level": 5, "small_blind": 100, "big_blind": 200, "duration": 15},
            {"level": 6, "small_blind": 150, "big_blind": 300, "duration": 15},
            {"level": 7, "small_blind": 200, "big_blind": 400, "duration": 15},
            {"level": 8, "small_blind": 250, "big_blind": 500, "duration": 15},
            {"level": 9, "small_blind": 300, "big_blind": 600, "duration": 15},
            {"level": 10, "small_blind": 400, "big_blind": 800, "duration": 15},
            {"level": 11, "small_blind": 500, "big_blind": 1000, "duration": 15},
            {"level": 12, "small_blind": 600, "big_blind": 1200, "duration": 15},
            {"level": 13, "small_blind": 800, "big_blind": 1600, "duration": 15},
            {"level": 14, "small_blind": 1000, "big_blind": 2000, "duration": 15},
            {"level": 15, "small_blind": 1500, "big_blind": 3000, "duration": 15},
            {"level": 16, "small_blind": 2000, "big_blind": 4000, "duration": 99}
        ]
    }

    # Créer les structures si elles n'existent pas
    for blinds_data in [japt_blinds, mtt_blinds, classic_blinds]:
        existing = db.query(BlindsStructure).filter(
            BlindsStructure.name == blinds_data["name"]
        ).first()

        if not existing:
            db_blinds = BlindsStructure(
                name=blinds_data["name"],
                structure=blinds_data["structure"]
            )
            db.add(db_blinds)

    db.commit()


def create_default_payout_structures(db: Session):
    """
    Crée les structures de paiements par défaut si elles n'existent pas
    """
    # Structure pour JAPT
    japt_payout = {
        "name": "JAPT Standard Payouts",
        "starting_chips": 20000,
        "rebuy_levels": 6,
        "structure": [
            {
                "num_players": 1,
                "prizes": [
                    {"position": 1, "percentage": 100},
                ]
            },
            {
                "num_players": 2,
                "prizes": [
                    {"position": 1, "percentage": 100},
                ]
            },
            {
                "num_players": 3,
                "prizes": [
                    {"position": 1, "percentage": 100},
                ]
            },
            {
                "num_players": 4,
                "prizes": [
                    {"position": 1, "percentage": 100},
                ]
            },
            {
                "num_players": 5,
                "prizes": [
                    {"position": 1, "percentage": 100},
                ]
            },
            {
                "num_players": 6,
                "prizes": [
                    {"position": 1, "percentage": 100},
                ]
            },
            {
                "num_players": 7,
                "prizes": [
                    {"position": 1, "percentage": 50},
                    {"position": 2, "percentage": 30},
                    {"position": 3, "percentage": 20}
                ]
            },
            {
                "num_players": 8,
                "prizes": [
                    {"position": 1, "percentage": 50},
                    {"position": 2, "percentage": 30},
                    {"position": 3, "percentage": 20}
                ]
            },
            {
                "num_players": 9,
                "prizes": [
                    {"position": 1, "percentage": 50},
                    {"position": 2, "percentage": 30},
                    {"position": 3, "percentage": 20}
                ]
            },
            {
                "num_players": 10,
                "prizes": [
                    {"position": 1, "percentage": 50},
                    {"position": 2, "percentage": 30},
                    {"position": 3, "percentage": 20}
                ]
            },
        ]
    }

    # Structure pour MTT
    mtt_payout = {
        "name": "MTT Standard Payouts",
        "starting_chips": 25000,
        "rebuy_levels": 8,
        "structure": [
            {
                "num_players": 18,
                "prizes": [
                    {"position": 1, "percentage": 45},
                    {"position": 2, "percentage": 25},
                    {"position": 3, "percentage": 15},
                    {"position": 4, "percentage": 10},
                    {"position": 5, "percentage": 5}
                ]
            },
            {
                "num_players": 12,
                "prizes": [
                    {"position": 1, "percentage": 50},
                    {"position": 2, "percentage": 30},
                    {"position": 3, "percentage": 20}
                ]
            }
        ]
    }

    # Structure pour Classique
    classic_payout = {
        "name": "Classique Standard Payouts",
        "starting_chips": 20000,
        "rebuy_levels": 4,
        "structure": [
            {
                "num_players": 8,
                "prizes": [
                    {"position": 1, "percentage": 60},
                    {"position": 2, "percentage": 40}
                ]
            },
            {
                "num_players": 10,
                "prizes": [
                    {"position": 1, "percentage": 50},
                    {"position": 2, "percentage": 30},
                    {"position": 3, "percentage": 20}
                ]
            }
        ]
    }

    # Créer les structures si elles n'existent pas
    for payout_data in [japt_payout, mtt_payout, classic_payout]:
        existing = db.query(PayoutStructure).filter(
            PayoutStructure.name == payout_data["name"]
        ).first()

        if not existing:
            db_payout = PayoutStructure(
                name=payout_data["name"],
                starting_chips=payout_data["starting_chips"],
                rebuy_levels=payout_data["rebuy_levels"],
                structure=payout_data["structure"]
            )
            db.add(db_payout)

    db.commit()


def create_default_sound_configuration(db: Session):
    """
    Crée la configuration sonore par défaut si elle n'existe pas
    """
    default_sounds = {
        "name": "Sons par défaut",
        "is_default": True,
        "sounds": {
            "level_start": "default_start.mp3",
            "level_warning": "default_warning.mp3",
            "break_start": "default_break.mp3",
            "break_end": "default_break_end.mp3"
        }
    }

    existing = db.query(SoundConfiguration).filter(
        SoundConfiguration.name == default_sounds["name"]
    ).first()

    if not existing:
        db_sound_config = SoundConfiguration(
            name=default_sounds["name"],
            is_default=default_sounds["is_default"],
            sounds=default_sounds["sounds"]
        )
        db.add(db_sound_config)
        db.commit()
        return db_sound_config

    return existing


def create_default_configurations(db: Session):
    """
    Crée les configurations par défaut pour tous les types de tournoi
    """
    # Créer les structures de base
    create_default_blinds_structures(db)
    create_default_payout_structures(db)
    sound_config = create_default_sound_configuration(db)

    # Récupérer les structures créées
    japt_blinds = db.query(BlindsStructure).filter(
        BlindsStructure.name == "JAPT Standard Blinds"
    ).first()

    mtt_blinds = db.query(BlindsStructure).filter(
        BlindsStructure.name == "MTT Standard Blinds"
    ).first()

    classic_blinds = db.query(BlindsStructure).filter(
        BlindsStructure.name == "Classique Standard Blinds"
    ).first()

    japt_payout = db.query(PayoutStructure).filter(
        PayoutStructure.name == "JAPT Standard Payouts"
    ).first()

    mtt_payout = db.query(PayoutStructure).filter(
        PayoutStructure.name == "MTT Standard Payouts"
    ).first()

    classic_payout = db.query(PayoutStructure).filter(
        PayoutStructure.name == "Classique Standard Payouts"
    ).first()

    # Configurations de tournoi
    tournament_configs = [
        {
            "name": "JAPT Standard",
            "tournament_type": "JAPT",
            "buy_in": 20.0,
            "is_default": True,
            "blinds_structure_id": japt_blinds.id if japt_blinds else None,
            "payout_structure_id": japt_payout.id if japt_payout else None,
            "sound_configuration_id": sound_config.id if sound_config else None
        },
        {
            "name": "MTT Standard",
            "tournament_type": "MTT",
            "buy_in": 30.0,
            "is_default": True,
            "blinds_structure_id": mtt_blinds.id if mtt_blinds else None,
            "payout_structure_id": mtt_payout.id if mtt_payout else None,
            "sound_configuration_id": sound_config.id if sound_config else None
        },
        {
            "name": "Classique Standard",
            "tournament_type": "CLASSIQUE",
            "buy_in": 25.0,
            "is_default": True,
            "blinds_structure_id": classic_blinds.id if classic_blinds else None,
            "payout_structure_id": classic_payout.id if classic_payout else None,
            "sound_configuration_id": sound_config.id if sound_config else None
        }
    ]

    # Créer les configurations si elles n'existent pas
    for config_data in tournament_configs:
        # Vérifier que tous les IDs nécessaires sont présents
        if None in [config_data["blinds_structure_id"], config_data["payout_structure_id"]]:
            continue

        existing = db.query(TournamentConfiguration).filter(
            TournamentConfiguration.name == config_data["name"]
        ).first()

        if not existing:
            db_config = TournamentConfiguration(**config_data)
            db.add(db_config)

    db.commit()