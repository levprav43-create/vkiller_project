import vk_api  # type: ignore[import-untyped]
from dotenv import load_dotenv
import os

load_dotenv()


class VKClient:
    def __init__(self):
        self.token = os.getenv('VK_TOKEN')
        self.version = os.getenv('VK_VERSION', '5.131')
        self.vk = vk_api.VkApi(token=self.token)  # type: ignore[attr-defined]
    
    def get_user_info(self, user_id=None):
        """Получить информацию о пользователе"""
        params = {
            'fields': 'city,age,sex',
            'v': self.version
        }
        if user_id:
            params['user_ids'] = user_id
        
        response = self.vk.method('users.get', params)
        return response[0] if response else None
    
    def search_users(self, age, sex, city, offset=0, count=10):
        """Поиск кандидатов"""
        search_sex = 2 if sex == 1 else 1
        
        params = {
            'age_from': age - 3,
            'age_to': age + 3,
            'sex': search_sex,
            'city': city,
            'has_photo': 1,
            'offset': offset,
            'count': count,
            'v': self.version
        }
        
        try:
            result = self.vk.method('users.search', params)
            return result.get('items', [])
        except Exception as e:
            print(f"Ошибка поиска: {e}")
            return []
    
    def get_user_photos(self, user_id, count=10):
        """Получить фото пользователя"""
        try:
            photos = self.vk.method('photos.get', {
                'owner_id': user_id,
                'album_id': 'profile',
                'extended': 1,
                'count': count,
                'v': self.version
            })
            
            sorted_photos = sorted(
                photos.get('items', []),
                key=lambda x: x.get('likes', {}).get('count', 0),
                reverse=True
            )
            
            return [
                {
                    'url': photo['sizes'][-1]['url'],
                    'likes': photo['likes']['count'],
                    'id': photo['id']
                }
                for photo in sorted_photos[:3]
            ]
        except Exception as e:
            print(f"Ошибка получения фото: {e}")
            return []