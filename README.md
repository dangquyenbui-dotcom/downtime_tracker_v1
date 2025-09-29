# Downtime Tracker - Notes for Claude

## What This Is
Manufacturing downtime tracking system with single-session enforcement. Users log when production lines stop, categorize why, track duration. Flask + SQL Server + Active Directory.

## Current State
**Version 1.3.3** - Complete with single-session enforcement. All admin features complete. Downtime entry itself is placeholder. Reports not implemented.

### Recent Fixes (v1.3.3)
- ✅ Implemented single-session enforcement (users can only login from one location)
- ✅ Added session conflict detection with clear warnings
- ✅ Applied session validation to all protected routes
- ✅ Created ActiveSessions table for tracking user sessions
- ✅ Added automatic session cleanup for expired sessions
- ✅ Improved security with IP and user agent tracking

### Previous Fixes (v1.3.2)
- ✅ Fixed VS Code CSS parsing errors in categories template
- ✅ Separated Jinja2 syntax from inline styles using data attributes
- ✅ Added JavaScript-based color application for dynamic styling
- ✅ Improved template compatibility with code editors

### Previous Fixes (v1.3.1)
- ✅ Fixed SQL Server 2012 compatibility (removed STRING_AGG dependency)
- ✅ Fixed database connection persistence (no more constant reconnection messages)
- ✅ Fixed category filter to properly hide inactive subcategories
- ✅ Fixed expand arrows to only show for categories with subcategories

## System Requirements
- Python 3.7+
- SQL Server 2012 or later (2012, 2014, 2016, 2019, 2022)
- Active Directory (optional - can use TEST_MODE)
- Windows or Linux server

## How to Navigate This Codebase

### Start Here
- `app.py` - Entry point, all blueprints registered here
- `.env` - Config (TEST_MODE=True bypasses AD)
- `database/__init__.py` - All DB modules exported as singletons

### Core Flow
1. User hits `/login` → `routes/main.py`
2. Auth via `auth/ad_auth.py` (or test mode)
3. **NEW**: Session validated/created in `database/sessions.py`
4. Session created with unique ID and tracked in database
5. All routes protected with `@validate_session` decorator
6. Dashboard shows based on role
7. Admin gets `/admin` access

## Key Things to Remember

### Single-Session Enforcement (NEW in v1.3.3)
- Users can only be logged in from one location at a time
- Attempting to login from a second location shows a warning
- Users can choose to force login, which ends their other session
- All sessions tracked in `ActiveSessions` table with IP and timestamp
- Sessions auto-expire after configured timeout (default 8 hours)

### Database Pattern
Every module in `database/` follows same pattern:
```python
# They're all singletons with persistent connections
from database import facilities_db, lines_db, categories_db, sessions_db

# Standard operations
success, message, record_id = module_db.create(...)
records = module_db.get_all(active_only=True)
success, message = module_db.deactivate(id, username)
```

### Session Management (NEW)
```python
# Session validation decorator on all protected routes
@validate_session
def protected_route():
    # Automatically validates session on each request
    pass

# Session operations in database/sessions.py
sessions_db.create_session(session_id, username, ip, user_agent)
sessions_db.validate_session(session_id, username)
sessions_db.end_session(session_id)
```

### NEVER Hard Delete
Everything uses soft delete (`is_active=0` or `is_deleted=1`). Can reactivate.

### Audit Everything
Every CUD operation logs to AuditLog with field-level changes:
```python
audit_db.log(
    table_name='Whatever',
    record_id=id,
    action_type='INSERT|UPDATE|DEACTIVATE|REACTIVATE',
    changes={'field': {'old': 'x', 'new': 'y'}}
)
```

### Frontend Patterns
- Theme: CSS variables + `data-theme` attribute (true black OLED mode)
- Modals: `dtUtils.openModal('id')` / `dtUtils.closeModal('id')`  
- Forms: Always `e.preventDefault()` then `dtUtils.submitForm()`
- Alerts: `dtUtils.showAlert(message, 'success|error')`
- No localStorage for sensitive data
- **Dynamic Styles**: Use data attributes + JavaScript, not inline Jinja2 (v1.3.2)

### Template Best Practices (v1.3.2)
- **Never mix Jinja2 with inline styles** - Causes VS Code CSS parsing errors
- Use `data-*` attributes for dynamic values: `data-color="{{ value }}"`
- Apply dynamic styles via JavaScript: `element.style.property = element.dataset.value`
- Set CSS defaults for all dynamic properties
- Use CSS classes instead of inline style manipulation where possible

## Database Structure

### Hierarchy
```
Facilities (buildings)
  └── ProductionLines (equipment in buildings)
        └── Downtimes (events that happened)
              ├── DowntimeCategories (why it happened)
              └── Shifts (when it happened)

UserLogins tracks all user sessions
AuditLog tracks all changes
ActiveSessions tracks current user sessions (NEW)
```

### ActiveSessions Table (NEW in v1.3.3)
```sql
CREATE TABLE ActiveSessions (
    session_id NVARCHAR(100) PRIMARY KEY,
    username NVARCHAR(100) NOT NULL,
    login_date DATETIME NOT NULL,
    last_activity DATETIME NOT NULL,
    ip_address NVARCHAR(50),
    user_agent NVARCHAR(500),
    is_active BIT DEFAULT 1
);
```

### Categories are Hierarchical
- Main: 2 letters (EQ = Equipment)
- Sub: 2 letters + 2 numbers (EQ01 = Motor Failure)
- Parent must be active to reactivate child
- Expand arrows only show for categories with subcategories
- Colors applied via data attributes (v1.3.2)

## Current Features Status

### ✅ Complete (v1.3.3)
- **Single-session enforcement** (NEW)
- **Session conflict detection and resolution** (NEW)
- **Session tracking with IP and user agent** (NEW)
- Facilities management
- Production lines management  
- Hierarchical categories with colors
- Shift management (detects overnight shifts)
- User activity tracking with login history
- Audit log with field-level tracking
- Theme system (light/dark/OLED black)
- SQL Server 2012+ compatibility
- Persistent database connections
- Smart category filtering
- VS Code compatible templates

### ⏳ Placeholder
- `/downtime` - Form to enter downtime (routes/downtime.py)
- `/reports` - View reports

### 🔧 Test Mode
Set `TEST_MODE=True` in .env:
- Bypasses AD completely
- Login: `test/test` (user) or `test1/test1` (admin)
- Perfect for development and testing

## Common Tasks

### Testing Single-Session Enforcement (NEW)
1. Login in Browser A
2. Try to login in Browser B with same credentials
3. You'll see a warning about existing session
4. Can choose to continue (ends Browser A session) or cancel
5. If continued, Browser A will be logged out on next action

### Add New Admin Module
1. Create `database/newmodule.py` (copy pattern from facilities.py)
2. Create `routes/admin/newmodule.py` (copy pattern from facilities.py)
3. Create `templates/admin/newmodule.html` (copy pattern)
4. Register in `app.py`: `app.register_blueprint()`
5. Add to `database/__init__.py` exports
6. Add card in `templates/admin/panel.html`
7. **NEW**: Add `@validate_session` decorator to all routes

### Debug Database Issues
1. Check connection: `/status` page (admin only)
2. Connection lives in `database/connection.py`
3. Uses persistent connection with auto-reconnect
4. Falls back to ODBC Driver 17 if SQL Server driver fails
5. Check for "No active database connection" messages in console

### Fix Modal Issues
Problem usually in the onclick handler. Pattern should be:
```html
onclick="openEditModal({{ id }}, '{{ name }}', '{{ value or '' }}')"
```
Note the `or ''` for nullable fields!

### Fix Template CSS Parsing Errors (v1.3.2)
VS Code shows CSS errors when Jinja2 is in styles:
```html
<!-- DON'T DO THIS - Causes parsing errors -->
<div style="background-color: {{ color }}"></div>

<!-- DO THIS INSTEAD -->
<div data-color="{{ color }}"></div>
<script>
element.style.backgroundColor = element.dataset.color;
</script>
```

## Gotchas & Solutions

### Session Management (NEW in v1.3.3)
- **Single session only**: Users cannot be logged in from multiple locations
- **Session conflicts**: System detects and warns about existing sessions
- **Force logout**: Users can force login, ending their other session
- **Session timeout**: Sessions expire after 8 hours (configurable)

### JavaScript String Escaping
When passing data to onclick, watch for quotes in strings. The `or ''` pattern prevents null issues.

### Theme No-Flash
Theme applied before render via inline script in base.html. Don't move it.

### Database Connection
- Connection persists across requests (performance improvement)
- Auto-reconnects if connection dies
- Test with `SELECT 1` before each operation
- No more "Attempting to reconnect..." spam

### Category Reactivation  
Must check parent is active first. Logic in `categories_db.reactivate()`.

### Overnight Shifts
If end_time < start_time, it's overnight. Duration = 24 - start_hour + end_hour.

### SQL Server Compatibility
- Works with SQL Server 2012 and later
- No STRING_AGG (2017+ function) - uses CASE statements instead
- Compatible with both Windows Auth and SQL Auth
- Automatic driver fallback (SQL Server → ODBC Driver 17)

### Template Compatibility (v1.3.2)
- VS Code and other editors parse CSS strictly
- Jinja2 in inline styles breaks CSS parsing
- Solution: data attributes + JavaScript application
- All dynamic colors use `data-color` pattern

## Troubleshooting

### "Your session has expired or you logged in from another location"
- **NEW in v1.3.3**: This means you logged in from another browser/computer
- Your previous session was ended when you logged in elsewhere
- This is normal behavior to prevent multiple simultaneous logins

### "No active database connection. Attempting to reconnect..."
- **Fixed in v1.3.1**: Database connection now persists
- If still seeing: Check SQL Server is running and accessible

### Categories filter not working
- **Fixed in v1.3.1**: Filter now properly hides inactive items on page load
- Active/Inactive filter applies to both main and subcategories

### User Management page errors
- **Fixed in v1.3.1**: Removed STRING_AGG for SQL Server 2012 compatibility
- If "STRING_AGG is not a recognized built-in function": Update to latest users.py

### Expand arrows showing for all categories
- **Fixed in v1.3.1**: Arrows only show for categories with subcategories
- Empty space maintains alignment for categories without children

### VS Code showing CSS parsing errors in templates
- **Fixed in v1.3.2**: Separated Jinja2 from inline styles
- Used data attributes for dynamic values
- Applied styles via JavaScript instead of inline

## File Quick Reference

### Routes
- `routes/main.py` - Login, dashboard, logout, status (with session management)
- `routes/admin/*.py` - All admin pages (all protected with `@validate_session`)
- `routes/downtime.py` - Placeholder for downtime entry

### Templates  
- `templates/base.html` - Has navbar, theme toggle, container
- `templates/login.html` - Standalone with session conflict handling
- `templates/admin/*.html` - All extend base.html
- `templates/admin/categories.html` - Uses data attributes for dynamic colors

### Static
- `static/js/common.js` - dtUtils namespace (alerts, modals, forms)
- `static/js/theme.js` - Theme management
- `static/css/base.css` - CSS variables, theme definitions
- `static/css/admin.css` - Admin-specific styles

### Database Modules
All in `database/` folder, all follow same CRUD pattern, all are singletons with persistent connections.
- **NEW**: `database/sessions.py` - Active session management

## SQL Tables Summary

```sql
Facilities (facility_id, facility_name, location, is_active)
ProductionLines (line_id, facility_id, line_name, line_code, is_active)  
DowntimeCategories (category_id, parent_id, category_name, category_code, color_code, is_active)
Downtimes (downtime_id, line_id, category_id, shift_id, start_time, end_time, duration_minutes, is_deleted)
Shifts (shift_id, shift_name, shift_code, start_time, end_time, is_overnight, is_active)
UserLogins (login_id, username, login_date, ip_address, is_admin)
AuditLog (audit_id, table_name, record_id, action_type, old_value, new_value, changed_by)
ActiveSessions (session_id, username, login_date, last_activity, ip_address, user_agent, is_active) -- NEW
```

## Environment Variables (.env)
```env
# Core Settings
TEST_MODE=False
SECRET_KEY=your-secret-key

# Database (SQL Server 2012+)
DB_SERVER=your-sql-server
DB_NAME=ProductionDB
DB_USE_WINDOWS_AUTH=False
DB_USERNAME=db_user
DB_PASSWORD=db_password

# Active Directory
AD_DOMAIN=DOMAIN.LOCAL
AD_SERVER=your-dc.domain.local
AD_PORT=389
AD_BASE_DN=DC=domain,DC=local
AD_SERVICE_ACCOUNT=service_account
AD_SERVICE_PASSWORD=service_password
AD_ADMIN_GROUP=DowntimeTracker_Admin
AD_USER_GROUP=DowntimeTracker_User

# Session
SESSION_HOURS=8  # Sessions expire after 8 hours

# Email (optional)
SMTP_SERVER=mail.local
SMTP_PORT=587
SMTP_USE_TLS=True
EMAIL_FROM=downtime@local
```

## Next Development Steps
1. **Priority**: Implement actual downtime entry form
2. Build reports/analytics dashboard
3. Add email notifications for critical categories
4. Excel export functionality
5. REST API for integration
6. Mobile-responsive downtime entry
7. **Future**: Admin panel for viewing/managing active sessions

## Version History

### v1.3.3 (Current) - Single-Session Enforcement
- Implemented single-session enforcement
- Added session conflict detection and warnings
- Applied session validation to all protected routes
- Created ActiveSessions table for tracking
- Enhanced security with IP and user agent tracking
- Improved user experience with clear messaging

### v1.3.2 - Template Compatibility Fix
- Fixed VS Code CSS parsing errors in categories template
- Separated Jinja2 syntax from inline styles
- Implemented data attribute pattern for dynamic styling
- Added JavaScript-based style application
- Improved code editor compatibility

### v1.3.1 - Bug Fixes & Optimization
- Fixed SQL Server 2012 compatibility issues
- Implemented persistent database connections
- Fixed category filtering on page load
- Fixed expand arrows for categories
- Improved overall performance

### v1.3 - User & Shift Management
- Complete shift management system
- User activity tracking
- Login monitoring
- CSV export functionality
- Enhanced audit trail

### v1.2 - Stability Improvements
- Category reactivation
- Enhanced error handling
- Dashboard improvements

### v1.1 - Categories Enhancement
- Hierarchical categories
- Color coding
- Notification settings

### v1.0 - Initial Release
- Basic facilities and production lines
- Simple audit logging

## Performance Notes
- Database connection persists (no reconnection overhead)
- Indexed columns for common queries
- Client-side table filtering (no server round-trip)
- Theme persistence without server involvement
- Minimal JavaScript dependencies
- Dynamic styles via data attributes (v1.3.2)
- **NEW**: Session validation adds ~5ms per request (minimal overhead)

## Security Enhancements (v1.3.3)
- **Single-session enforcement** prevents credential sharing
- **Session tracking** with IP and user agent
- **Automatic session cleanup** after timeout
- **Session conflict detection** with user choice
- **Audit trail** of all login events and sessions
- **Protected routes** with `@validate_session` decorator

## Code Quality Standards
- **Templates**: No Jinja2 in inline styles
- **JavaScript**: Use data attributes for dynamic values
- **CSS**: Provide defaults for all dynamic properties
- **Python**: Follow singleton pattern for DB modules
- **Security**: Never store sensitive data in localStorage
- **Sessions**: All routes protected with `@validate_session` decorator

## Remember
- This is a manufacturing floor system - keep it simple
- Users might be on tablets/touchscreens
- Downtime costs money - logging must be fast
- Everything must be auditable for compliance
- SQL Server 2012+ compatible (broad enterprise support)
- Templates must work in all code editors (v1.3.2)
- **Users can only login from one location at a time** (v1.3.3)

---
*Version 1.3.3 - Production-ready with single-session enforcement. TEST_MODE for development. All admin features complete. Downtime entry and reports pending implementation.*