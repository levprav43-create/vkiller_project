import vk_api
from vk_api.utils import get_random_id
import os
from dotenv import load_dotenv

load_dotenv()


class VKClient:
    def __init__(self):
        self.token = os.getenv('VK_TOKEN')
        self.vk = vk_api.VkApi(token=self.token)
        self.version = os.getenv('VK_VERSION', '5.131')
    
    def get_user_info(self, user_id: int):
        """Получить информацию о пользователе"""
        try:
            response = self.vk.method('users.get', {
                'user_ids': user_id,
                'fields': 'city,age,sex,photo_200',
                'v': self.version
            })
            if response:
                user = response[0]
                return {
                    'id': user.get('id'),
                    'first_name': user.get('first_name'),
                    'last_name': user.get('last_name'),
                    'city': user.get('city'),
                    'age': user.get('age'),
                    'sex': user.get('sex'),
                    'photo_200': user.get('photo_200')
                }
        except Exception as e:
            print(f"❌ Ошибка получения инфо: {e}")
        return {}
    
    def search_users(self, age: int, sex: int, city: str = '', count: int = 10):
        """Поиск пользователей по критериям"""
        try:
            # Преобразуем city в ID если это число
            city_id = None
            if city and str(city).isdigit():
                city_id = int(city)
            
            params = {
                'age_from': max(18, age - 5),
                'age_to': age + 10,
                'sex': sex,
                'has_photo': 1,
                'count': count,
                'v': self.version
            }
            
            if city_id:
                params['city'] = city_id
            
            response = self.vk.method('users.search', params)
            
            candidates = []
            if response and 'items' in response:
                for user in response['items']:
                    candidate = {
                        'id': user.get('id'),
                        'first_name': user.get('first_name'),
                        'last_name': user.get('last_name'),
                        'age': user.get('age'),
                        'city': user.get('city', {}).get('title') if user.get('city') else '',
                        'profile_url': f"https://vk.com/id{user.get('id')}"
                    }
                    
                    # 🔧 Получаем фото кандидата
                    photos = self._get_user_photos(user.get('id'))
                    candidate['photos'] = photos
                    
                    candidates.append(candidate)
            
            return candidates
            
        except Exception as e:
            print(f"❌ Ошибка поиска: {e}")
            return []
    
    def _get_user_photos(self, user_id: int, count: int = 3):
        """Получить топ-3 фото пользователя по лайкам"""
        try:
            response = self.vk.method('photos.get', {
                'owner_id': user_id,
                'album_id': 'profile',
                'extended': 1,
                'count': 10,
                'v': self.version
            })
            
            if response and 'items' in response:
                # Сортируем по лайкам
                photos = sorted(
                    response['items'],
                    key=lambda x: x.get('likes', {}).get('count', 0),
                    reverse=True
                )[:count]
                
                # Возвращаем URL фото
                return [p.get('photo_807') or p.get('photo_604') or p.get('photo_200') 
                        for p in photos 
                        if p.get('photo_807') or p.get('photo_604')]
            
            return []
            
        except vk_api.exceptions.ApiError as e:
            if e.code == 30:
                print(f"⚠️  Профиль {user_id} закрыт — фото недоступны")
            else:
                print(f"❌ Ошибка получения фото: {e}")
            return []
        except Exception as e:
            print(f"❌ Ошибка получения фото: {e}")
            return []
    
    def send_message_with_photos(self, peer_id: int, text: str, photo_urls: list):
        """Отправить сообщение с фото как attachment"""
        try:
            # Формируем attachments из фото
            attachments = []
            for url in photo_urls:
                if url:
                    # Для внешних фото используем простой формат
                    attachments.append(url)
            
            params = {
                'peer_id': peer_id,
                'message': text,
                'random_id': get_random_id(),
                'v': self.version
            }
            
            if attachments:
                params['attachment'] = ','.join(attachments)
            
            return self.vk.method('messages.send', params)
            
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")
            return None