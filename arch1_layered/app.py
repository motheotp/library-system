from flask import Flask
from flask_cors import CORS
from config import config
from models import db
from services import (CacheService, UserService, BookService, 
                     BorrowingService, ReservationService, StatisticsService)
from routes import create_routes
import os

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Initialize Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Enable CORS
    CORS(app)
    
    # Initialize database
    db.init_app(app)
    
    # Initialize services
    cache_service = CacheService(app.config)
    user_service = UserService(cache_service)
    book_service = BookService(cache_service)
    borrowing_service = BorrowingService(cache_service, user_service, book_service)
    reservation_service = ReservationService(cache_service)
    statistics_service = StatisticsService(cache_service)
    
    # Create and register routes
    api_blueprint = create_routes(
        user_service=user_service,
        book_service=book_service,
        borrowing_service=borrowing_service,
        reservation_service=reservation_service,
        statistics_service=statistics_service
    )
    
    app.register_blueprint(api_blueprint)
    
    return app

# Create app instance at module level for WSGI servers (gunicorn, etc.)
app = create_app()

if __name__ == '__main__':
    # Run the application directly (for development)
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )