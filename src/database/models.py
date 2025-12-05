"""
SQLAlchemy database models for Neon DB.
"""
from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """User model for Neon DB."""
    __tablename__ = "users"

    username = Column(String(50), primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=True)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    software_background = Column(Text, nullable=True)
    hardware_background = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

