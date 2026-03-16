from sqlalchemy import String, ForeignKey, Sequence, Integer, Column, SmallInteger, CheckConstraint, or_, and_
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, sessionmaker
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
        id,
        vk_id,
        first_name,
        last_name,
        city,
        age,
        gender
):
    with Session() as session:
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
        id,
        vk_id,
        first_name,
        last_name,
        city,
        age,
        gender,
        profile_url,
        photo_1,
        photo_2,
        photo_3
):
    with Session() as session:
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
        id,
        user_id,
        candidate_id,
):
    with Session() as session:
        session.add(Favorite(
            id=id,
            user_id=user_id,
            candidate_id=candidate_id,
        ))
        session.commit()
        return True


def add_blacklist(
        id,
        user_id,
        candidate_id,
):
    with Session() as session:
        session.add(Blacklist(
            id=id,
            user_id=user_id,
            candidate_id=candidate_id,
        ))
        session.commit()
        return True