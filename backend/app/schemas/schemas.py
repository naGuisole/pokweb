# backend/app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, validator, field_validator
from typing import Optional, Dict, List
from datetime import datetime

from ..models.models import TournamentType, TournamentStatus


# User schemas
class UserBase(BaseModel):
    """
    Modèle de base pour les utilisateurs
    """
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    address: Optional[str] = None
    profile_image_path: Optional[str] = None
    league_id: Optional[int] = None


    @field_validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Le nom d\'utilisateur ne peut contenir que des lettres, chiffres, tirets et underscores')
        return v


class UserSimple(UserBase):
    id: int

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    """
    Modèle pour la création d'un utilisateur
    """
    password: str = Field(..., min_length=8)
    league: Optional['dict'] = None


    @field_validator('password')
    def validate_password(cls, password):
        """
        Validation du mot de passe
        - Au moins 8 caractères
        - Au moins un chiffre
        - Au moins une majuscule
        - Au moins un caractère spécial
        """
        import re
        if len(password) < 8:
            raise ValueError('Mot de passe trop court')
        if not re.search(r'\d', password):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        if not re.search(r'[A-Z]', password):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError('Le mot de passe doit contenir au moins un caractère spécial')
        return password

class LeagueBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None


class LeagueSimple(LeagueBase):
    #member_count: int
    #admin_count: int

    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: int
    created_at: datetime
    last_login: Optional[datetime]
    is_league_admin: bool = False
    league: Optional[LeagueSimple] = None  # Version simplifiée de la ligue

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """
    Modèle pour la connexion utilisateur
    """
    email: EmailStr
    password: str

class UserUpdateProfile(BaseModel):
    """
    Modèle pour la mise à jour du profil utilisateur
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    address: Optional[str] = None
    profile_image_path: Optional[str] = None
    league_id: Optional[int] = None


class BountyHunterResponse(BaseModel):
    id: int
    username: str
    profile_image_path: Optional[str]
    bounty_count: int
    bounty_earnings: float

    class Config:
        from_attributes = True


class ClayTokenHistoryResponse(BaseModel):
    tournament_id: int
    holder_id: int
    holder_username: str
    holder_profile_image: Optional[str]
    date: datetime
    tournament_name: str

    class Config:
        from_attributes = True



# Tournaments schemas :
class TablePosition(BaseModel):
    """
    Position d'un joueur à une table
    """
    player_id: int
    position: int


class TableState(BaseModel):
    """
    État d'une table
    """
    positions: Dict[int, int]  # position -> player_id


class TournamentBase(BaseModel):
    """
    Informations de base d'un tournoi
    """
    name: str = Field(..., min_length=3, max_length=100)
    tournament_type: TournamentType
    date: datetime
    max_players: int = Field(..., ge=2, le=100)
    buy_in: float = Field(..., gt=0)
    num_tables: Optional[int] = Field(1, ge=1)
    players_per_table: Optional[int] = Field(10, ge=2, le=10)

    # @field_validator('num_tables')
    # def validate_tables(cls, v, values):
    #     print("validate_tables " + str(v))
    #
    #     if 'tournament_type' in values:
    #         if values['tournament_type'] in [TournamentType.CLASSIQUE, TournamentType.JAPT]:
    #             if v != 1:
    #                 raise ValueError("Les tournois Classique et JAPT doivent avoir une seule table")
    #     print("validate_tables : OK")
    #
    #     return v

    @field_validator('players_per_table')
    def validate_players_per_table(cls, v, values):
        if v > 10:
          raise ValueError("Maximum 10 joueurs par table")
        return v

    @field_validator('tournament_type')
    def validate_tournament_type(cls, v):
        if isinstance(v, str):
            try:
                return TournamentType(v)
            except ValueError:
                raise ValueError("Type de tournoi invalide")

        return v

    # @field_validator('date')
    # def parse_date(cls, v):
    #     print("parse_date " + str(v))
    #
    #     if isinstance(v, str):
    #         try:
    #             print("parse_date : OK")
    #             return datetime.fromisoformat(v.replace("Z", "+00:00"))
    #         except ValueError:
    #             raise ValueError("Format de date invalide")
    #
    #     return v

class TournamentCreate(TournamentBase):
    """
    Données pour la création d'un tournoi
    """
    configuration_id: int
    sound_configuration_id: int
    league_id: int

    class Config:
        from_attributes = True
        use_enum_values = True # pour permettre la conversion string -> enum


class TournamentUpdate(BaseModel):
    """
    Données pour la mise à jour d'un tournoi
    """
    name: Optional[str] = None
    date: Optional[datetime] = None
    max_players: Optional[int] = None
    status: Optional[TournamentStatus] = None
    current_level: Optional[int] = None


class ParticipationBase(BaseModel):
    """
    Informations de base sur la participation d'un joueur
    """
    tournament_id: int
    user_id: int


class ParticipationCreate(ParticipationBase):
    """
    Données pour l'inscription d'un joueur
    """
    tournament_id: int
    user_id: int


class ParticipationUpdate(BaseModel):
    """
    Mise à jour de la participation d'un joueur
    """
    is_active: Optional[bool] = None
    elimination_time: Optional[datetime] = None
    current_position: Optional[int] = None
    prize_won: Optional[float] = None
    num_rebuys: int = 0
    total_buyin: float


class ParticipationResponse(ParticipationBase):
    id: int
    is_registered: bool
    is_active: bool
    registration_time: datetime
    elimination_time: Optional[datetime]
    current_position: Optional[int]
    num_rebuys: int
    total_buyin: float
    prize_won: float
    league_id: Optional[int] = None
    user: UserSimple


    class Config:
        from_attributes = True


class TournamentResponse(TournamentBase):
    """
    Réponse complète pour un tournoi
    """
    id: int
    status: TournamentStatus
    league_id: int
    admin_id: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    current_level: Optional[int]
    total_rebuys: Optional[int]
    prize_pool: Optional[float]
    clay_token_holder_id: Optional[int]
    bounty_hunter_id: Optional[int]
    tables_state: Dict[str, Dict[str, int]]  # Structure des tables
    participations: List[ParticipationResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class TournamentStateUpdate(BaseModel):
    """
    Mise à jour de l'état d'un tournoi en cours
    """
    current_level: Optional[int] = None
    tables_state: Optional[Dict[str, Dict[str, int]]] = None
    paused_at: Optional[datetime] = None


class RebuyRequest(BaseModel):
    """
    Demande de rebuy pour un joueur
    """
    player_id: int
    amount: float


# Schémas pour BlindLevel
class BlindLevel(BaseModel):
    """
    Structure d'un niveau de blindes
    """
    level: int
    small_blind: int
    big_blind: int
    duration: int  # en minutes

    @field_validator('big_blind')
    def validate_big_blind(cls, v, values):
        if 'small_blind' in values.data and v < values.data['small_blind']:
            raise ValueError("La grosse blinde doit supérieure à la petite blinde")
        return v

# Schémas pour BlindsStructure
class BlindsStructureBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    structure: List[Dict]  # [{level, small_blind, big_blind, duration}]
    starting_chips: int = Field(..., gt=0)
    is_default: bool = False

    @field_validator('structure')
    def validate_structure(cls, v):
        """Valide la structure des blindes"""
        if not v:
            raise ValueError("La structure des blindes ne peut pas être vide")

        for level in v:
            if level["big_blind"] < level["small_blind"]:
                raise ValueError(f"La grosse blinde doit être supérieure à la petite blinde au niveau {level['level']}")
            if level["duration"] <= 0:
                raise ValueError(f"La durée doit être positive au niveau {level['level']}")

        # Vérifier que les niveaux sont ordonnés
        for i in range(1, len(v)):
            if v[i]["level"] <= v[i - 1]["level"]:
                raise ValueError("Les niveaux doivent être strictement croissants")
            if v[i]["small_blind"] <= v[i - 1]["small_blind"] and v[i]["big_blind"] <= v[i - 1]["big_blind"]:
                raise ValueError("Les blindes doivent augmenter à chaque niveau")

        return v

class BlindsStructureCreate(BlindsStructureBase):
    pass

class BlindsStructureResponse(BlindsStructureBase):
    id: int
    created_by_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class PayoutPrize(BaseModel):
    """
    Structure d'un prix dans la table des paiements
    """
    position: int
    percentage: float


class PayoutEntry(BaseModel):
    """
    Structure de paiement pour un nombre de joueurs donné
    """
    num_players: int
    prizes: List[Dict]  # [{position, percentage}]



class SoundConfigBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    sounds: Dict[str, str]
    is_default: bool = False

    @field_validator('sounds')
    def validate_sounds(cls, v):
        required_sounds = {'level_start', 'level_warning', 'break_start', 'break_end'}
        if not all(key in v for key in required_sounds):
            raise ValueError(f"Sons requis manquants. Requis: {required_sounds}")
        return v

class SoundConfigCreate(SoundConfigBase):
    pass

class SoundConfigResponse(SoundConfigBase):
    id: int
    created_by_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class TournamentConfigBase(BaseModel):
    """
    Informations de base d'une configuration de tournoi
    """
    name: str = Field(..., min_length=3, max_length=100)
    tournament_type: str = Field(..., pattern='^(JAPT|CLASSIQUE|MTT)$')
    buy_in: float = Field(..., gt=0)
    is_default: bool = False
    rebuy_levels: int = Field(0, ge=0)  # Ajouté ici depuis PayoutStructure

class TournamentConfigCreate(TournamentConfigBase):
    """
    Données pour la création d'une configuration de tournoi
    """
    blinds_structure_id: int
    sound_configuration_id: Optional[int] = None

class TournamentConfigResponse(TournamentConfigBase):
    """
    Réponse complète pour une configuration de tournoi
    """
    id: int
    blinds_structure: BlindsStructureResponse
    sound_configuration: Optional[SoundConfigResponse]
    created_by_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True





# League schemas


class LeagueCreate(LeagueBase):
    pass

class LeagueResponse(LeagueBase):
    id: int
    members: List[UserResponse]
    admins: List[int] = Field(default_factory=list)


    class Config:
        from_attributes = True


class LeagueAdminCreate(BaseModel):
    user_id: int
    league_id: int


class LeagueAdminResponse(BaseModel):
    user_id: int
    league_id: int
    user: UserResponse

    class Config:
        from_attributes = True