# backend/config.py
from pydantic import ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os

class Settings(BaseSettings):
    """
    Configuration globale de l'application Pokweb.
    Gère les paramètres sensibles et l'environnement.
    """
    # Configuration de la base de données
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+mysqlconnector://user:password@localhost/pokweb")

    # Configurations de sécurité
    SECRET_KEY: str = os.getenv("SECRET_KEY", "votre_clé_secrète_ici")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Configuration d'email
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_FROM: str = "noreply@pokweb.com"

    # Configurations de l'application
    APP_NAME: str = "pokweb"
    DEBUG: bool = False

    # Configuration des uploads
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 2 * 1024 * 1024  # 2MB en bytes

    class Config:
        """Configuration supplémentaire pour les variables d'environnement"""
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
model_config = ConfigDict(from_attributes=True)


