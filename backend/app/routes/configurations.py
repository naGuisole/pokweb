# backend/app/routes/configurations.py
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
from pathlib import Path
import logging

from ..database import get_db
from ..crud import configuration as config_crud
from ..schemas.schemas import (
    TournamentConfigCreate, TournamentConfigResponse,
    BlindsStructureCreate, BlindsStructureResponse,
    PayoutStructureCreate, PayoutStructureResponse,
    SoundConfigCreate, SoundConfigResponse
)
from ..models.models import TournamentType
from .auth import get_current_user
from ..models.models import User

router = APIRouter()
logger = logging.getLogger(__name__)

# Dossier pour les fichiers sonores
SOUND_UPLOAD_DIR = Path("uploads/sounds")
SOUND_UPLOAD_DIR.mkdir(parents=True, exist_ok=True, mode=0o755)


# ---------------------- Routes pour les structures de blindes ----------------------

@router.post("/blinds", response_model=BlindsStructureResponse)
async def create_blinds_structure(
        structure: BlindsStructureCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Crée une nouvelle structure de blindes
    """
    try:
        return config_crud.create_blinds_structure(db, structure, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/blinds", response_model=List[BlindsStructureResponse])
async def get_blinds_structures(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Récupère la liste des structures de blindes
    """
    return config_crud.list_blinds_structures(db, current_user.id)


@router.get("/blinds/{structure_id}", response_model=BlindsStructureResponse)
async def get_blinds_structure(
        structure_id: int,
        db: Session = Depends(get_db)
):
    """
    Récupère une structure de blindes par son ID
    """
    structure = config_crud.get_blinds_structure(db, structure_id)
    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Structure de blindes non trouvée"
        )
    return structure


@router.put("/blinds/{structure_id}", response_model=BlindsStructureResponse)
async def update_blinds_structure(
        structure_id: int,
        structure: BlindsStructureCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Met à jour une structure de blindes
    """
    db_structure = config_crud.get_blinds_structure(db, structure_id)
    if not db_structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Structure de blindes non trouvée"
        )

    if db_structure.created_by_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez modifier que vos propres structures"
        )

    try:
        return config_crud.update_blinds_structure(db, structure_id, structure)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/blinds/{structure_id}")
async def delete_blinds_structure(
        structure_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Supprime une structure de blindes
    """
    db_structure = config_crud.get_blinds_structure(db, structure_id)
    if not db_structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Structure de blindes non trouvée"
        )

    if db_structure.created_by_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez supprimer que vos propres structures"
        )

    result = config_crud.delete_blinds_structure(db, structure_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de supprimer la structure (elle est peut-être utilisée par des configurations)"
        )

    return {"status": "success", "message": "Structure de blindes supprimée"}


# ---------------------- Routes pour les structures de paiements ----------------------

@router.post("/payouts", response_model=PayoutStructureResponse)
async def create_payout_structure(
        structure: PayoutStructureCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Crée une nouvelle structure de paiements
    """
    try:
        return config_crud.create_payout_structure(db, structure, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/payouts", response_model=List[PayoutStructureResponse])
async def get_payout_structures(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Récupère la liste des structures de paiements
    """
    return config_crud.list_payout_structures(db, current_user.id)


@router.get("/payouts/{structure_id}", response_model=PayoutStructureResponse)
async def get_payout_structure(
        structure_id: int,
        db: Session = Depends(get_db)
):
    """
    Récupère une structure de paiements par son ID
    """
    structure = config_crud.get_payout_structure(db, structure_id)
    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Structure de paiements non trouvée"
        )
    return structure


@router.put("/payouts/{structure_id}", response_model=PayoutStructureResponse)
async def update_payout_structure(
        structure_id: int,
        structure: PayoutStructureCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Met à jour une structure de paiements
    """
    db_structure = config_crud.get_payout_structure(db, structure_id)
    if not db_structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Structure de paiements non trouvée"
        )

    if db_structure.created_by_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez modifier que vos propres structures"
        )

    try:
        return config_crud.update_payout_structure(db, structure_id, structure)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/payouts/{structure_id}")
async def delete_payout_structure(
        structure_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Supprime une structure de paiements
    """
    db_structure = config_crud.get_payout_structure(db, structure_id)
    if not db_structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Structure de paiements non trouvée"
        )

    if db_structure.created_by_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez supprimer que vos propres structures"
        )

    result = config_crud.delete_payout_structure(db, structure_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de supprimer la structure (elle est peut-être utilisée par des configurations)"
        )

    return {"status": "success", "message": "Structure de paiements supprimée"}


# ---------------------- Routes pour les configurations de tournoi ----------------------

@router.post("/tournament", response_model=TournamentConfigResponse)
async def create_tournament_config(
        config: TournamentConfigCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Crée une nouvelle configuration de tournoi
    """
    try:
        if config.is_default and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seuls les administrateurs peuvent créer des configurations par défaut"
            )
        return config_crud.create_tournament_configuration(db, config, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/tournament", response_model=List[TournamentConfigResponse])
async def get_tournament_configs(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Récupère la liste des configurations de tournoi
    """
    return config_crud.list_tournament_configurations(db, user_id=current_user.id)


@router.get("/tournament/{config_id}", response_model=TournamentConfigResponse)
async def get_tournament_config(
        config_id: int,
        db: Session = Depends(get_db)
):
    """
    Récupère une configuration de tournoi par son ID
    """
    config = config_crud.get_tournament_configuration(db, config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration de tournoi non trouvée"
        )
    return config


@router.put("/tournament/{config_id}", response_model=TournamentConfigResponse)
async def update_tournament_config(
        config_id: int,
        config: TournamentConfigCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Met à jour une configuration de tournoi
    """
    db_config = config_crud.get_tournament_configuration(db, config_id)
    if not db_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration de tournoi non trouvée"
        )

    if db_config.created_by_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez modifier que vos propres configurations"
        )

    try:
        return config_crud.update_tournament_configuration(db, config_id, config)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/tournament/{config_id}")
async def delete_tournament_config(
        config_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Supprime une configuration de tournoi
    """
    config = config_crud.get_tournament_configuration(db, config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration non trouvée"
        )

    if config.is_default:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Les configurations par défaut ne peuvent pas être supprimées"
        )

    if config.created_by_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez supprimer que vos propres configurations"
        )

    config_crud.delete_tournament_configuration(db, config_id)
    return {"status": "success", "message": "Configuration supprimée"}


# ---------------------- Routes pour les configurations sonores ----------------------

@router.post("/sound", response_model=SoundConfigResponse)
async def create_sound_config(
        name: str,
        files: List[UploadFile] = File(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Crée une nouvelle configuration sonore
    """
    sounds = {}

    # Vérification des fichiers
    for file in files:
        if not file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Le fichier {file.filename} n'est pas un fichier audio"
            )

    # Sauvegarde des fichiers
    for file in files:
        sound_path = SOUND_UPLOAD_DIR / f"{current_user.id}_{file.filename}"
        with sound_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        sounds[file.filename] = str(sound_path)

    config = SoundConfigCreate(
        name=name,
        sounds=sounds,
        is_default=False
    )

    try:
        return config_crud.create_sound_configuration(db, config, current_user.id)
    except ValueError as e:
        # En cas d'erreur, supprimer les fichiers uploadés
        for sound_path in sounds.values():
            os.remove(sound_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/sound", response_model=List[SoundConfigResponse])
async def get_sound_configs(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Récupère les configurations sonores de l'utilisateur
    """
    return config_crud.list_sound_configurations(db, user_id=current_user.id)


@router.get("/sound/{config_id}", response_model=SoundConfigResponse)
async def get_sound_config(
        config_id: int,
        db: Session = Depends(get_db)
):
    """
    Récupère une configuration sonore par son ID
    """
    config = config_crud.get_sound_configuration(db, config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration sonore non trouvée"
        )
    return config


@router.delete("/sound/{config_id}")
async def delete_sound_config(
        config_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Supprime une configuration sonore
    """
    config = config_crud.get_sound_configuration(db, config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration sonore non trouvée"
        )

    if config.is_default:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Les configurations par défaut ne peuvent pas être supprimées"
        )

    if config.created_by_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez supprimer que vos propres configurations"
        )

    # Suppression des fichiers sonores
    for sound_path in config.sounds.values():
        try:
            os.remove(sound_path)
        except OSError:
            pass

    config_crud.delete_sound_configuration(db, config_id)
    return {"status": "success", "message": "Configuration sonore supprimée"}


# ---------------------- Route pour l'initialisation des configurations par défaut ----------------------

@router.post("/initialize-defaults")
async def initialize_default_configurations(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Initialise les configurations par défaut (JAPT, MTT, Classique)
    Réservé aux administrateurs
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Opération réservée aux administrateurs"
        )

    config_crud.create_default_configurations(db)
    return {"status": "success", "message": "Configurations par défaut créées"}