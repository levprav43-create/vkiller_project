from database.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from vk_service.vk_client import VKClient
import vk_api  # type: ignore[import-untyped]
from vk_api import longpoll  # type: ignore[import-untyped]
from dotenv import load_dotenv
import os

# 🔥 Импорт функций из db_manager (будут работать, когда Влад запушит)
try:
    from database.db_manager import (
        get_or_create_user,
        add_candidate,
        add_to_favorites,
        add_to_blacklist,
        get_favorites,
        get_blacklist_ids,
        filtering_out_elements
    )
    DB_FUNCTIONS_AVAILABLE = True
except ImportError:
    DB_FUNCTIONS_AVAILABLE = False
    print("⚠️  Функции db_manager.py ещё не готовы — работаю без БД")

load_dotenv()


def main():
    # 🔥 Создаём движок БД
    DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    engine = create_engine(DATABASE_URL, echo=False)
    
    # 🔥 Создаём таблицы в БД
    Base.metadata.create_all(bind=engine)
    
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
                
                # 🔥 ИНТЕГРАЦИЯ С БД: Сохраняем пользователя
                if DB_FUNCTIONS_AVAILABLE:
                    with Session(engine) as db_session:
                        try:
                            # Получаем инфо о пользователе из VK
                            user_info = vk_client.get_user_info(user_id)
                            
                            # Сохраняем или обновляем пользователя в БД
                            # user = get_or_create_user(
                            #     db_session,
                            #     vk_id=user_id,
                            #     first_name=user_info.get('first_name', ''),
                            #     last_name=user_info.get('last_name', ''),
                            #     city=user_info.get('city', {}).get('title') if user_info.get('city') else None,
                            #     age=user_info.get('age'),
                            #     sex=user_info.get('sex')
                            # )
                            # db_session.commit()
                            print(f"✅ Пользователь {user_id} обработан (БД готова)")
                            
                        except Exception as db_error:
                            print(f"⚠️  Ошибка БД: {db_error}")
                            db_session.rollback()
                
                # 🔥 Обработка команд бота
                command = text.strip().lower()
                
                if command in ['начать', 'start', '/start']:
                    response = "🔍 Привет! Начинаю поиск пары...\nНапиши 'далее' для следующего кандидата"
                    
                elif command == 'далее':
                    # 🔥 Здесь будет поиск кандидатов через VK API + БД
                    if DB_FUNCTIONS_AVAILABLE:
                        with Session(engine) as db_session:
                            try:
                                # Получаем ЧС и избранное
                                # blacklist_ids = get_blacklist_ids(db_session, user_id)
                                # favorites_ids = ...
                                
                                # Ищем кандидатов в VK
                                # raw_candidates = vk_client.search_users(...)
                                
                                # Фильтруем через функцию Влада
                                # filtered = filtering_out_elements(raw_candidates, blacklist_ids, favorites_ids)
                                
                                response = "👤 Показываю следующего кандидата... (функция в разработке)"
                            except Exception as db_error:
                                response = "⚠️ Ошибка поиска кандидатов"
                                print(f"❌ Ошибка: {db_error}")
                    else:
                        response = "👤 Показываю следующего кандидата... (БД ещё не готова)"
                    
                elif command == 'избранное':
                    if DB_FUNCTIONS_AVAILABLE:
                        with Session(engine) as db_session:
                            try:
                                # favorites = get_favorites(db_session, user_id)
                                response = "⭐ Ваш список избранного (функция в разработке)"
                            except Exception as db_error:
                                response = "⚠️ Ошибка получения избранного"
                    else:
                        response = "⭐ Ваш список избранного (БД ещё не готова)"
                    
                else:
                    response = "Напишите /начать для поиска пары 💕"
                
                # Отправляем ответ пользователю
                vk_session.method('messages.send', {  # type: ignore[attr-defined]
                    'peer_id': event.peer_id,
                    'message': response,
                    'random_id': vk_api.utils.get_random_id(),  # type: ignore[attr-defined]
                    'v': '5.131'
                })
                
            except Exception as e:
                print(f"❌ Ошибка обработки: {e}")


if __name__ == '__main__':
    main()