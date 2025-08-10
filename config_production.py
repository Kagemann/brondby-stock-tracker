import os
from dotenv import load_dotenv

load_dotenv()

class ProductionConfig:
    # API Keys
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
    
    # Stock Configuration
    STOCK_SYMBOL = 'BIF.CO'
    STOCK_NAME = 'Brøndby IF'
    
    # Database - Use PostgreSQL in production
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./brondby_tracker.db')
    
    # News Sources
    NEWS_SOURCES = [
        'brondby.com',
        'superliga.dk',
        'tipsbladet.dk',
        'bold.dk',
        'ekstrabladet.dk',
        'bt.dk'
    ]
    
    # Keywords for news filtering
    NEWS_KEYWORDS = [
        'brøndby',
        'brondby',
        'brøndby if',
        'brondby if',
        'brøndby stadion',
        'brondby stadion',
        'superliga',
        'danish football',
        'danish soccer'
    ]
    
    # Data Collection Settings
    STOCK_UPDATE_INTERVAL = 300  # 5 minutes
    NEWS_UPDATE_INTERVAL = 1800  # 30 minutes
    SENTIMENT_UPDATE_INTERVAL = 3600  # 1 hour
    
    # Alert Settings
    PRICE_CHANGE_THRESHOLD = 0.05  # 5% price change
    SENTIMENT_THRESHOLD = 0.3  # Sentiment score threshold
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'brondby_tracker.log'
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
