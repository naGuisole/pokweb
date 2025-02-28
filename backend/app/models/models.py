# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum

class League(Base):
    __tablename__ = 'leagues'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500))

    # Admins de la ligue
    admins = relationship("User", secondary="league_admins", back_populates="administered_league")

    # Membres de la ligue
    members = relationship("User", back_populates="league")

    # Tournois de la ligue
    tournaments = relationship("Tournament", back_populates="league")

# Table d'association Admins-Ligues
class LeagueAdmin(Base):
   __tablename__ = 'league_admins'
   league_id = Column(Integer, ForeignKey('leagues.id'), primary_key=True)
   user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)


class TournamentType(enum.Enum):
    """
    Types de tournois possibles sur pokweb
    """
    CLASSIQUE = "CLASSIQUE"  # Une table, max 10 joueurs
    MTT = "MTT"  # Plusieurs tables
    JAPT = "JAPT"  # Une table, max 10 joueurs, avec jeton d'argile


class TournamentStatus(enum.Enum):
    """
    Statuts possibles pour un tournoi
    """
    PLANNED = "PLANNED"  # Créé mais pas encore commencé
    IN_PROGRESS = "IN_PROGRESS"  # Tournoi en cours
    COMPLETED = "COMPLETED"  # Tournoi terminé


class Tournament(Base):
    """
    Modèle représentant un tournoi/une partie de poker
    """
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    tournament_type = Column(Enum(TournamentType), nullable=False)
    status = Column(Enum(TournamentStatus), default=TournamentStatus.PLANNED)

    # Configuration du tournoi
    configuration_id = Column(Integer, ForeignKey('tournament_configurations.id'))
    configuration = relationship("TournamentConfiguration")
    sound_configuration_id = Column(Integer, ForeignKey('sound_configurations.id'))
    sound_configuration = relationship("SoundConfiguration")

    # Informations temporelles
    date = Column(DateTime(timezone=True), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=True)  # Heure réelle de début
    end_time = Column(DateTime(timezone=True), nullable=True)  # Heure de fin
    current_level = Column(Integer, default=0)  # Niveau actuel des blindes
    seconds_remaining = Column(Integer, nullable=True)  # Temps restant dans le niveau actuel
    level_duration = Column(Integer, nullable=True)  # Durée totale du niveau en secondes
    paused_at = Column(DateTime(timezone=True), nullable=True)  # Horodatage de la dernière mise en pause
    last_timer_update = Column(DateTime(timezone=True), nullable=True)  # Dernier moment où le timer a été mis à jour

    # Paramètres du tournoi
    max_players = Column(Integer, nullable=False)
    buy_in = Column(Float, nullable=False)
    num_tables = Column(Integer, default=1)
    players_per_table = Column(Integer, default=10)

    # Gestion financière
    total_buyin = Column(Float, default=0)  # Buy-in total (incluant les rebuys)
    total_rebuys = Column(Integer, default=0)  # Nombre total de rebuys
    prize_pool = Column(Float, default=0)  # Cagnotte totale à distribuer

    # Gestion du Jeton d'Argile
    clay_token_holder_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    bounty_hunter_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Tables et positions (stocké en JSON pour plus de flexibilité)
    tables_state = Column(JSON, default={})  # Structure: {table_id: {position: player_id, ...}, ...}

    # Administrateur du tournoi
    admin_id = Column(Integer, ForeignKey('users.id'))

    # Relations
    league_id = Column(Integer, ForeignKey('leagues.id'), nullable=False)

    league = relationship("League", back_populates="tournaments")
    admin = relationship("User", foreign_keys=[admin_id])
    participations = relationship("TournamentParticipation", back_populates="tournament")
    clay_token_holder = relationship("User", foreign_keys=[clay_token_holder_id])
    bounty_hunter = relationship("User", foreign_keys=[bounty_hunter_id])


class TournamentParticipation(Base):
    """
    Participation d'un joueur à un tournoi
    Stocke toutes les informations sur l'état d'un joueur dans le tournoi
    """
    __tablename__ = "tournament_participations"

    id = Column(Integer, primary_key=True, index=True)

    tournament_id = Column(Integer, ForeignKey('tournaments.id'))
    tournament = relationship("Tournament", back_populates="participations")

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User")

    # État de la participation
    is_registered = Column(Boolean, default=True)  # Pour la phase d'inscription
    is_active = Column(Boolean, default=True)  # Pour suivre si le joueur est encore en jeu
    registration_time = Column(DateTime(timezone=True), server_default=func.now())
    elimination_time = Column(DateTime(timezone=True), nullable=True)
    current_position = Column(Integer, nullable=True)  # Position finale ou actuelle

    # Gestion des jetons et de l'argent
    num_rebuys = Column(Integer, default=0)  # Nombre de rebuys effectués
    total_buyin = Column(Float, default=0)  # Buy-in total (initial + rebuys)
    prize_won = Column(Float, default=0)  # Gains éventuels

    # Historique des actions (stocké en JSON pour la flexibilité)
    action_history = Column(JSON, default=[])  # Liste des actions (rebuys, éliminations, etc.)


class User(Base):
    """
    Modèle représentant un utilisateur dans l'application Pokweb
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    address = Column(String(255), nullable=True)
    profile_image_path = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relations

    # Relation Ligue
    league_id = Column(Integer, ForeignKey('leagues.id'))
    league = relationship("League", foreign_keys=[league_id])
    administered_league = relationship("League", secondary="league_admins", back_populates="admins", uselist=False)

    # Relations Tournoi
    tournaments_as_admin = relationship("Tournament", back_populates="admin", foreign_keys="[Tournament.admin_id]")
    tournament_participations = relationship("TournamentParticipation", back_populates="user")

    # Relations configs
    tournament_configurations = relationship("TournamentConfiguration", back_populates="created_by")
    sound_configurations = relationship("SoundConfiguration", back_populates="created_by")

    blog_posts = relationship("BlogPost", back_populates="author")