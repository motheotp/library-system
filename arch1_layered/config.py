import os
from pickle import TRUE
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DATABASE_URL = os.getenv()
    SQLALCHEMY_DATABASE_URI = DATABASE_URL

    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))

    ITEMS_PER_PAGE = int(os.getenv('ITEMS_PER_PAGE', 10))
    MAX_BORROWING_LIMIT = int(os.getenv('MAX_BORROWING_LIMIT', 3))
    LOAN_PERIOD_DAYS = int(os.getenv('LOAN_PERIOD_DAYS', 14))
    CACHE_EXPIRY_SECONDS = int(os.getenv('CACHE_EXPIRY_SECONDS', 300))

class DevelopmentConfig(Config):
    DEBUG=TRUE
    FLASK_ENV='development'

class ProductionConfig(Config):
    DEBUG=False
    FLASK_ENV='production'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}