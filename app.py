"""
Downtime Tracker - Main Application
Clean, modular structure with proper separation of concerns
"""

from flask import Flask
import os
from datetime import timedelta
from config import Config

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = Config.SECRET_KEY
    app.permanent_session_lifetime = timedelta(hours=Config.SESSION_HOURS)
    
    # Configure static files path
    app.static_folder = 'static'
    app.static_url_path = '/static'
    
    # Register blueprints
    register_blueprints(app)
    
    # Initialize database
    initialize_database()
    
    return app

def register_blueprints(app):
    """Register all application blueprints"""
    from routes.main import main_bp
    from routes.downtime import downtime_bp
    from routes.admin.panel import admin_panel_bp
    from routes.admin.facilities import admin_facilities_bp
    from routes.admin.production_lines import admin_lines_bp
    from routes.admin.categories import admin_categories_bp
    from routes.admin.audit import admin_audit_bp
    from routes.admin.shifts import admin_shifts_bp
    from routes.admin.users import admin_users_bp
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(downtime_bp)
    app.register_blueprint(admin_panel_bp, url_prefix='/admin')
    app.register_blueprint(admin_facilities_bp, url_prefix='/admin')
    app.register_blueprint(admin_lines_bp, url_prefix='/admin')
    app.register_blueprint(admin_categories_bp, url_prefix='/admin')
    app.register_blueprint(admin_audit_bp, url_prefix='/admin')
    app.register_blueprint(admin_shifts_bp, url_prefix='/admin')
    app.register_blueprint(admin_users_bp, url_prefix='/admin')

def initialize_database():
    """Initialize database connection and verify tables"""
    from database.connection import DatabaseConnection
    
    db = DatabaseConnection()
    if db.test_connection():
        print("✅ Database: Connected and ready!")
    else:
        print("❌ Database: Connection failed!")
        print("   Run database initialization script")
    
def test_services():
    """Test all service connections on startup"""
    print("\n" + "="*60)
    print("DOWNTIME TRACKER v1 - STARTUP DIAGNOSTICS")
    print("="*60)
    
    # Test Database
    from database.connection import DatabaseConnection
    db = DatabaseConnection()
    if db.test_connection():
        print("✅ Database: Connected")
    else:
        print("❌ Database: Not connected")
    
    # Test AD (if not in test mode)
    if not Config.TEST_MODE:
        from auth.ad_auth import test_ad_connection
        if test_ad_connection():
            print("✅ Active Directory: Connected")
        else:
            print("❌ Active Directory: Not connected")
    else:
        print("🧪 Test Mode: Using fake authentication")
    
    print("="*60 + "\n")

if __name__ == '__main__':
    # Create required directories
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Display configuration
    print("\n" + "="*50)
    print("DOWNTIME TRACKER v1 - CONFIGURATION")
    print("="*50)
    print(f"Mode: {'TEST' if Config.TEST_MODE else 'PRODUCTION'}")
    print(f"Database: {Config.DB_SERVER}/{Config.DB_NAME}")
    print(f"AD Domain: {Config.AD_DOMAIN}")
    print("="*50 + "\n")
    
    # Test connections
    test_services()
    
    # Create and run app
    app = create_app()
    
    print(f"🚀 Starting server at: http://localhost:5000")
    print("Press CTRL+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)