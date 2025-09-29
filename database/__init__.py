"""
Database package initialization
Provides centralized access to all database modules
"""

from .connection import DatabaseConnection, get_db
from .facilities import FacilitiesDB
from .production_lines import ProductionLinesDB
from .categories import CategoriesDB
from .downtimes import DowntimesDB
from .audit import AuditDB
from .shifts import ShiftsDB
from .users import UsersDB
from .sessions import SessionsDB  # Add this

# Create singleton instances
facilities_db = FacilitiesDB()
lines_db = ProductionLinesDB()
categories_db = CategoriesDB()
downtimes_db = DowntimesDB()
audit_db = AuditDB()
shifts_db = ShiftsDB()
users_db = UsersDB()
sessions_db = SessionsDB()  # Add this

# Export main database functions
__all__ = [
    'DatabaseConnection',
    'get_db',
    'facilities_db',
    'lines_db',
    'categories_db',
    'downtimes_db',
    'audit_db',
    'shifts_db',
    'users_db',
    'sessions_db'  # Add this
]