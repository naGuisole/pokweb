# backend/app/crud/user.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
import bcrypt
from typing import Optional
from pydantic import EmailStr
from pathlib import Path

from ..config import settings
from ..models.models import User, League
from ..schemas.schemas import UserCreate, UserUpdateProfile

def get_user_with_league(db: Session, user_id: int):
    # Une seule requête qui charge l'utilisateur ET sa ligue
    user = db.query(User).options(
        joinedload(User.league)
    ).filter(User.id == user_id).first()
    return user


def get_user_by_email(db: Session, email: EmailStr) -> Optional[User]:
    """
    Récupère un utilisateur par son email
    
    Args:
        db (Session): Session de base de données
        email (str): Email de l'utilisateur
    
    Returns:
        Optional[User]: Utilisateur trouvé ou None
    """
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Récupère un utilisateur par son nom d'utilisateur
    
    Args:
        db (Session): Session de base de données
        username (str): Nom d'utilisateur
    
    Returns:
        Optional[User]: Utilisateur trouvé ou None
    """
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate) -> User:
    """
    Crée un nouvel utilisateur
    
    Args:
        db (Session): Session de base de données
        user (UserCreate): Données du nouvel utilisateur
    
    Returns:
        User: Utilisateur créé
    """
    # Vérification préalable de l'existence de l'email ou du username
    existing_user = db.query(User).filter(
        or_(
            User.email == user.email, 
            User.username == user.username
        )
    ).first()
    
    if existing_user:
        raise ValueError("Email ou nom d'utilisateur déjà existant")

    # Vérification que l'utilisateur n'appartient pas déjà à une ligue
    if user.league_id:
        existing_league = db.query(League).filter(League.id == user.league_id).first()
        if not existing_league:
            raise ValueError("La ligue spécifiée n'existe pas")

    # Hashage du mot de passe
    hashed_password = bcrypt.hashpw(
        user.password.encode('utf-8'), 
        bcrypt.gensalt()
    ).decode('utf-8')
    
    # Création du nouvel utilisateur
    db_user = User(
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=hashed_password,
        address=user.address,
        profile_image_path=user.profile_image_path
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

def update_user_profile(
    db: Session, 
    user_id: int, 
    profile_data: UserUpdateProfile
) -> Optional[User]:
    """
    Met à jour le profil d'un utilisateur
    
    Args:
        db (Session): Session de base de données
        user_id (int): ID de l'utilisateur
        profile_data (UserUpdateProfile): Données de mise à jour
    
    Returns:
        Optional[User]: Utilisateur mis à jour ou None
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        return None
    
    # Mise à jour des champs non-None
    for field, value in profile_data.dict(exclude_unset=True).items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user

def authenticate_user(
    db: Session, 
    email: str, 
    password: str
) -> Optional[User]:
    """
    Authentifie un utilisateur
    
    Args:
        db (Session): Session de base de données
        email (str): Email de l'utilisateur
        password (str): Mot de passe en clair
    
    Returns:
        Optional[User]: Utilisateur authentifié ou None
    """
    user = get_user_by_email(db, email)
    
    if not user:
        return None
    
    # Vérification du mot de passe
    if not bcrypt.checkpw(
        password.encode('utf-8'), 
        user.hashed_password.encode('utf-8')
    ):
        return None
    
    return user

def list_users(
    db: Session, 
    skip: int = 0, 
    limit: int = 100
) -> list[User]:
    """
    Liste les utilisateurs
    
    Args:
        db (Session): Session de base de données
        skip (int): Nombre d'utilisateurs à ignorer
        limit (int): Nombre max d'utilisateurs à retourner
    
    Returns:
        list[User]: Liste des utilisateurs
    """
    return db.query(User).offset(skip).limit(limit).all()


# Fonction de mise à jour de l'image de profil
def update_profile_image(db: Session, user_id: int, image_path: str) -> Optional[User]:
    """
    Met à jour le chemin de l'image de profil d'un utilisateur
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    # Si une ancienne image existe, on pourrait la supprimer ici
    if user.profile_image_path:
        old_image_path = Path(settings.UPLOAD_DIR) / user.profile_image_path.lstrip('/')
        old_image_path.unlink(missing_ok=True)

    user.profile_image_path = image_path
    db.commit()
    db.refresh(user)
    return user