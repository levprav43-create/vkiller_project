from database.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from vk_service.vk_client import VKClient
import vk_api  # type: ignore[import-untyped]
from vk_api import longpoll  # type: ignore[import-untyped]
from dotenv import load_dotenv
import os

# Импорт функций из db_manager
try:
    from database.db_manager import (
        get_or_create_user,
        add_candidate,
        add_to_favorites,
        add_to_blacklist,
        get_favorites,
        get_blacklist_ids,
        filter_candidates
    )
    DB_FUNCTIONS_AVAILABLE = True
    print("✅ Функции db_manager.py загружены")
except ImportError as e:
    DB_FUNCTIONS_AVAILABLE = False
    print(f"⚠️  Функции db_manager.py ещё не готовы: {e}")

load_dotenv()

# Глобальная переменная для engine
engine = None


def main():
    global engine, DB_FUNCTIONS_AVAILABLE
    
    # Попытка подключения к БД
    try:
        DATABASE_URL = "postgresql://postgres:makinTosh1122@localhost:5432/vkiller_db"
        engine = create_engine(DATABASE_URL, echo=False)
        Base.metadata.create_all(bind=engine)
        print("✅ Подключение к БД успешно")
    except Exception as db_error:
        print(f"⚠️  Не удалось подключиться к БД: {db_error}")
        print("🔄 Бот работает в режиме без БД (тест функционала)")
        DB_FUNCTIONS_AVAILABLE = False
    
    # Инициализация клиента VK
    vk_client = VKClient()
    
    print("🤖 Бот VKinder запущен...")
    
    # Long Polling для бота
    vk_session = vk_api.VkApi(token=os.getenv('VK_TOKEN'))  # type: ignore[attr-defined]
    lp = longpoll.VkLongPoll(vk_session)  # type: ignore[attr-defined]
    
    for event in lp.listen():
        if event.type == longpoll.VkEventType.MESSAGE_NEW and event.to_me:  # type: ignore[attr-defined]
            try:
                user_id = event.user_id
                text = event.text
                print(f"💬 Сообщение от {user_id}: {text}")
                
                # ИНТЕГРАЦИЯ С БД (только если подключение успешно)
                if DB_FUNCTIONS_AVAILABLE and engine:
                    with Session(engine) as db_session:
                        try:
                            user_info = vk_client.get_user_info(user_id)
                            user = get_or_create_user(
                                db_session,
                                vk_id=user_id,
                                first_name=user_info.get('first_name', 'Н'),
                                last_name=user_info.get('last_name', 'Н'),
                                city=user_info.get('city', {}).get('title') if user_info.get('city') else 'Н',
                                age=user_info.get('age', 10),
                                sex=user_info.get('sex', 3)
                            )   # 'H' - значит не указанно, 10 для возраста по умолчанию
                            db_session.commit()
                            print(f"✅ Пользователь {user_id} сохранён в БД")
                        except Exception as db_error:
                            print(f"⚠️  Ошибка БД: {db_error}")
                            db_session.rollback()
                
                # Обработка команд
                command = text.strip().lower()
                
                if command in ['начать', 'start', '/start']:
                    response = "🔍 Привет! Начинаю поиск пары...\nНапиши 'далее' для следующего кандидата"
                    
                elif command == 'далее':
                    if DB_FUNCTIONS_AVAILABLE and engine:
                        with Session(engine) as db_session:
                            try:
                                current_user = get_or_create_user(
                                    db_session, vk_id=user_id,
                                    first_name="", last_name="", city="", age=0, sex=0
                                )
                                blacklist_vk_ids = get_blacklist_ids(db_session, user_id)
                                favorites = get_favorites(db_session, user_id)
                                favorites_vk_ids = [c.vk_id for c in favorites]
                                
                                raw_candidates = vk_client.search_users(
                                    age=current_user.age if current_user.age else 25,
                                    sex=current_user.sex if current_user.sex else 1,
                                    city=current_user.city if current_user.city else "",
                                    count=10
                                )
                                filtered = filter_candidates(raw_candidates, blacklist_vk_ids, favorites_vk_ids)
                                
                                if filtered:
                                    candidate = filtered[0]
                                    response = (
                                        f"👤 {candidate['first_name']} {candidate['last_name']}, {candidate['age']} лет\n"
                                        f"📍 {candidate.get('city', 'Город не указан')}\n"
                                        f"🔗 {candidate['profile_url']}\n\n"
                                        f"📸 Фото: {candidate['photo_1']}\n\n"
                                        f"💕 Нравится? Напиши 'избранное' чтобы сохранить"
                                    )
                                else:
                                    response = "😔 К сожалению, подходящих кандидатов не найдено. Попробуй позже!"
                            except Exception as db_error:
                                response = "⚠️ Ошибка поиска кандидатов"
                                print(f"❌ Ошибка: {db_error}")
                    else:
                        response = "👤 Показываю следующего кандидата... (БД недоступна, режим теста)"
                    
                elif command == 'избранное':
                    if DB_FUNCTIONS_AVAILABLE and engine:
                        response = "⭐ Ваш список избранного (функция в разработке)"
                    else:
                        response = "⭐ Ваш список избранного (БД недоступна, режим теста)"
                    
                elif command.startswith('нравится') or command.startswith('like'):
                    response = "✅ Добавлено в избранное! (функция в разработке)"
                    
                elif command.startswith('не нравится') or command.startswith('blacklist'):
                    response = "✅ Добавлено в чёрный список! (функция в разработке)"
                    
                else:
                    response = "Напишите /начать для поиска пары 💕"
                
                # Отправка ответа
                vk_session.method('messages.send', {
                    'peer_id': event.peer_id,
                    'message': response,
                    'random_id': vk_api.utils.get_random_id(),
                    'v': '5.131'
                })
                
            except Exception as e:
                print(f"❌ Ошибка обработки: {e}")


if __name__ == '__main__':
    main()