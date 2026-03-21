from sqlalchemy.orm import Session
from database.models import User, Candidate, Favorite, Blacklist



def get_or_create_user(
        db_session: Session,
        vk_id: int,
        first_name: str,
        last_name: str,
        city: str,
        age: int,
        sex: int
) -> User:
    """
    Добавляет пользователя в БД в таблицу 'users'

    Когда пользователь уже имеется в БД возвращает объект класса 'User'

    Аргументы:
        db_session (Session): Активная сессия sqlalchemy
        vk_id (int): ID пользователя из VK;
        first_name (str): Имя пользователя;
        last_name (str): Фамилия пользователя;
        city (str): Город пользователя;
        sex (int): Род пользователя

    Возвращает:
        User: Новый или имеющийся объект класса 'User'
    """
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


def add_candidate(
        db_session: Session,
        user_id: int,
        candidate_data: dict
) -> Candidate:
    """
    Добавляет кандидата для знакомства в БД в таблицу 'candidates'

    Аргументы:
        db_session (Session): Активная сессия sqlalchemy;
        user_id (int): ID пользователя;
        candidate_data (dict): Словарь с данными о кандидате

    Возвращает:
        Candidate: объект класса 'Candidate'
    """
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


def add_to_favorites(
        db_session: Session,
        user_id: int,
        candidate_vk_id: int
) -> Favorite:
    """
    Добавляет выбранного кандидата в избранное для пользователя
        сохраняя его в БД в таблице 'favorites'

    Аргументы:
        db_session (Session): Активная сессия sqlalchemy;
        user_id (int): ID пользователя из таблицы 'users' для которого
                выбранный человек добавляется в избранные;
        candidate_vk_id (int): VK ID понравившегося кандидата

    Возвращает:
        Favorite: объект класса 'Favorite'
    """
    favorite = Favorite(
        user_id=user_id,
        candidate_vk_id=candidate_vk_id
    )
    db_session.add(favorite)
    db_session.commit()
    return favorite


def add_to_blacklist(
        db_session: Session,
        user_id: int,
        candidate_vk_id: int
) -> Blacklist:
    """
    Добавляет выбранного кандидата в чёрный список для пользователя
        сохраняя его в БД в таблице 'blacklist'

    Аргументы:
        db_session (Session): Активная сессия sqlalchemy;
        user_id (int): ID пользователя из таблицы 'users' для которого
                выбранный человек добавляется в черный список;
        candidate_vk_id (int): VK ID понравившегося кандидата

    Возвращает:
        Blacklist: объект класса 'Blacklist'
    """
    blacklist = Blacklist(
        user_id=user_id,
        candidate_vk_id=candidate_vk_id
    )
    db_session.add(blacklist)
    db_session.commit()
    return blacklist


def get_favorites(db_session: Session, user_id: int) -> list:
    """
    Ищет кандидатов, которые добавлены в избранное

    Аргументы:
        db_session (Session): Активная сессия sqlalchemy;
        user_id (int): ID пользователя из таблицы 'users' для которого идет поиск

    Возвращает:
        list[Candidate]: Список объектов класса 'Candidate', которые есть в избранном у пользователя;
        []: Пустой список, если ничего не найдено
    """
    return db_session.query(Favorite).filter(Favorite.user_id == user_id).all()


def get_blacklist_ids(db_session: Session, user_id: int) -> list:
    """
    Ищет 'vk_id' кандидатов, которые помещены в черный список

    Аргументы:
        db_session (Session): Активная сессия sqlalchemy;
        user_id (int): ID пользователя из таблицы 'users' для которого идет поиск

    Возвращает:
        list[int]: Список 'candidate_vk_id' кандидатов, которые добавлены в черный список у пользователя;
        []: Пустой список, если ни кто не добавлен
    """
    blacklists = db_session.query(Blacklist).filter(Blacklist.user_id == user_id).all()
    return [b.candidate_vk_id for b in blacklists]


def filter_candidates(
        candidates: list[dict],
        blacklist_ids: list[int],
        favorites_ids: list[int]
) -> list[dict]:
    """
    Фильтрует список поступивших кандидатов, убирает тех кто есть в ЧС или в избранном

    Аргументы:
        candidates (list[dict]): Список кандидатов от VK API;
        blacklist_ids (list[int]): список VK ID пользователей находящихся в черном списке;
        favorites_ids (list[int]): список VK ID избранных пользователей

    Возвращает:
        list[dict]: Отфильтрованный список кандидатов.
    """
    filtered = []
    for c in candidates:
        vk_id = c.get('id')
        if vk_id and vk_id not in blacklist_ids and vk_id not in favorites_ids:
            filtered.append(c)
    return filtered