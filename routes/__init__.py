"""
Routes package initialization
All route blueprints are imported and registered in app.py
"""

# This file can remain empty as blueprints are imported directly in app.py
# Or you can import all blueprints here for convenience:

from .main import main_bp
from .downtime import downtime_bp

__all__ = ['main_bp', 'downtime_bp']