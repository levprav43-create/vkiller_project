from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class User(Base):
    """Пользователь бота"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    vk_id = Column(Integer, unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    city = Column(String(100))
    age = Column(Integer)
    gender = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())


class Candidate(Base):
    """Кандидат для знакомства"""
    __tablename__ = 'candidates'
    
    id = Column(Integer, primary_key=True)
    vk_id = Column(Integer, unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    city = Column(String(100))
    age = Column(Integer)
    gender = Column(Integer)
    profile_url = Column(String(255), nullable=False)
    photo_1 = Column(String(255))
    photo_2 = Column(String(255))
    photo_3 = Column(String(255))


class Favorite(Base):
    """Избранное"""
    __tablename__ = 'favorites'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    candidate_id = Column(Integer, ForeignKey('candidates.id'))
    added_at = Column(DateTime, server_default=func.now())


class Blacklist(Base):
    """Чёрный список"""
    __tablename__ = 'blacklist'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    candidate_id = Column(Integer, ForeignKey('candidates.id'))
    added_at = Column(DateTime, server_default=func.now())