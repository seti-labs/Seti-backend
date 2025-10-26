from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from config.settings import config

db = SQLAlchemy()
migrate = Migrate()
cache = Cache()

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    # Configure CORS
    if app.config['CORS_ORIGINS'] == '*':
        CORS(app, origins='*')
    else:
        CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Register blueprints
    from app.api import markets, predictions, users, analytics, comments, favorites, admin, games
    app.register_blueprint(markets.bp, url_prefix='/api/v1/markets')
    app.register_blueprint(predictions.bp, url_prefix='/api/v1/predictions')
    app.register_blueprint(users.bp, url_prefix='/api/v1/users')
    app.register_blueprint(analytics.bp, url_prefix='/api/v1/analytics')
    app.register_blueprint(comments.bp, url_prefix='/api/v1/comments')
    app.register_blueprint(favorites.bp, url_prefix='/api/v1/favorites')
    app.register_blueprint(admin.bp, url_prefix='/api/v1/admin')
    app.register_blueprint(games.games_bp, url_prefix='/api/v1')
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'service': 'seti-backend'}, 200
    
    @app.route('/')
    def index():
        return {
            'name': app.config['API_TITLE'],
            'version': app.config['API_VERSION'],
            'status': 'running'
        }, 200
    
    # Initialize sync services
    def initialize_services():
        """Initialize sync services on first request"""
        try:
            from app.services.sync_scheduler import sync_scheduler
            from app.services.event_listener import event_listener
            
            # Start sync scheduler (only in production or when explicitly enabled)
            if app.config.get('ENABLE_AUTO_SYNC', False):
                sync_scheduler.start()
                event_listener.start_listening()
                print("Auto-sync services started")
            else:
                print("Auto-sync services disabled (set ENABLE_AUTO_SYNC=true to enable)")
                
        except Exception as e:
            print(f"Error initializing sync services: {e}")
    
    # Initialize services immediately (Flask 2.3+ compatible)
    initialize_services()
    
    return app

