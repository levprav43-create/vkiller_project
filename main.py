from database.models import Base
from sqlalchemy import create_engine
from vk_service.vk_client import VKClient
import vk_api  # type: ignore[import-untyped]
from vk_api import longpoll  # type: ignore[import-untyped]
from dotenv import load_dotenv
import os

load_dotenv()


def main():
    # Создаём движок БД
    DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    engine = create_engine(DATABASE_URL, echo=False)
    
    # Создаём таблицы в БД
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
                user_id = event.obj['from_id']
                text = event.obj['text']
                print(f"💬 Сообщение от {user_id}: {text}")
                
                vk_session.method('messages.send', {  # type: ignore[attr-defined]
                    'peer_id': event.peer_id,
                    'message': f"✅ Получил: {text}\n🔧 Бот в разработке...",
                    'random_id': vk_api.utils.get_random_id(),  # type: ignore[attr-defined]
                    'v': '5.131'
                })
            except Exception as e:
                print(f"❌ Ошибка: {e}")


if __name__ == '__main__':
    main()