# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# URL de connexion à la base de données MySQL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Création du moteur de base de données
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_pre_ping=True,  # Test de connexion avant utilisation
    pool_size=10,        # Nombre de connexions dans le pool
    max_overflow=20      # Connexions supplémentaires autorisées
)

# Création d'une session factory
SessionLocal = sessionmaker(
    autocommit=False,     # Pas de commit automatique
    autoflush=False,      # Pas de flush automatique
    bind=engine
)

# Base déclarative pour les modèles
Base = declarative_base()

def get_db():
    """
    Générateur de session de base de données.
    Permet de gérer proprement les connexions et les transactions.
    
    Utilisation typique dans les routes FastAPI :
    db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
