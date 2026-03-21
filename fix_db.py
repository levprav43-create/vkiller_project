from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:makinTosh1122@localhost:5432/vkiller_db"
engine = create_engine(DATABASE_URL)

print("🔧 Пересоздание таблиц БД...")

with engine.connect() as conn:
    # Удаляем старые таблицы (в правильном порядке из-за внешних ключей)
    conn.execute(text("DROP TABLE IF EXISTS blacklists CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS favorites CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS candidates CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
    conn.commit()
    print("✅ Старые таблицы удалены")
    
    # Создаём users
    conn.execute(text("""
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            vk_id INTEGER UNIQUE NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            city VARCHAR(100),
            age INTEGER,
            sex INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    # Создаём candidates
    conn.execute(text("""
        CREATE TABLE candidates (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            vk_id INTEGER NOT NULL,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            age INTEGER,
            city VARCHAR(100),
            photo_1 VARCHAR(255),
            photo_2 VARCHAR(255),
            photo_3 VARCHAR(255),
            profile_url VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    # Создаём favorites
    conn.execute(text("""
        CREATE TABLE favorites (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            candidate_vk_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    # Создаём blacklists
    conn.execute(text("""
        CREATE TABLE blacklists (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            candidate_vk_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    conn.commit()
    print("✅ Все таблицы созданы с правильными колонками")

print("✅ Готово! Перезапусти бота: python main.py")