from sqlalchemy.orm import Session
from database.models import User, Candidate, Favorite, Blacklist



def get_or_create_user(db_session: Session, vk_id: int, first_name: str, last_name: str, city: str, age: int, sex: int):
    """Получить или создать пользователя"""
    user = db_session.query(User).filter(User.vk_id == vk_id).first()
    
    if not user:
        user = User(
            vk_id=vk_id,
            first_name=first_name,
            last_name=last_name,
            city=city,
            age=age,
            sex=sex
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    
    return user


def add_candidate(db_session: Session, user_id: int, candidate_data: dict):
    """Добавить кандидата"""
    candidate = Candidate(
        user_id=user_id,
        vk_id=candidate_data.get('vk_id'),
        first_name=candidate_data.get('first_name'),
        last_name=candidate_data.get('last_name'),
        age=candidate_data.get('age'),
        city=candidate_data.get('city'),
        photo_1=candidate_data.get('photo_1'),
        photo_2=candidate_data.get('photo_2'),
        photo_3=candidate_data.get('photo_3'),
        profile_url=candidate_data.get('profile_url')
    )
    db_session.add(candidate)
    db_session.commit()
    return candidate


def add_to_favorites(db_session: Session, user_id: int, candidate_vk_id: int):
    """Добавить в избранное"""
    favorite = Favorite(
        user_id=user_id,
        candidate_vk_id=candidate_vk_id
    )
    db_session.add(favorite)
    db_session.commit()
    return favorite


def add_to_blacklist(db_session: Session, user_id: int, candidate_vk_id: int):
    """Добавить в чёрный список"""
    # 🔧 ИСПРАВЛЕНИЕ: candidate_vk_id вместо user_vk_id
    blacklist = Blacklist(
        user_id=user_id,
        candidate_vk_id=candidate_vk_id
    )
    db_session.add(blacklist)
    db_session.commit()
    return blacklist


def get_favorites(db_session: Session, user_id: int):
    """Получить список избранного"""
    return db_session.query(Favorite).filter(Favorite.user_id == user_id).all()


def get_blacklist_ids(db_session: Session, user_id: int):
    """Получить ID чёрного списка"""
    # 🔧 ИСПРАВЛЕНИЕ: candidate_vk_id вместо user_vk_id
    blacklists = db_session.query(Blacklist).filter(Blacklist.user_id == user_id).all()
    return [b.candidate_vk_id for b in blacklists]


def filter_candidates(candidates: list, blacklist_ids: list, favorites_ids: list):
    """Отфильтровать кандидатов"""
    filtered = []
    for c in candidates:
        vk_id = c.get('id')
        if vk_id and vk_id not in blacklist_ids and vk_id not in favorites_ids:
            filtered.append(c)
    return filtered