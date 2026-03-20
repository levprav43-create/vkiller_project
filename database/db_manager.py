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
    Добавляет пользователя в БД в таблицу 'users',
        если же пользователь уже добавлен возвращает объект класса 'User'
    Аргументы:
        - session > активная сессия для взаимодействия
            созданная от Session(engine);
        - vk_id > ID пользователя из VK;
        - first_name > имя пользователя;
        - last_name > фамилия пользователя;
        - city > город пользователя;
        - sex > род пользователя (число)
            0 = Женский
            1 = Мужской
            прочее приведется к 2 = не указан;
    Возвращает:
        - Новый или имеющийся объект класса 'User
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
        return new_user


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
    """
    Добавляет кандидата для знакомства в БД в таблицу 'candidates'
    Аргументы:
        - session > активная сессия для взаимодействия
            созданная от Session(engine);
        - vk_id > ID кандидата из VK;
        - first_name > имя кандидата;
        - last_name > фамилия кандидата;
        - city > город кандидата;
        - sex > род кандидата (число)
            0 = Женский
            1 = Мужской
            прочее приведется к 2 - не указан;
        - profile_url > ссылка на профиль в VK;
        - photo_1 > ссылка №1 на популярное фото в VK
        - photo_2 > ссылка №2 на популярное фото в VK
        - photo_3 > ссылка №3 на популярное фото в VK
    Возвращает:
        При корректном завершении True
    """
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
        user_vk_id: int,
        candidate_vk_id: int,
) -> bool:
    """
    Добавляет выбранного кандидата в избранное для пользователя
        сохраняя его в БД в таблице 'favorites'
    Аргументы:
        - session > активная сессия для взаимодействия
                созданная от Session(engine);
        - user_vk_id > VK ID пользователя из таблицы 'users' для которого
                выбранный человек добавляется в избранные;
        - candidate_vk_id > VK ID понравившегося кандидата
    Возвращает:
        True при успешном выполнении кода
    """
    check = all([
        isinstance(session, Session),
        isinstance(user_vk_id, int),
        isinstance(candidate_vk_id, int),
    ])

    if not check:
        raise ValueError("Один из аргументов имеет не верный тип данных")

    session.add(Favorite(user_vk_id=user_vk_id, candidate_vk_id=candidate_vk_id))
    session.commit()
    return True


def add_to_blacklist(
        session: Session,
        user_vk_id: int,
        candidate_vk_id: int,
) -> bool:
    """
    Добавляет выбранного кандидата в чёрный список для пользователя
        сохраняя его в БД в таблице 'blacklist'
    Аргументы:
        - session > активная сессия для взаимодействия
                созданная от Session(engine);
        - user_vk_id > VK ID пользователя из таблицы 'users' для которого
                выбранный человек добавляется в черный список;
        - candidate_vk_id > VK ID кандидата добавляемого в черный список
    Возвращает:
        True при успешном исполнении кода
    """
    check = all([
        isinstance(session, Session),
        isinstance(user_vk_id, int),
        isinstance(candidate_vk_id, int),
    ])

    if not check:
        raise ValueError("Один из аргументов имеет не верный тип данных")

    session.add(Blacklist(user_vk_id=user_vk_id, candidate_vk_id=candidate_vk_id))
    session.commit()
    return True


def get_favorites(session: Session, user_vk_id: int) -> list:
    """
    Ищет кандидатов, которые добавлены в избранное
    Аргументы:
        - session > активная сессия для взаимодействия
            созданная от Session(engine);
        - user_vk_id > ID пользователя из таблицы 'users' для которого идет поиск;
    Возвращает:
        - список объектов класса 'Candidate', которые есть в избранном у пользователя;
        - [] пустой список, если ничего не найдено
    """
    check = all([
        isinstance(session, Session),
        isinstance(user_vk_id, int)
    ])

    if not check:
        raise ValueError("Один из аргументов имеет не верный тип данных")

    list_ids = session.query(Favorite.candidate_vk_id).filter(Favorite.user_vk_id == user_vk_id).all()

    if list_ids:
        list_obj = []
        for vk_id in [vk_id[0] for vk_id in list_ids]:
            candidate = session.query(Candidate).filter(Candidate.vk_id == vk_id).first()
            if candidate:
                list_obj.append(candidate)
        return list_obj
    else:
        return []


def get_blacklist_ids(session: Session, user_vk_id: int) -> list:
    """
    Ищет 'vk_id' кандидатов, которые помещены в черный список
    Аргументы:
        - session > активная сессия для взаимодействия
            созданная от Session(engine);
        - user_vk_id > ID пользователя из таблицы 'users' для которого идет поиск;
    Возвращает:
        - список 'vk_id' кандидатов, которые добавлены в черный список у пользователя;
        - [] пустой список, если ни кто не добавлен
    """
    check = all([
        isinstance(session, Session),
        isinstance(user_vk_id, int)
    ])

    if not check:
        raise ValueError("Один из аргументов имеет не верный тип данных")

    list_ids = session.query(Blacklist.candidate_vk_id).filter(Blacklist.user_vk_id == user_vk_id).all()

    if list_ids:
        list_vk_ids = []
        for vk_id in [vk_id[0] for vk_id in list_ids]:
            vk_id = session.query(Candidate.vk_id).filter(Candidate.vk_id == vk_id).first()
            if vk_id:
                list_vk_ids.append(vk_id[0])
        return list_vk_ids
    else:
        return []


def get_user_by_vk_id(session: Session, vk_id: int) -> User | None:
    """
    Находит пользователя по 'vk_id' в таблице 'users'
    Аргументы:
        - session > активная сессия для взаимодействия
            созданная от Session(engine);
        - vk_id > VK ID пользователя из таблицы 'users'
    Возвращает:
        - Объект класса 'User', если он был найден;
        - None, если ни чего не найдено
    """
    check = all([
        isinstance(session, Session),
        isinstance(vk_id, int)
    ])

    if not check:
        raise ValueError("Один из аргументов имеет не верный тип данных")

    return session.query(User).filter(User.vk_id == vk_id).first()


def get_candidate_by_vk_id(session: Session, vk_id: int) -> Candidate | None:
    """
    Находит кандидата по 'vk_id' в таблице 'candidates'
    Аргументы:
        - session > активная сессия для взаимодействия
            созданная от Session(engine);
        - vk_id > VK ID кандидата из таблицы 'candidates'
    Возвращает:
        - Объект класса 'Candidate', если он найден;
        - None, если кандидата не нашлось
    """
    check = all([
        isinstance(session, Session),
        isinstance(vk_id, int)
    ])

    if not check:
        raise ValueError("Один из аргументов имеет не верный тип данных")

    return session.query(Candidate).filter(Candidate.vk_id == vk_id).first()


def filter_candidates(
    candidates: list[dict],
    blacklist_ids: list[int],
    favorites_ids: list[int]
) -> list[dict]:
    """
    Функция для фильтрации поступивших кандидатов, убирает тех кто есть в ЧС или в избранном
    Аргументы:
        - candidates > список кандидатов от VK API;
        - blacklist_ids > список VK ID пользователей находящихся в черном списке;
        - favorites_ids > список VK ID избранных пользователей
    Возвращает:
        - отфильтрованный список кандидатов.
    """
    check = all([
        isinstance(candidates, list),
        isinstance(blacklist_ids, list),
        isinstance(favorites_ids, list)
    ])

    if not check:
        raise ValueError("Один из аргументов имеет не верный тип данных")

    exclude_ids = set(blacklist_ids + favorites_ids)

    return [rec for rec in candidates if rec['id'] not in exclude_ids]