from sqlalchemy import String, ForeignKey, Sequence, Integer, Column, SmallInteger, CheckConstraint, or_, and_
from sqlalchemy.orm import mapped_column, sessionmaker
from database.models import *
import sqlalchemy


DSN = 'postgresql://postgres:GrePost_SQL@localhost:5432/users_database'

engine = sqlalchemy.create_engine(DSN)

Session = sessionmaker(bind=engine)


def create_tables(cleaning=False):
    """
    Функция создаёт таблицы назначенные наследованием от класса Base
    Аргумент - cleaning со значением True позволяет удалить и заново создать все таблицы
        по умолчанию равен False
    Возвращает: True при удачном создании или когда таблицы уже существуют
    """
    if cleaning:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return True


def add_user(
        session: Session,
        id: int,
        vk_id: int,
        first_name: str,
        last_name: str,
        city: str,
        age: int,
        gender: int
):
    """
    Функция добавляет пользователя в БД в таблицу 'users'
    Аргументы:
        - session > активная сессия для взаимодействия
            созданная от sessionmaker(engine);
        - id > уникальный ID для пользователя;
        - vk_id > ID пользователя из VK;
        - first_name > имя пользователя;
        - last_name > фамилия пользователя;
        - city > город пользователя;
        - gender > род пользователя (число)
            0 = Женский
            1 = Мужской
            прочее - не указан;
    Возвращает:
        True при успешном выполнении
    """
    with session() as session:
        session.add(User(
            id=id,
            vk_id=vk_id,
            first_name=first_name,
            last_name=last_name,
            city=city,
            age=age,
            gender=gender
        ))
        session.commit()
        return True


def add_candidate_for_dating(
        session: Session,
        id: int,
        vk_id: int,
        first_name: str,
        last_name: str,
        city: str,
        age: int,
        gender: int,
        profile_url: str,
        photo_1: str,
        photo_2: str,
        photo_3: str
):
    """
        Функция добавляет кандидата для знакомства в БД в таблицу 'candidates'
        Аргументы:
            - session > активная сессия для взаимодействия
                созданная от sessionmaker(engine);
            - id > уникальный ID для кандидата;
            - vk_id > ID пользователя из VK;
            - first_name > имя пользователя;
            - last_name > фамилия пользователя;
            - city > город пользователя;
            - gender > род пользователя (число)
                0 = Женский
                1 = Мужской
                прочее - не указан;
            - profile_url > ссылка на профиль в VK;
            - photo_1 > ссылка №1 на популярное фото в VK
            - photo_2 > ссылка №2 на популярное фото в VK
            - photo_3 > ссылка №3 на популярное фото в VK
        Возвращает:
            При корректном завершении True
        """
    with session() as session:
        session.add(Candidate(
            id=id,
            vk_id=vk_id,
            first_name=first_name,
            last_name=last_name,
            city=city,
            age=age,
            gender=gender,
            profile_url=profile_url,
            photo_1=photo_1,
            photo_2=photo_2,
            photo_3=photo_3,
        ))
        session.commit()
        return True


def add_favorites(
        session: Session,
        id: int,
        user_id: int,
        candidate_id: DateTime,
):
    """
    Функция добавляет выбранного человека в избранное для пользователя
        сохраняя его в БД в таблице 'favorites'
    Аргументы:
        - session > активная сессия для взаимодействия
                созданная от sessionmaker(engine);
        - id > уникальный ID для избранного;
        - user_id > ID пользователя из таблицы 'users' для которого
                выбранный человек добавляется в избранные;
        - candidate_id > ID понравившегося пользователя
    Возвращает:
        True при успешном выполнении кода
    """
    with session() as session:
        session.add(Favorite(
            id=id,
            user_id=user_id,
            candidate_id=candidate_id,
        ))
        session.commit()
        return True


def add_blacklist(
        session: Session,
        id: int,
        user_id: int,
        candidate_id: DateTime,
):
    """
    Функция добавляет выбранного человека в чёрный список для пользователя
        сохраняя его в БД в таблице 'blacklist'
    Аргументы:
        - session > активная сессия для взаимодействия
                созданная от sessionmaker(engine);
        - id > уникальный идентификатор записи;
        - user_id > ID пользователя из таблицы 'users' для которого
                выбранный человек добавляется в черный список;
        - candidate_id > ID пользователя добавляемого в черный список
    Возвращает:
        True при успешном исполнении кода
    """
    with session() as session:
        session.add(Blacklist(
            id=id,
            user_id=user_id,
            candidate_id=candidate_id,
        ))
        session.commit()
        return True
