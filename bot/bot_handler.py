class BotHandler:
    def __init__(self, vk_client, db_session):
        self.vk = vk_client
        self.db = db_session
    
    def handle_message(self, event):
        """Обработчик сообщений"""
        user_id = event.obj['from_id']
        text = event.obj['text'].strip().lower()
        
        if text in ['начать', 'start', '/start']:
            return "🔍 Привет! Начинаю поиск пары...\nНапиши 'далее' для следующего кандидата"
        elif text == 'далее':
            return "👤 Показываю следующего кандидата..."
        elif text == 'избранное':
            return "⭐ Ваш список избранного"
        
        return "Напишите /начать для поиска пары 💕"