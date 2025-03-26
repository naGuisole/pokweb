# backend/app/models/configuration.py
from sqlalchemy import Column, Integer, String, JSON, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class BlindsStructure(Base):
    __tablename__ = "blinds_structures"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    structure = Column(JSON, nullable=False)  # [{level, small_blind, big_blind, duration}]
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    created_by = relationship("User", back_populates="blinds_structures")
    tournament_configurations = relationship("TournamentConfiguration", back_populates="blinds_structure")


class PayoutStructure(Base):
    __tablename__ = "payout_structures"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    starting_chips = Column(Integer, nullable=False)  # Déplacé ici depuis TournamentConfiguration
    rebuy_levels = Column(Integer, default=0)
    structure = Column(JSON, nullable=False)  # [{num_players, prizes: [{position, percentage}]}]
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    created_by = relationship("User", back_populates="payout_structures")
    tournament_configurations = relationship("TournamentConfiguration", back_populates="payout_structure")


class SoundConfiguration(Base):
    __tablename__ = "sound_configurations"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    is_default = Column(Boolean, default=False)
    sounds = Column(JSON, nullable=False)  # {event_type: sound_path}
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    created_by = relationship("User", back_populates="sound_configurations")
    tournament_configurations = relationship("TournamentConfiguration", back_populates="sound_configuration")


class TournamentConfiguration(Base):
    __tablename__ = "tournament_configurations"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    tournament_type = Column(String(20), nullable=False)  # JAPT, CLASSIQUE, MTT
    is_default = Column(Boolean, default=False)
    buy_in = Column(Float, nullable=False)

    # Relations vers les autres tables
    blinds_structure_id = Column(Integer, ForeignKey('blinds_structures.id'), nullable=False)
    payout_structure_id = Column(Integer, ForeignKey('payout_structures.id'), nullable=False)
    sound_configuration_id = Column(Integer, ForeignKey('sound_configurations.id'), nullable=True)

    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    blinds_structure = relationship("BlindsStructure", back_populates="tournament_configurations")
    payout_structure = relationship("PayoutStructure", back_populates="tournament_configurations")
    sound_configuration = relationship("SoundConfiguration", back_populates="tournament_configurations")
    created_by = relationship("User", back_populates="tournament_configurations")