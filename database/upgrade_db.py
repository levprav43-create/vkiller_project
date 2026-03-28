from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Добавляем UNIQUE в favorites
    conn.execute(text("""
        ALTER TABLE favorites 
        ADD CONSTRAINT unique_favorite UNIQUE (user_id, candidate_vk_id)
    """))
    
    # Добавляем UNIQUE в blacklists
    conn.execute(text("""
        ALTER TABLE blacklists 
        ADD CONSTRAINT unique_blacklist UNIQUE (user_id, candidate_vk_id)
    """))
    
    conn.commit()

print("✅ Уникальные ограничения добавлены!")