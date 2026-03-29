from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    
    # 🔧 ИСПРАВЛЕНИЕ: убрали явный Sequence, пусть PostgreSQL сам создаст users_id_seq
    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_id = Column(Integer, unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    city = Column(String(100))
    age = Column(Integer)
    sex = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    candidates = relationship('Candidate', back_populates='user', cascade='all, delete-orphan')
    favorites = relationship('Favorite', back_populates='user', cascade='all, delete-orphan')
    blacklists = relationship('Blacklist', back_populates='user', cascade='all, delete-orphan')


class Candidate(Base):
    __tablename__ = 'candidates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    vk_id = Column(Integer, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    age = Column(Integer)
    city = Column(String(100))
    photo_1 = Column(String(255))
    photo_2 = Column(String(255))
    photo_3 = Column(String(255))
    profile_url = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', back_populates='candidates')


class Favorite(Base):
    __tablename__ = 'favorites'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    candidate_vk_id = Column(Integer, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', back_populates='favorites')


class Blacklist(Base):
    __tablename__ = 'blacklists'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    candidate_vk_id = Column(Integer, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', back_populates='blacklists')