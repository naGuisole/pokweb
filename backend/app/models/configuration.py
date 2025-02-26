from sqlalchemy import Column, Integer, String, JSON, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class TournamentConfiguration(Base):
    __tablename__ = "tournament_configurations"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    tournament_type = Column(String(20), nullable=False)  # JAPT, CLASSIQUE, MTT
    is_default = Column(Boolean, default=False)
    starting_chips = Column(Integer, nullable=False)
    buy_in = Column(Float, nullable=False)
    blinds_structure = Column(JSON, nullable=False)  # [{level, small_blind, big_blind, duration}]
    rebuy_levels = Column(Integer, default=0)
    payouts_structure = Column(JSON, nullable=False)  # [{num_players, prizes: [{position, percentage}]}]
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    created_by = relationship("User", back_populates="tournament_configurations")

class SoundConfiguration(Base):
    __tablename__ = "sound_configurations"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    is_default = Column(Boolean, default=False)
    sounds = Column(JSON, nullable=False)  # {event_type: sound_path}
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    created_by = relationship("User", back_populates="sound_configurations")