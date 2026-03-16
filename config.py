from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    # VK
    VK_TOKEN = os.getenv('VK_TOKEN')
    VK_VERSION = os.getenv('VK_VERSION', '5.131')
    VK_GROUP_ID = os.getenv('VK_GROUP_ID')
    
    # Database
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'vkiller_db')
    
    # Bot
    BOT_PREFIX = os.getenv('BOT_PREFIX', '/')