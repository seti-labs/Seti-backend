"""
Enhanced configuration with security settings
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration with enhanced security"""
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
    
    # Enhanced CORS Configuration - Restrict in production
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'https://seti-backend.onrender.com,https://setilive.vercel.app,https://seti-mvp.vercel.app,http://localhost:3000,http://localhost:5173,http://localhost:8080').split(',') if os.getenv('CORS_ORIGINS') != '*' else ['http://localhost:3000', 'http://localhost:5173']
    
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
    
    # Security Settings
    SECURITY_HEADERS = True
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW = 3600  # 1 hour
    BLOCK_SUSPICIOUS_REQUESTS = True
    CORS_STRICT = True
    
    # Admin Authentication
    ADMIN_KEY = os.getenv('ADMIN_KEY', 'admin-secret-key-change-in-production')
    
    # JWT Settings (for future implementation)
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # External API Keys
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', '')
    
    # File Upload Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    
    # Relaxed security for development
    RATE_LIMIT_REQUESTS = 1000
    BLOCK_SUSPICIOUS_REQUESTS = False
    CORS_STRICT = False

class ProductionConfig(Config):
    """Production configuration with strict security"""
    DEBUG = False
    TESTING = False
    
    # Strict security settings
    RATE_LIMIT_REQUESTS = 50
    RATE_LIMIT_WINDOW = 3600
    BLOCK_SUSPICIOUS_REQUESTS = True
    CORS_STRICT = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    
    # Disable security features for testing
    RATE_LIMIT_ENABLED = False
    BLOCK_SUSPICIOUS_REQUESTS = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}