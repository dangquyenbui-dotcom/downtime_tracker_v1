"""
Downtime entry routes
Placeholder implementation
"""

from flask import Blueprint, render_template, redirect, url_for, session, flash
from auth import require_login
from routes.main import validate_session

downtime_bp = Blueprint('downtime', __name__)

@downtime_bp.route('/downtime')
@validate_session
def entry_form():
    if not require_login(session):
        return redirect(url_for('main.login'))
    
    return "<h1>Report Downtime</h1><p>Downtime form coming soon...</p><a href='/dashboard'>Back to Dashboard</a>"

@downtime_bp.route('/reports')
@validate_session
def reports():
    if not require_login(session):
        return redirect(url_for('main.login'))
    
    return "<h1>Reports</h1><p>Reports coming soon...</p><a href='/dashboard'>Back to Dashboard</a>"
