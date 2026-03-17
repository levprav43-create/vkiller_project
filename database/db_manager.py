from sqlalchemy.orm import Session
from database.models import *


def get_or_create_user(
        session: Session,
        vk_id: int,
        first_name: str,
        last_name: str,
        city: str,
        age: int,
        sex: int
) -> User:
    """
    Функция добавляет пользователя в БД в таблицу 'users',
        если же пользователь уже добавлен возвращает объект класса 'User'
    """
    availability = session.query(User).filter(User.vk_id == vk_id).first()

    if availability:
        return availability
    else:
        check = all(
            [
                isinstance(session, Session),
                isinstance(vk_id, int),
                isinstance(first_name, str),
                isinstance(last_name, str),
                isinstance(city, str),
                isinstance(age, int),
                isinstance(sex, int)
            ]
        )

        if not check:
            raise TypeError("Один из аргументов имеет не верный тип данных")

        for i in [first_name, last_name, city]:
            if not i:
                raise ValueError("Одно из строковых значений пустое")

        if not 1 < age < 140:
            raise ValueError("Возраст меньше 1 или больше 140")

        if sex not in [0, 1]:
            sex = 2

        new_user = User(
            vk_id=vk_id,
            first_name=first_name,
            last_name=last_name,
            city=city,
            age=age,
            sex=sex
        )
        session.add(new_user)
        session.commit()
        return new_user  # Всегда возвращаем объект


def add_candidate(
        session: Session,
        vk_id: int,
        first_name: str,
        last_name: str,
        city: str,
        age: int,
        sex: int,
        profile_url: str,
        photo_1: str,
        photo_2: str,
        photo_3: str
) -> bool:
    """Добавляет кандидата в БД"""
    check = all(
        [
            isinstance(session, Session),
            isinstance(vk_id, int),
            isinstance(first_name, str),
            isinstance(last_name, str),
            isinstance(city, str),
            isinstance(age, int),
            isinstance(sex, int),
            isinstance(profile_url, str),
            isinstance(photo_1, str),
            isinstance(photo_2, str),
            isinstance(photo_3, str)
        ]
    )

    if not check:
        raise TypeError("Один из аргументов имеет не верный тип данных")

    for i in [first_name, last_name, city, profile_url, photo_1, photo_2, photo_3]:
        if not i:
            raise ValueError("Одно из строковых значений пустое")

    if not 1 < age < 140:
        raise ValueError("Возраст меньше 1 или больше 140")

    if sex not in [0, 1]:
        sex = 2

    session.add(Candidate(
        vk_id=vk_id,
        first_name=first_name,
        last_name=last_name,
        city=city,
        age=age,
        sex=sex,
        profile_url=profile_url,
        photo_1=photo_1,
        photo_2=photo_2,
        photo_3=photo_3,
    ))
    session.commit()
    return True


def add_to_favorites(
        session: Session,
        user_id: int,
        candidate_id: int,
) -> bool:
    """Добавляет кандидата в избранное"""
    check = all([
        isinstance(session, Session),
        isinstance(user_id, int),
        isinstance(candidate_id, int),
    ])
    if not check:
        raise ValueError("Один из аргументов имеет не верный тип данных")

    session.add(Favorite(user_id=user_id, candidate_id=candidate_id))
    session.commit()
    return True


def add_to_blacklist(
        session: Session,
        user_id: int,
        candidate_id: int,
) -> bool:
    """Добавляет кандидата в чёрный список"""
    check = all([
        isinstance(session, Session),
        isinstance(user_id, int),
        isinstance(candidate_id, int),
    ])
    if not check:
        raise ValueError("Один из аргументов имеет не верный тип данных")

    session.add(Blacklist(user_id=user_id, candidate_id=candidate_id))
    session.commit()
    return True


def get_favorites(
        session: Session,
        user_vk_id: int
) -> list:
    """Ищет кандидатов в избранном у пользователя"""
    check = all([
        isinstance(session, Session),
        isinstance(user_vk_id, int)
    ])
    if not check:
        raise ValueError("Один из аргументов имеет не верный тип данных")

    # 🔥 Сначала найти пользователя по vk_id
    user = session.query(User).filter(User.vk_id == user_vk_id).first()
    if not user:
        return []
    
    # 🔥 Теперь использовать ВНУТРЕННИЙ user.id
    list_ids = session.query(Favorite.candidate_id).filter(Favorite.user_id == user.id).all()

    if list_ids:
        list_obj = []
        for id in [id[0] for id in list_ids]:
            candidate = session.query(Candidate).filter(Candidate.id == id).first()
            if candidate:  # Проверка на None
                list_obj.append(candidate)
        return list_obj
    else:
        return []


def get_blacklist_ids(
        session: Session,
        user_vk_id: int
) -> list:
    """Ищет vk_id кандидатов в чёрном списке"""
    check = all([
        isinstance(session, Session),
        isinstance(user_vk_id, int)
    ])
    if not check:
        raise ValueError("Один из аргументов имеет не верный тип данных")

    # Найти пользователя по vk_id
    user = session.query(User).filter(User.vk_id == user_vk_id).first()
    if not user:
        return []

    list_ids = session.query(Blacklist.candidate_id).filter(Blacklist.user_id == user.id).all()

    if list_ids:
        list_vk_ids = []
        for id in [id[0] for id in list_ids]:
            vk_id = session.query(Candidate.vk_id).filter(Candidate.id == id).first()
            if vk_id:
                list_vk_ids.append(vk_id[0])
        return list_vk_ids
    else:
        return []


def get_user_by_vk_id(session: Session, vk_id: int) -> User | None:
    """Находит пользователя по vk_id"""
    check = all([isinstance(session, Session), isinstance(vk_id, int)])
    if not check:
        raise ValueError("Один из аргументов имеет не верный тип данных")
    return session.query(User).filter(User.vk_id == vk_id).first()


def get_candidate_by_vk_id(session: Session, vk_id: int) -> Candidate | None:
    """Находит кандидата по vk_id"""
    check = all([isinstance(session, Session), isinstance(vk_id, int)])
    if not check:
        raise ValueError("Один из аргументов имеет не верный тип данных")
    return session.query(Candidate).filter(Candidate.vk_id == vk_id).first()


def filter_candidates(
    candidates: list[dict],
    blacklist_ids: list[int],
    favorites_ids: list[int]
) -> list[dict]:
    """
    Фильтрует кандидатов: убирает тех, кто в ЧС или избранном.
    ✅ Исправлено: без session, без багов с удалением
    """
    check = all([
        isinstance(candidates, list),
        isinstance(blacklist_ids, list),
        isinstance(favorites_ids, list)
    ])
    if not check:
        raise ValueError("Один из аргументов имеет не верный тип данных")

    exclude_ids = set(blacklist_ids + favorites_ids)
    # ✅ Безопасная фильтрация через list comprehension
    return [c for c in candidates if c['id'] not in exclude_ids]