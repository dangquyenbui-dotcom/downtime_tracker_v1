# routes/downtime.py - Complete implementation

"""
Downtime entry routes - FULL IMPLEMENTATION
iPad-optimized interface for production floor use
"""

from flask import Blueprint, render_template, redirect, url_for, session, flash, jsonify, request
from auth import require_login
from routes.main import validate_session
from database import facilities_db, lines_db, categories_db, downtimes_db, shifts_db
from utils import get_client_info
from datetime import datetime

downtime_bp = Blueprint('downtime', __name__)

@downtime_bp.route('/downtime')
@validate_session
def entry_form():
    """Display the downtime entry form"""
    if not require_login(session):
        return redirect(url_for('main.login'))
    
    # Get data for dropdowns
    facilities = facilities_db.get_all(active_only=True)
    lines = lines_db.get_all(active_only=True)
    categories = categories_db.get_hierarchical(active_only=True)
    shifts = shifts_db.get_all(active_only=True)
    
    # Auto-detect current shift
    current_time = datetime.now()
    current_shift = None
    
    for shift in shifts:
        start_time = datetime.strptime(shift['start_time'], '%H:%M').time()
        end_time = datetime.strptime(shift['end_time'], '%H:%M').time()
        
        if shift.get('is_overnight'):
            # Overnight shift
            if current_time.time() >= start_time or current_time.time() < end_time:
                current_shift = shift
                break
        else:
            # Regular shift
            if start_time <= current_time.time() < end_time:
                current_shift = shift
                break
    
    # Get recent entries by this user for reference
    recent_entries = downtimes_db.get_recent(days=1, limit=5)
    user_recent = [e for e in recent_entries if e['entered_by'] == session['user']['username']]
    
    return render_template('downtime/entry.html',
                         facilities=facilities,
                         lines=lines,
                         categories=categories,
                         shifts=shifts,
                         current_shift=current_shift,
                         recent_entries=user_recent[:3],
                         user=session['user'])

@downtime_bp.route('/downtime/submit', methods=['POST'])
@validate_session
def submit_downtime():
    """Submit a new downtime entry"""
    if not require_login(session):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        # Get form data
        facility_id = request.form.get('facility_id')
        line_id = request.form.get('line_id')
        category_id = request.form.get('category_id')
        shift_id = request.form.get('shift_id')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        crew_size = request.form.get('crew_size', '1')
        reason_notes = request.form.get('comments', '').strip()
        
        # Validate required fields
        if not all([facility_id, line_id, category_id, start_time, end_time]):
            return jsonify({'success': False, 'message': 'All required fields must be filled'})
        
        # Validate crew size
        try:
            crew_size = int(crew_size)
            if crew_size < 1 or crew_size > 10:
                return jsonify({'success': False, 'message': 'Crew size must be between 1 and 10'})
        except ValueError:
            return jsonify({'success': False, 'message': 'Crew size must be a number'})
        
        # Create downtime entry
        data = {
            'line_id': line_id,
            'category_id': category_id,
            'shift_id': shift_id,
            'start_time': start_time,
            'end_time': end_time,
            'crew_size': crew_size,
            'reason_notes': reason_notes,
            'entered_by': session['user']['username']
        }
        
        success, message, downtime_id = downtimes_db.create(data)
        
        if success:
            # Log in audit
            from database import audit_db
            ip, user_agent = get_client_info()
            audit_db.log(
                table_name='Downtimes',
                record_id=downtime_id,
                action_type='INSERT',
                username=session['user']['username'],
                ip=ip,
                user_agent=user_agent,
                notes=f"Downtime reported for line {line_id}"
            )
            
            return jsonify({
                'success': True,
                'message': 'Downtime entry submitted successfully!',
                'downtime_id': downtime_id
            })
        else:
            return jsonify({'success': False, 'message': message})
        
    except Exception as e:
        print(f"Error submitting downtime: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred while submitting'})

@downtime_bp.route('/downtime/api/lines/<int:facility_id>')
@validate_session
def get_facility_lines(facility_id):
    """API endpoint to get lines for a specific facility"""
    if not require_login(session):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    lines = lines_db.get_by_facility(facility_id, active_only=True)
    return jsonify({
        'success': True,
        'lines': [{'id': l['line_id'], 'name': l['line_name']} for l in lines]
    })

@downtime_bp.route('/downtime/api/subcategories/<int:parent_id>')
@validate_session
def get_subcategories(parent_id):
    """API endpoint to get subcategories for a main category"""
    if not require_login(session):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    categories = categories_db.get_all(active_only=True)
    subcategories = [c for c in categories if c.get('parent_id') == parent_id]
    
    return jsonify({
        'success': True,
        'subcategories': [{'id': c['category_id'], 'name': c['category_name'], 'code': c['category_code']} 
                         for c in subcategories]
    })