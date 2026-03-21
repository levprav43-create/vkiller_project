from database.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from vk_service.vk_client import VKClient
import vk_api
from vk_api import longpoll
from dotenv import load_dotenv
import os
import time

try:
    from database.db_manager import (
        get_or_create_user,
        add_candidate,
        add_to_favorites,
        add_to_blacklist,
        get_favorites,
        get_blacklist_ids,
        filter_candidates,
        get_user_by_vk_id
    )
    DB_FUNCTIONS_AVAILABLE = True
    print("✅ Функции db_manager.py загружены")
except ImportError as e:
    DB_FUNCTIONS_AVAILABLE = False
    print(f"⚠️  Функции db_manager.py ещё не готовы: {e}")

load_dotenv()

engine = None
LAST_BOT_MESSAGES = []
user_candidates = {}


def main():
    global engine, DB_FUNCTIONS_AVAILABLE, LAST_BOT_MESSAGES, user_candidates
    
    print("🔍 DEBUG: Инициализация...")
    
    try:
        DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        engine = create_engine(DATABASE_URL, echo=False)
        Base.metadata.create_all(bind=engine)
        print("✅ Подключение к БД успешно")
    except Exception as db_error:
        print(f"⚠️  Не удалось подключиться к БД: {db_error}")
        DB_FUNCTIONS_AVAILABLE = False
    
    vk_token = os.getenv('VK_TOKEN')
    print(f"🔍 DEBUG: Токен: {vk_token[:20] if vk_token else 'None'}...")
    
    vk_session = vk_api.VkApi(token=vk_token)
    
    try:
        user = vk_session.method('users.get', {'v': '5.131'})
        print(f"✅ Токен работает! Я: {user[0]['first_name']} {user[0]['last_name']} (ID: {user[0]['id']})")
    except Exception as e:
        print(f"❌ Токен НЕ работает: {e}")
        return
    
    vk_client = VKClient()
    
    print("🤖 Бот VKinder запущен...")
    
    try:
        lp = longpoll.VkLongPoll(vk_session)
        print(f"✅ VkLongPoll инициализирован")
    except Exception as e:
        print(f"❌ Ошибка Long Poll: {e}")
        return
    
    print("🔄 Ожидание сообщений...")
    
    for event in lp.listen():
        if event.type == longpoll.VkEventType.MESSAGE_NEW:
            try:
                raw_id = getattr(event, 'from_user', None)
                if not raw_id or raw_id is False:
                    raw_id = getattr(event, 'peer_id', None)
                
                try:
                    user_id = int(raw_id) if raw_id else None
                except (ValueError, TypeError):
                    user_id = None
                
                if user_id and user_id < 0:
                    user_id = abs(user_id)
                
                text = getattr(event, 'text', None)
                peer_id = getattr(event, 'peer_id', None)
                
                if user_id is None or user_id <= 0 or not text or peer_id is None:
                    continue
                
                print(f"💬 Сообщение от {user_id}: {text[:50]}...")
                
                # 🔧 Сохранение пользователя в БД (всегда, для всех команд)
                if DB_FUNCTIONS_AVAILABLE and engine:
                    with Session(engine) as db_session:
                        try:
                            user_info = vk_client.get_user_info(user_id)
                            if not user_info:
                                user_info = {}
                            
                            first_name = user_info.get('first_name') or 'Н'
                            last_name = user_info.get('last_name') or 'Н'
                            city = user_info.get('city', {}).get('title') if user_info.get('city') else ''
                            age = user_info.get('age') or 25
                            sex = user_info.get('sex') or 1
                            
                            user = get_or_create_user(
                                db_session,
                                vk_id=user_id,
                                first_name=first_name,
                                last_name=last_name,
                                city=city,
                                age=age,
                                sex=sex
                            )
                            db_session.commit()
                        except Exception as db_error:
                            print(f"⚠️  Ошибка БД: {db_error}")
                
                command = text.strip().lower()
                
                # =================================================================
                # КОМАНДА: начать
                # =================================================================
                if command in ['начать', 'start', '/start', 'тест', 'test']:
                    if user_id in user_candidates:
                        del user_candidates[user_id]
                    if f"{user_id}_index" in user_candidates:
                        del user_candidates[f"{user_id}_index"]
                    response = "🔍 Привет! Бот работает! 🎉\nНапиши 'далее' для поиска пары"
                
                # =================================================================
                # КОМАНДА: далее (поиск кандидатов)
                # =================================================================
                elif command == 'далее':
                    if DB_FUNCTIONS_AVAILABLE and engine:
                        with Session(engine) as db_session:
                            try:
                                current_user = get_or_create_user(
                                    db_session, vk_id=user_id,
                                    first_name="Н", last_name="Н", city="", age=25, sex=1
                                )
                                blacklist_vk_ids = get_blacklist_ids(db_session, user_id)
                                favorites = get_favorites(db_session, user_id)
                                favorites_vk_ids = [c.candidate_vk_id for c in favorites]
                                
                                search_city = ''
                                
                                # Если нет кандидатов — ищем новых
                                if user_id not in user_candidates or not user_candidates[user_id]:
                                    print(f"🔍 Поиск: age={current_user.age}, sex={current_user.sex}, city='{search_city}'")
                                    
                                    raw_candidates = vk_client.search_users(
                                        age=current_user.age if current_user.age else 25,
                                        sex=current_user.sex if current_user.sex else 1,
                                        city=search_city,
                                        count=10
                                    )
                                    
                                    print(f"🔍 Найдено от VK API: {len(raw_candidates)}")
                                    
                                    filtered = filter_candidates(raw_candidates, blacklist_vk_ids, favorites_vk_ids)
                                    user_candidates[user_id] = filtered
                                
                                candidates = user_candidates.get(user_id, [])
                                
                                if candidates:
                                    # Берём следующего кандидата
                                    if f"{user_id}_index" not in user_candidates:
                                        user_candidates[f"{user_id}_index"] = 0
                                    
                                    idx = user_candidates[f"{user_id}_index"]
                                    if idx >= len(candidates):
                                        user_candidates[f"{user_id}_index"] = 0
                                        idx = 0
                                    
                                    candidate = candidates[idx]
                                    user_candidates[f"{user_id}_index"] = idx + 1
                                    
                                    # 🔧 Сохраняем кандидата в БД
                                    try:
                                        add_candidate(
                                            db_session,
                                            get_user_by_vk_id(db_session, user_id).id,
                                            candidate
                                        )
                                        db_session.commit()
                                    except:
                                        pass  # Не критично, если не сохранится
                                    
                                    # Формируем ответ с фото
                                    photos = candidate.get('photos', [])
                                    photo_text = ""
                                    if photos:
                                        photo_text = "\n".join([f"📸 {p}" for p in photos[:3]])
                                    else:
                                        photo_text = "📸 Нет фото (профиль закрыт или нет фото)"
                                    
                                    response = (
                                        f"👤 {candidate.get('first_name', 'Н')} {candidate.get('last_name', 'Н')}, {candidate.get('age', 'N/A')} лет\n"
                                        f"📍 {candidate.get('city', 'Город не указан')}\n"
                                        f"🔗 {candidate.get('profile_url', '')}\n\n"
                                        f"{photo_text}\n\n"
                                        f"💕 Нравится? Напиши 'нравится' чтобы сохранить\n"
                                        f"➡️ Напиши 'далее' для следующего"
                                    )
                                else:
                                    response = "😔 К сожалению, подходящих кандидатов не найдено. Попробуй позже!"
                                    if user_id in user_candidates:
                                        del user_candidates[user_id]
                                    if f"{user_id}_index" in user_candidates:
                                        del user_candidates[f"{user_id}_index"]
                                        
                            except Exception as db_error:
                                response = "⚠️ Ошибка поиска"
                                print(f"❌ Ошибка: {db_error}")
                    else:
                        response = "👤 Поиск... (БД недоступна)"
                
                # =================================================================
                # КОМАНДА: избранное (показать список)
                # =================================================================
                elif command == 'избранное':
                    if DB_FUNCTIONS_AVAILABLE and engine:
                        with Session(engine) as db_session:
                            try:
                                user_obj = get_user_by_vk_id(db_session, user_id)
                                fav_list = get_favorites(db_session, user_obj.id)
                                
                                if fav_list:
                                    items = []
                                    for fav in fav_list:
                                        # 🔧 ИСПРАВЛЕНИЕ: используем .vk_id вместо .candidate_vk_id
                                        vk_id = getattr(fav, 'vk_id', getattr(fav, 'candidate_vk_id', 'unknown'))
                                        items.append(f"- https://vk.com/id{vk_id}")
                                    response = f"⭐ Ваше избранное ({len(fav_list)}):\n" + "\n".join(items)
                                else:
                                    response = "⭐ Ваш список избранного пуст"
                            except Exception as e:
                                response = f"⚠️ Ошибка: {e}"
                    else:
                        response = "⭐ Ваш список избранного (БД недоступна)"
                
                # =================================================================
                # КОМАНДА: нравится / like / + (добавить в избранное)
                # =================================================================
                elif command in ['нравится', 'like', '+']:
                    if DB_FUNCTIONS_AVAILABLE and engine:
                        with Session(engine) as db_session:
                            try:
                                # Проверяем, есть ли текущий кандидат
                                if user_id in user_candidates and f"{user_id}_index" in user_candidates:
                                    idx = user_candidates[f"{user_id}_index"] - 1
                                    if idx >= 0 and idx < len(user_candidates[user_id]):
                                        candidates = user_candidates[user_id]
                                        candidate = candidates[idx]
                                        candidate_vk_id = candidate.get('id')
                                        
                                        user_obj = get_user_by_vk_id(db_session, user_id)
                                        add_to_favorites(db_session, user_obj.id, candidate_vk_id)
                                        db_session.commit()
                                        
                                        response = f"✅ {candidate.get('first_name')} добавлен в избранное!"
                                    else:
                                        response = "⚠️ Сначала напиши 'далее' чтобы увидеть кандидата"
                                else:
                                    response = "⚠️ Сначала напиши 'далее' чтобы увидеть кандидата"
                            except Exception as e:
                                response = f"⚠️ Ошибка: {e}"
                    else:
                        response = "✅ Добавлено в избранное! (БД недоступна)"
                
                # =================================================================
                # КОМАНДА: не нравится / blacklist / - (добавить в ЧС)
                # =================================================================
                elif command in ['не нравится', 'blacklist', '-']:
                    if DB_FUNCTIONS_AVAILABLE and engine:
                        with Session(engine) as db_session:
                            try:
                                # Проверяем, есть ли текущий кандидат
                                if user_id in user_candidates and f"{user_id}_index" in user_candidates:
                                    idx = user_candidates[f"{user_id}_index"] - 1
                                    if idx >= 0 and idx < len(user_candidates[user_id]):
                                        candidates = user_candidates[user_id]
                                        candidate = candidates[idx]
                                        candidate_vk_id = candidate.get('id')
                                        
                                        user_obj = get_user_by_vk_id(db_session, user_id)
                                        add_to_blacklist(db_session, user_obj.id, candidate_vk_id)
                                        db_session.commit()
                                        
                                        response = f"✅ {candidate.get('first_name')} добавлен в чёрный список!"
                                    else:
                                        response = "⚠️ Сначала напиши 'далее' чтобы увидеть кандидата"
                                else:
                                    response = "⚠️ Сначала напиши 'далее' чтобы увидеть кандидата"
                            except Exception as e:
                                response = f"⚠️ Ошибка: {e}"
                    else:
                        response = "✅ Добавлено в чёрный список! (БД недоступна)"
                
                # =================================================================
                # КОМАНДА: неизвестная
                # =================================================================
                else:
                    response = "Напишите /начать для поиска пары 💕"
                
                # 🔧 Защита от зацикливания (только ответы бота)
                response_hash = f"{peer_id}:{response.strip()}"
                if response_hash in LAST_BOT_MESSAGES:
                    print("⏭️  Пропущено: дубль ответа бота")
                    continue
                LAST_BOT_MESSAGES.append(response_hash)
                if len(LAST_BOT_MESSAGES) > 20:
                    LAST_BOT_MESSAGES.pop(0)
                
                print(f"📤 Отправка в peer_id={peer_id}")
                vk_session.method('messages.send', {
                    'peer_id': peer_id,
                    'message': response,
                    'random_id': vk_api.utils.get_random_id(),
                    'v': '5.131'
                })
                print(f"✅ Ответ отправлен")
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                import traceback
                traceback.print_exc()


if __name__ == '__main__':
    main()