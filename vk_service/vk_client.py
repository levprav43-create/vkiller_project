import vk_api
from vk_api.utils import get_random_id
import json
import time


class VKClient:
    """Клиент для работы с VK API."""

    def __init__(self):
        self.version = '5.131'
        self.vk = None

    def init_session(self, token: str):
        """Инициализация сессии VK."""
        self.vk = vk_api.VkApi(token=token)

    def get_user_info(self, user_id: int) -> dict:
        """Получить информацию о пользователе."""
        try:
            response = self.vk.method('users.get', {
                'user_ids': user_id,
                'fields': 'city,age,sex,photo_max',
                'v': self.version
            })
            if response:
                user = response[0]
                return {
                    'first_name': user.get('first_name', ''),
                    'last_name': user.get('last_name', ''),
                    'city': user.get('city', {}),
                    'age': user.get('age'),
                    'sex': user.get('sex'),
                    'photo': user.get('photo_max', '')
                }
        except vk_api.exceptions.ApiError as e:
            print(f"VK API Error (get_user_info): {e}")
        return {}

    def search_users(self, age: int, sex: int, city: str = '',
                     count: int = 100) -> list:
        """Поиск пользователей с обходом лимита 1000."""
        all_candidates = []
        offset = 0
        max_pages = 10

        age_from = max(18, age - 5)
        age_to = age + 10

        for page in range(max_pages):
            try:
                params = {
                    'age_from': age_from,
                    'age_to': age_to,
                    'sex': sex,
                    'has_photo': 1,
                    'count': min(count, 100),
                    'offset': offset,
                    'v': self.version
                }

                if city:
                    params['city'] = city

                response = self.vk.method('users.search', params)

                if not response or 'items' not in response:
                    break

                all_candidates.extend(response['items'])
                offset += 100

                if len(response['items']) < 100:
                    break

                time.sleep(0.3)

            except vk_api.exceptions.ApiError as e:
                print(f"VK API Error (search_users): {e}")
                break

        return all_candidates

    def get_user_photos(self, user_id: int, count: int = 3) -> list:
        """Получить фото (аватарки + стена) сортированные по лайкам."""
        all_photos = []

        try:
            response = self.vk.method('photos.get', {
                'owner_id': user_id,
                'album_id': 'profile',
                'extended': 1,
                'count': 50,
                'v': self.version
            })
            if response and 'items' in response:
                all_photos.extend(response['items'])
        except vk_api.exceptions.ApiError as e:
            print(f"VK API Error (profile photos): {e}")

        try:
            response = self.vk.method('photos.getWall', {
                'owner_id': user_id,
                'extended': 1,
                'count': 50,
                'v': self.version
            })
            if response and 'items' in response:
                all_photos.extend(response['items'])
        except vk_api.exceptions.ApiError as e:
            print(f"VK API Error (wall photos): {e}")

        photos = sorted(
            all_photos,
            key=lambda x: x.get('likes', {}).get('count', 0),
            reverse=True
        )[:count]

        return [
            p.get('photo_807') or p.get('photo_604')
            for p in photos
            if p.get('photo_807') or p.get('photo_604')
        ]

    def send_message(self, peer_id: int, text: str):
        """Отправить текстовое сообщение."""
        try:
            self.vk.method('messages.send', {
                'peer_id': peer_id,
                'message': text,
                'random_id': get_random_id(),
                'v': self.version
            })
        except vk_api.exceptions.ApiError as e:
            print(f"VK API Error (send_message): {e}")

    def send_message_with_buttons(self, peer_id: int, text: str,
                                   buttons: list):
        """Отправить сообщение с inline-кнопками."""
        keyboard = {
            'one_time': False,
            'inline': True,
            'buttons': buttons
        }

        try:
            self.vk.method('messages.send', {
                'peer_id': peer_id,
                'message': text,
                'keyboard': json.dumps(keyboard),
                'random_id': get_random_id(),
                'v': self.version
            })
        except vk_api.exceptions.ApiError as e:
            print(f"VK API Error (send_with_buttons): {e}")

    def like_photo(self, owner_id: int, photo_id: int) -> bool:
        """Поставить лайк на фото."""
        try:
            self.vk.method('likes.add', {
                'type': 'photo',
                'owner_id': owner_id,
                'item_id': photo_id,
                'v': self.version
            })
            return True
        except vk_api.exceptions.ApiError as e:
            print(f"VK API Error (like_photo): {e}")
            return False

    def get_user_interests(self, user_id: int) -> dict:
        """Получить интересы пользователя (группы, музыка)."""
        interests = {'groups': [], 'music': []}

        try:
            response = self.vk.method('groups.get', {
                'user_id': user_id,
                'extended': 0,
                'count': 50,
               