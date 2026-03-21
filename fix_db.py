from sqlalchemy import create_engine
from database.models import Base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)

print("Пересоздание таблиц БД")

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

print("Таблицы были удалены и заново созданы")