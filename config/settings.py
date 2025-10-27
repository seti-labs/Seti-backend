import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///seti.db')
    # Supabase provides postgres:// URLs, but SQLAlchemy needs postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
    # Supabase
    SUPABASE_URL = os.getenv('SUPABASE_URL', '')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY', '')
    
    # Base Blockchain
    BASE_NETWORK = os.getenv('BASE_NETWORK', 'sepolia')
    BASE_RPC_URL = os.getenv('BASE_RPC_URL', 'https://base-sepolia.api.onfinality.io/public')
    PREDICTION_MARKET_CONTRACT_ADDRESS = os.getenv('PREDICTION_MARKET_CONTRACT_ADDRESS', '0x63c0c19a282a1B52b07dD5a65b58948a07DAE32B')
    
    # CORS - Allow all origins for now, restrict in production
    # Include Seti frontend domains
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'https://seti-backend.onrender.com,https://seti-live.vercel.app,https://seti-mvp.vercel.app,http://localhost:3000,http://localhost:5173,http://localhost:8080').split(',') if os.getenv('CORS_ORIGINS') != '*' else '*'
    
    # Caching
    CACHE_TYPE = 'redis' if os.getenv('REDIS_URL') else 'simple'
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT = 300
    
    # API Settings
    API_TITLE = 'Seti Prediction Market API'
    API_VERSION = 'v1'
    
    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

