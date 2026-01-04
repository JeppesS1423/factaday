from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone

from .database import Base

class Fact(Base):
    __tablename__ = "facts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    category = Column(String, nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        unique=True,
        index=True
    )

class AppState(Base):
    __tablename__ = "app_state"
    
    key = Column(String, primary_key=True)
    value = Column(Integer, nullable=False)