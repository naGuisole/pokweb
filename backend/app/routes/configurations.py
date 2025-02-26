# backend/app/routes/configurations.py
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
from pathlib import Path
import json
import logging
from pydantic import ValidationError


from ..database import get_db
from ..crud import configuration as config_crud
from ..models.configuration import TournamentConfiguration
from ..schemas.schemas import (
    TournamentConfigCreate,
    SoundConfigCreate,
    TournamentConfigResponse
)
from ..models.models import TournamentType
from .auth import get_current_user
from ..models.models import User

router = APIRouter()

logger = logging.getLogger(__name__)


# Dossier pour les fichiers sonores
SOUND_UPLOAD_DIR = Path("uploads/sounds")
SOUND_UPLOAD_DIR.mkdir(parents=True, exist_ok=True, mode=0o755)

@router.post("/tournament", response_model=TournamentConfigResponse)
async def create_tournament_config(
    config: TournamentConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crée une nouvelle configuration de tournoi
    Seuls les utilisateurs connectés peuvent créer des configurations
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

@router.get("/tournament/defaults", response_model=List[TournamentConfigResponse])
async def get_default_tournament_configs(
    tournament_type: Optional[TournamentType] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les configurations de tournoi par défaut
    Optionnellement filtrées par type de tournoi
    """
    return config_crud.list_tournament_configurations(
        db,
        tournament_type=tournament_type,
        include_default=True,
        user_id=None
    )


@router.get("/tournament", response_model=List[TournamentConfigResponse])
async def get_tournament_configs(db: Session = Depends(get_db)):
    try:
        configs = db.query(TournamentConfiguration).all()

        # Conversion explicite en dictionnaire
        config_list = []
        for config in configs:
            config_dict = {
                "id": config.id,
                "name": config.name,
                "tournament_type": config.tournament_type,
                "is_default": config.is_default,
                "starting_chips": config.starting_chips,
                "buy_in": float(config.buy_in),
                "blinds_structure": config.blinds_structure,  # Déjà un dict/list grâce à SQLAlchemy et JSON
                "rebuy_levels": config.rebuy_levels,
                "payouts_structure": config.payouts_structure,  # Déjà un dict/list grâce à SQLAlchemy et JSON
                "created_by_id": config.created_by_id,
                "created_at": config.created_at
            }
            config_list.append(config_dict)

        return config_list

    except Exception as e:
        print(f"Error: {str(e)}")
        print("Type:", type(e))
        print("Args:", e.args)
        raise HTTPException(
            status_code=500,
            detail=f"Error getting tournament configurations: {str(e)}"
        )

@router.get("/tournament/{config_id}", response_model=TournamentConfigResponse)
async def get_tournament_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère une configuration de tournoi spécifique
    """
    config = config_crud.get_tournament_configuration(db, config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration non trouvée"
        )
    return config

@router.delete("/tournament/{config_id}")
async def delete_tournament_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Supprime une configuration de tournoi
    Seul le créateur peut supprimer sa configuration
    Les configurations par défaut ne peuvent pas être supprimées
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

@router.post("/initialize-defaults")
async def initialize_default_configurations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Initialise les configurations par défaut (JAPT et MTT)
    Réservé aux administrateurs
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Opération réservée aux administrateurs"
        )
    
    config_crud.create_default_configurations(db)
    return {"status": "success", "message": "Configurations par défaut créées"}

@router.post("/sound", response_model=SoundConfigCreate)
async def create_sound_config(
    name: str,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crée une nouvelle configuration sonore
    Vérifie que les fichiers sont bien des fichiers audio
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

@router.get("/sound/{config_id}")
async def get_sound_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupère une configuration sonore spécifique
    """
    config = config_crud.get_sound_configuration(db, config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration sonore non trouvée"
        )
    return config

@router.get("/sound")
async def get_user_sound_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les configurations sonores de l'utilisateur
    Et les configurations par défaut
    """
    return config_crud.list_sound_configurations(
        db,
        include_default=True,
        user_id=current_user.id
    )

@router.delete("/sound/{config_id}")
async def delete_sound_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Supprime une configuration sonore
    Supprime aussi les fichiers associés
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
