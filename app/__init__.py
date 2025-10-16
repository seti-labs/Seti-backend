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
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Register blueprints
    from app.api import markets, predictions, users, analytics, comments
    app.register_blueprint(markets.bp, url_prefix='/api/v1/markets')
    app.register_blueprint(predictions.bp, url_prefix='/api/v1/predictions')
    app.register_blueprint(users.bp, url_prefix='/api/v1/users')
    app.register_blueprint(analytics.bp, url_prefix='/api/v1/analytics')
    app.register_blueprint(comments.bp, url_prefix='/api/v1/comments')
    
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
    
    return app

