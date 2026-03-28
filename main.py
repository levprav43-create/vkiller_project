from database.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from vk_service.vk_client import VKClient
import vk_api
from vk_api import longpoll
from dotenv import load_dotenv
import os
import time
import json

try:
    from database.db_manager import (
        get_or_create_user,
        add_candidate,
        add_to_favorites,
        add_to_blacklist,
        get_favorites,
        get_blacklist_ids,
        filter_candidates,
        get_user_by_vk_id,
    )
    DB_FUNCTIONS_AVAILABLE = True
    print("✅ Функции db_manager.py загружены")
except ImportError as e:
    DB_FUNCTIONS_AVAILABLE = False
    print(f"⚠️  Функции db_manager.py: {e}")

load_dotenv()

engine = None
LAST_BOT_MESSAGES = []
user_candidates = {}


def main():
    """Основная функция бота."""
    global engine, DB_FUNCTIONS_AVAILABLE, LAST_BOT_MESSAGES, user_candidates

    print("🔍 DEBUG: Инициализация...")

    try:
        db_user = os.getenv('DB_USER')
        db_pass = os.getenv('DB_PASSWORD')
        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT')
        db_name = os.getenv('DB_NAME')

        database_url = (
            f"postgresql://{db_user}:{db_pass}@"
            f"{db_host}:{db_port}/{db_name}"
        )
        engine = create_engine(database_url, echo=False)
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
        first = user[0]['first_name']
        last = user[0]['last_name']
        uid = user[0]['id']
        print(f"✅ Токен работает! Я: {first} {last} (ID: {uid})")
    except vk_api.exceptions.ApiError as e:
        print(f"❌ Токен НЕ работает: {e}")
        return
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return

    vk_client = VKClient()

    print("🤖 Бот VKinder запущен...")

    try:
        lp = longpoll.VkLongPoll(vk_session)
        print("✅ VkLongPoll инициализирован")
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

                # Сохранение пользователя в БД
                if DB_FUNCTIONS_AVAILABLE and engine:
                    with Session(engine) as db_session:
                        try:
                            user_info = vk_client.get_user_info(user_id)
                            if not user_info:
                                user_info = {}

                            first_name = user_info.get('first_name') or 'Н'
                            last_name = user_info.get('last_name') or 'Н'
                            city_data = user_info.get('city', {})
                            city = city_data.get('title') if city_data else ''
                            age = user_info.get('age') or 25
                            sex = user_info.get('sex') or 1

                            user = get_or_create_user(
                                db_session,
                                vk_id=user_id,
                                first_name=first_name,
                                last_name=last_name,
                                city=city,
                                age=age,
                                sex=sex,
                            )
                            db_session.commit()
                        except Exception as db_error:
                            print(f"⚠️  Ошибка БД: {db_error}")

                command = text.strip().lower()

                # КОМАНДА: начать
                if command in ['начать', 'start', '/start', 'тест', 'test']:
                    if user_id in user_candidates:
                        del user_candidates[user_id]
                    index_key = f"{user_id}_index"
                    if index_key in user_candidates:
                        del user_candidates[index_key]
                    response = (
                        "🔍 Привет! Бот работает! 🎉\n"
                        "Напиши 'далее' для поиска пары"
                    )

                # КОМАНДА: далее
                elif command == 'далее':
                    if DB_FUNCTIONS_AVAILABLE and engine:
                        with Session(engine) as db_session:
                            try:
                                current_user = get_or_create_user(
                                    db_session,
                                    vk_id=user_id,
                                    first_name="Н",
                                    last_name="Н",
                                    city="",
                                    age=25,
                                    sex=1,
                                )
                                blacklist_ids = get_blacklist_ids(
                                    db_session, user_id
                                )
                                favorites = get_favorites(db_session, user_id)
                                fav_ids = [c.candidate_vk_id for c in favorites]

                                search_city = ''

                                if (
                                    user_id not in user_candidates
                                    or not user_candidates[user_id]
                                ):
                                    print(
                                        f"🔍 Поиск: age={current_user.age}, "
                                        f"sex={current_user.sex}, "
                                        f"city='{search_city}'"
                                    )

                                    raw_candidates = vk_client.search_users(
                                        age=current_user.age or 25,
                                        sex=current_user.sex or 1,
                                        city=search_city,
                                        count=10,
                                    )

                                    print(
                                        f"🔍 Найдено от VK API: "
                                        f"{len(raw_candidates)}"
                                    )

                                    filtered = filter_candidates(
                                        raw_candidates,
                                        blacklist_ids,
                                        fav_ids,
                                    )
                                    user_candidates[user_id] = filtered

                                candidates = user_candidates.get(user_id, [])

                                if candidates:
                                    index_key = f"{user_id}_index"
                                    if index_key not in user_candidates:
                                        user_candidates[index_key] = 0

                                    idx = user_candidates[index_key]
                                    if idx >= len(candidates):
                                        user_candidates[index_key] = 0
                                        idx = 0

                                    candidate = candidates[idx]
                                    user_candidates[index_key] = idx + 1

                                    # Сохраняем кандидата в БД
                                    try:
                                        user_obj = get_user_by_vk_id(
                                            db_session, user_id
                                        )
                                        add_candidate(
                                            db_session,
                                            user_obj.id,
                                            candidate,
                                        )
                                        db_session.commit()
                                    except Exception:
                                        pass

                                    photos = candidate.get('photos', [])
                                    if photos:
                                        photo_lines = [
                                            f"📸 {p}" for p in photos[:3]
                                        ]
                                        photo_text = "\n".join(photo_lines)
                                    else:
                                        photo_text = (
                                            "📸 Нет фото "
                                            "(профиль закрыт)"
                                        )

                                    first = candidate.get('first_name', 'Н')
                                    last = candidate.get('last_name', 'Н')
                                    age_val = candidate.get('age', 'N/A')
                                    city_val = candidate.get(
                                        'city', 'Город не указан'
                                    )
                                    url = candidate.get('profile_url', '')

                                    response = (
                                        f"👤 {first} {last}, {age_val} лет\n"
                                        f"📍 {city_val}\n"
                                        f"🔗 {url}\n\n"
                                        f"{photo_text}\n\n"
                                        f"💕 Напиши 'нравится' "
                                        f"чтобы сохранить\n"
                                        f"➡️ Напиши 'далее' для следующего"
                                    )
                                else:
                                    response = (
                                        "😔 Кандидатов не найдено. "
                                        "Попробуй позже!"
                                    )
                                    if user_id in user_candidates:
                                        del user_candidates[user_id]
                                    if index_key in user_candidates:
                                        del user_candidates[index_key]

                            except Exception as db_error:
                                response = "⚠️ Ошибка поиска"
                                print(f"❌ Ошибка: {db_error}")
                    else:
                        response = "👤 Поиск... (БД недоступна)"

                # КОМАНДА: избранное
                elif command == 'избранное':
                    if DB_FUNCTIONS_AVAILABLE and engine:
                        with Session(engine) as db_session:
                            try:
                                user_obj = get_user_by_vk_id(
                                    db_session, user_id
                                )
                                fav_list = get_favorites(
                                    db_session, user_obj.id
                                )

                                if fav_list:
                                    items = []
                                    for fav in fav_list:
                                        vk_id = getattr(
                                            fav, 'vk_id',
                                            getattr(
                                                fav, 'candidate_vk_id',
                                                'unknown'
                                            )
                                        )
                                        items.append(
                                            f"- https://vk.com/id{vk_id}"
                                        )
                                    count = len(fav_list)
                                    response = (
                                        f"⭐ Ваше избранное ({count}):\n"
                                        + "\n".join(items)
                                    )
                                else:
                                    response = "⭐ Ваш список избранного пуст"
                            except vk_api.exceptions.ApiError as e:
                                print(f"⚠️  VK API Error: {e}")
                                response = "⚠️ Ошибка VK API"
                            except Exception as e:
                                print(f"❌ Ошибка: {e}")
                                response = "⚠️ Произошла ошибка"
                    else:
                        response = "⭐ Ваш список избранного (БД недоступна)"

                # КОМАНДА: нравится
                elif command in ['нравится', 'like', '+']:
                    if DB_FUNCTIONS_AVAILABLE and engine:
                        with Session(engine) as db_session:
                            try:
                                if (
                                    user_id in user_candidates
                                    and f"{user_id}_index" in user_candidates
                                ):
                                    idx = user_candidates[f"{user_id}_index"]
                                    idx = idx - 1
                                    cands = user_candidates[user_id]
                                    if 0 <= idx < len(cands):
                                        candidate = cands[idx]
                                        cand_vk_id = candidate.get('id')

                                        user_obj = get_user_by_vk_id(
                                            db_session, user_id
                                        )
                                        add_to_favorites(
                                            db_session,
                                            user_obj.id,
                                            cand_vk_id,
                                        )
                                        db_session.commit()

                                        name = candidate.get('first_name', '')
                                        response = (
                                            f"✅ {name} добавлен в избранное!"
                                        )
                                    else:
                                        response = (
                                            "⚠️ Сначала напиши 'далее'"
                                        )
                                else:
                                    response = "⚠️ Сначала напиши 'далее'"
                            except vk_api.exceptions.ApiError as e:
                                print(f"⚠️  VK API Error: {e}")
                                response = "⚠️ Ошибка VK API"
                            except Exception as e:
                                print(f"❌ Ошибка: {e}")
                                response = "⚠️ Произошла ошибка"
                    else:
                        response = "✅ Добавлено! (БД недоступна)"

                # КОМАНДА: не нравится
                elif command in ['не нравится', 'blacklist', '-']:
                    if DB_FUNCTIONS_AVAILABLE and engine:
                        with Session(engine) as db_session:
                            try:
                                if (
                                    user_id in user_candidates
                                    and f"{user_id}_index" in user_candidates
                                ):
                                    idx = user_candidates[f"{user_id}_index"]
                                    idx = idx - 1
                                    cands = user_candidates[user_id]
                                    if 0 <= idx < len(cands):
                                        candidate = cands[idx]
                                        cand_vk_id = candidate.get('id')

                                        user_obj = get_user_by_vk_id(
                                            db_session, user_id
                                        )
                                        add_to_blacklist(
                                            db_session,
                                            user_obj.id,
                                            cand_vk_id,
                                        )
                                        db_session.commit()

                                        name = candidate.get('first_name', '')
                                        response = (
                                            f"✅ {name} добавлен в ЧС!"
                                        )
                                    else:
                                        response = (
                                            "⚠️ Сначала напиши 'далее'"
                                        )
                                else:
                                    response = "⚠️ Сначала напиши 'далее'"
                            except vk_api.exceptions.ApiError as e:
                                print(f"⚠️  VK API Error: {e}")
                                response = "⚠️ Ошибка VK API"
                            except Exception as e:
                                print(f"❌ Ошибка: {e}")
                                response = "⚠️ Произошла ошибка"
                    else:
                        response = "✅ Добавлено! (БД недоступна)"

                else:
                    response = "Напишите /начать для поиска пары 💕"

                # Защита от зацикливания
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
                    'v': '5.131',
                })
                print("✅ Ответ отправлен")

                time.sleep(0.5)

            except vk_api.exceptions.ApiError as e:
                print(f"⚠️  VK API Error: {e}")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                import traceback
                traceback.print_exc()


if __name__ == '__main__':
    main()