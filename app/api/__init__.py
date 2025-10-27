# API Blueprint initialization

from app.api.games import games_bp
from app.api.markets import bp as markets_bp
from app.api.predictions import bp as predictions_bp
from app.api.users import bp as users_bp
from app.api.analytics import bp as analytics_bp
from app.api.comments import bp as comments_bp
from app.api.favorites import bp as favorites_bp
from app.api.admin import bp as admin_bp
from app.api.prediction_tracking import bp as prediction_tracking_bp
from app.api import games

__all__ = ['games']
