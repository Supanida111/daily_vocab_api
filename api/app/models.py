# api/app/models.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Numeric,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(100), unique=True, nullable=False)
    definition = Column(Text)
    difficulty_level = Column(String(20), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    practice_sessions = relationship(
        "PracticeSession", back_populates="word", cascade="all, delete-orphan"
    )


class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    id = Column(Integer, primary_key=True, index=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    user_sentence = Column(Text, nullable=False)
    score = Column(Numeric(3, 1), nullable=False)
    feedback = Column(Text)
    corrected_sentence = Column(Text)
    practiced_at = Column(DateTime, server_default=func.now())

    word = relationship("Word", back_populates="practice_sessions")
