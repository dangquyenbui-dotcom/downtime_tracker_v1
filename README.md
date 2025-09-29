# Downtime Tracker v1.3.4 - Complete Documentation

## Project Overview
Manufacturing downtime tracking system with single-session enforcement, iPad-optimized interface for production floor use. Built with Flask + SQL Server + Active Directory integration.

**Current Version: 1.3.4** - Production-ready with complete downtime entry system
- ✅ Single-session enforcement (one login per user)
- ✅ iPad-optimized downtime entry form
- ✅ Hierarchical category management with color coding
- ✅ Auto-shift detection based on time
- ✅ Complete admin panel with audit logging
- ✅ Network-accessible for factory floor iPads
- ✅ Full CRUD operations for all entities

## Complete File Structure
```
downtime-tracker/
│
├── app.py                          # Main application entry point with network config
├── run_production.py               # Production server using Waitress
├── config.py                       # Configuration management
├── requirements.txt                # Python dependencies
├── test_network.py                 # Network diagnostic tool
├── .env                           # Environment variables (create from .env.example)
│
├── auth/
│   ├── __init__.py
│   └── ad_auth.py                 # Active Directory authentication
│
├── database/
│   ├── __init__.py                # Database module exports
│   ├── connection.py              # Persistent DB connection management
│   ├── facilities.py              # Facilities CRUD operations
│   ├── production_lines.py        # Production lines CRUD
│   ├── categories.py              # Hierarchical categories management
│   ├── downtimes.py               # Downtime entries with crew size
│   ├── shifts.py                  # Shift management
│   ├── users.py                   # User activity tracking
│   ├── sessions.py                # Active sessions management
│   └── audit.py                   # Audit logging
│
├── routes/
│   ├── __init__.py
│   ├── main.py                    # Login, dashboard, logout, status
│   ├── downtime.py                # COMPLETE: iPad-optimized entry form
│   └── admin/
│       ├── __init__.py
│       ├── panel.py               # Admin dashboard
│       ├── facilities.py          # Facilities management
│       ├── production_lines.py    # Lines management
│       ├── categories.py          # Categories with reactivation
│       ├── shifts.py              # Shift configuration
│       ├── users.py               # User activity monitoring
│       └── audit.py               # Audit log viewer
│
├── static/
│   ├── css/
│   │   ├── base.css              # Theme system, core styles
│   │   └── admin.css              # Admin panel styles
│   └── js/
│       ├── common.js              # dtUtils namespace, shared functions
│       └── theme.js               # Dark/light theme management
│
├── templates/
│   ├── base.html                  # Base template with navbar
│   ├── login.html                 # Standalone login with session conflict handling
│   ├── dashboard.html             # User dashboard
│   ├── status.html                # System status page
│   │
│   ├── downtime/
│   │   └── entry.html             # iPad-optimized downtime entry form
│   │
│   └── admin/
│       ├── panel.html             # Admin main page
│       ├── facilities.html        # Facilities management
│       ├── production_lines.html  # Lines management
│       ├── categories.html        # Categories with dynamic colors
│       ├── shifts.html            # Shift management
│       ├── users.html             # User management
│       └── audit_log.html         # Audit trail viewer
│
└── utils/
    ├── __init__.py
    ├── helpers.py                 # Helper functions
    └── validators.py              # Input validation
```

## System Requirements
- **Python**: 3.7+ (3.9+ recommended)
- **SQL Server**: 2012 or later (2016+ recommended)
- **Active Directory**: Windows Server 2012+ (optional - TEST_MODE available)
- **OS**: Windows Server 2016+ or Windows 10/11
- **Network**: Port 5000 open for iPad access
- **Client Devices**: iPad/tablets with modern browser

## Database Schema

### Core Tables
```sql
-- Facilities (Manufacturing locations)
CREATE TABLE Facilities (
    facility_id INT IDENTITY(1,1) PRIMARY KEY,
    facility_name NVARCHAR(100) NOT NULL,
    location NVARCHAR(200),
    is_active BIT DEFAULT 1,
    created_date DATETIME DEFAULT GETDATE(),
    created_by NVARCHAR(100),
    modified_date DATETIME,
    modified_by NVARCHAR(100)
);

-- Production Lines
CREATE TABLE ProductionLines (
    line_id INT IDENTITY(1,1) PRIMARY KEY,
    facility_id INT NOT NULL FOREIGN KEY REFERENCES Facilities(facility_id),
    line_name NVARCHAR(100) NOT NULL,
    line_code NVARCHAR(20),
    is_active BIT DEFAULT 1,
    created_date DATETIME DEFAULT GETDATE(),
    created_by NVARCHAR(100),
    modified_date DATETIME,
    modified_by NVARCHAR(100)
);

-- Downtime Categories (Hierarchical)
CREATE TABLE DowntimeCategories (
    category_id INT IDENTITY(1,1) PRIMARY KEY,
    parent_id INT NULL FOREIGN KEY REFERENCES DowntimeCategories(category_id),
    category_name NVARCHAR(100) NOT NULL,
    category_code NVARCHAR(4) NOT NULL UNIQUE,  -- XX for main, XX01 for sub
    description NVARCHAR(500),
    color_code NVARCHAR(7),  -- Hex color
    notification_required BIT DEFAULT 0,
    is_active BIT DEFAULT 1,
    created_date DATETIME DEFAULT GETDATE(),
    created_by NVARCHAR(100),
    modified_date DATETIME,
    modified_by NVARCHAR(100)
);

-- Shifts
CREATE TABLE Shifts (
    shift_id INT IDENTITY(1,1) PRIMARY KEY,
    shift_name NVARCHAR(100) NOT NULL,
    shift_code NVARCHAR(10),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    duration_hours DECIMAL(4,2),
    description NVARCHAR(500),
    is_overnight BIT DEFAULT 0,
    is_active BIT DEFAULT 1,
    created_date DATETIME DEFAULT GETDATE(),
    created_by NVARCHAR(100),
    modified_date DATETIME,
    modified_by NVARCHAR(100)
);

-- Downtime Entries (Main tracking table)
CREATE TABLE Downtimes (
    downtime_id INT IDENTITY(1,1) PRIMARY KEY,
    line_id INT NOT NULL FOREIGN KEY REFERENCES ProductionLines(line_id),
    category_id INT NOT NULL FOREIGN KEY REFERENCES DowntimeCategories(category_id),
    shift_id INT NULL FOREIGN KEY REFERENCES Shifts(shift_id),
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    duration_minutes INT NOT NULL,
    crew_size INT DEFAULT 1,  -- NEW: Number of operators affected (1-10)
    reason_notes NVARCHAR(MAX),
    entered_by NVARCHAR(100) NOT NULL,
    entered_date DATETIME DEFAULT GETDATE(),
    created_by NVARCHAR(100),
    created_date DATETIME DEFAULT GETDATE(),
    modified_by NVARCHAR(100),
    modified_date DATETIME,
    is_deleted BIT DEFAULT 0
);

-- User Activity Tracking
CREATE TABLE UserLogins (
    login_id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(100) NOT NULL,
    display_name NVARCHAR(200),
    email NVARCHAR(200),
    ad_groups NVARCHAR(MAX),
    is_admin BIT DEFAULT 0,
    login_date DATETIME NOT NULL,
    ip_address NVARCHAR(50),
    user_agent NVARCHAR(500)
);

-- Active Sessions (Single-session enforcement)
CREATE TABLE ActiveSessions (
    session_id NVARCHAR(100) PRIMARY KEY,
    username NVARCHAR(100) NOT NULL,
    login_date DATETIME NOT NULL,
    last_activity DATETIME NOT NULL,
    ip_address NVARCHAR(50),
    user_agent NVARCHAR(500),
    is_active BIT DEFAULT 1
);

-- Audit Log
CREATE TABLE AuditLog (
    audit_id INT IDENTITY(1,1) PRIMARY KEY,
    table_name NVARCHAR(100) NOT NULL,
    record_id INT,
    action_type NVARCHAR(50) NOT NULL,  -- INSERT, UPDATE, DELETE, DEACTIVATE, REACTIVATE
    field_name NVARCHAR(100),
    old_value NVARCHAR(MAX),
    new_value NVARCHAR(MAX),
    changed_by NVARCHAR(100) NOT NULL,
    changed_date DATETIME NOT NULL DEFAULT GETDATE(),
    user_ip NVARCHAR(50),
    user_agent NVARCHAR(500),
    additional_notes NVARCHAR(MAX)
);
```

## Configuration (.env file)

```env
# Core Settings
TEST_MODE=False                    # Set True to bypass AD authentication
SECRET_KEY=your-secret-key-here    # Change in production!

# Database Configuration
DB_SERVER=YOUR_SQL_SERVER
DB_NAME=ProductionDB
DB_USE_WINDOWS_AUTH=False          # Set True for Windows Auth
DB_USERNAME=db_username            # Not needed if Windows Auth
DB_PASSWORD=db_password            # Not needed if Windows Auth

# Active Directory Settings
AD_DOMAIN=YOURDOMAIN.LOCAL
AD_SERVER=your-dc.domain.local
AD_PORT=389
AD_BASE_DN=DC=domain,DC=local
AD_SERVICE_ACCOUNT=service_account
AD_SERVICE_PASSWORD=service_password
AD_ADMIN_GROUP=DowntimeTracker_Admin    # AD group for admins
AD_USER_GROUP=DowntimeTracker_User      # AD group for users

# Session Configuration
SESSION_HOURS=8                    # Session timeout in hours

# Email Settings (optional)
SMTP_SERVER=mail.domain.local
SMTP_PORT=587
SMTP_USE_TLS=True
EMAIL_FROM=downtime@domain.local
```

## How to Run

### Development Mode
```bash
# Install dependencies
pip install -r requirements.txt

# Run with network access
python app.py

# Access URLs:
# Local: http://localhost:5000
# Network: http://YOUR_IP:5000
# iPad: http://YOUR_IP:5000/downtime
```

### Production Mode (Recommended)
```bash
# Install production server
pip install waitress

# Run production server
python run_production.py

# More stable for network access
```

### Windows Firewall Setup
```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "Downtime Tracker" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

## Key Features & Implementation Details

### 1. **Single-Session Enforcement**
- Users can only login from one device at a time
- Session conflicts show warning with option to force login
- All sessions tracked in `ActiveSessions` table
- Decorator `@validate_session` on all protected routes

### 2. **iPad-Optimized Downtime Entry** (/downtime)
- Large touch-friendly buttons (min 50px height)
- No zoom on input focus (font-size: 16px)
- Cascading dropdowns: Facility → Line, Category → Subcategory
- Auto-detects current shift based on time
- Pre-fills times (start: 30 min ago, end: now)
- Crew size selector with +/- buttons (1-10)
- Shows recent entries for reference
- Success modal with auto-reset

### 3. **Hierarchical Categories**
- Two-level structure: Main (XX) and Sub (XX01)
- Color coding with visual indicators
- Parent must be active to reactivate child
- Email notification flags per category
- Expand/collapse UI with smart filtering

### 4. **Audit System**
- Field-level change tracking
- Complete history for all entities
- IP and user agent logging
- Never hard delete - only soft delete
- Timeline visualization in UI

### 5. **Theme System**
- True black OLED mode for dark theme
- No flash on page load (theme applied before render)
- Persistent across sessions via localStorage
- CSS variables for easy customization

### 6. **Database Patterns**
- Singleton pattern for all DB modules
- Persistent connections with auto-reconnect
- SQL Server 2012+ compatibility (no STRING_AGG)
- All modules follow same CRUD pattern

## Access Levels

### Regular Users (DowntimeTracker_User group)
- ✅ Login/Dashboard access
- ✅ Report downtime (/downtime)
- ✅ View their recent entries
- ❌ No admin panel access
- ❌ Cannot modify configurations

### Administrators (DowntimeTracker_Admin group)
- ✅ All user permissions
- ✅ Admin panel access (/admin)
- ✅ Manage facilities & production lines
- ✅ Configure categories & shifts
- ✅ View user activity & audit logs
- ✅ System status page (/status)

## Test Mode

Set `TEST_MODE=True` in .env for development:
- Bypasses Active Directory completely
- Test credentials:
  - User: `test/test`
  - Admin: `test1/test1`
- Perfect for development and testing

## Common Operations

### Adding a New Facility
1. Admin → Facilities → Add New Facility
2. Enter name and location
3. Automatically tracked in audit log

### Reporting Downtime (iPad)
1. Navigate to `/downtime`
2. Select facility → production line auto-filters
3. Select main category → subcategories load
4. Set times (or use defaults)
5. Adjust crew size (default: 2)
6. Add comments if needed
7. Submit → Success modal → Form resets

### Viewing Audit Trail
1. Admin → Audit Log
2. Filter by table, action, user, or date
3. See field-level changes with old/new values

## Troubleshooting

### Cannot Access from Network
1. Check Windows Firewall allows port 5000
2. Verify app running with `host='0.0.0.0'`
3. Try using `run_production.py` instead
4. Run `python test_network.py` for diagnostics

### Database Connection Issues
- Verify SQL Server is running
- Check connection string in .env
- Try both SQL Server and ODBC Driver 17
- Test with `python -c "from database import facilities_db; print(facilities_db.get_all())"`

### Session Conflicts
- Users seeing "session expired" = logged in elsewhere
- Check ActiveSessions table for debugging
- Sessions auto-expire after SESSION_HOURS

### iPad Specific Issues
- Ensure font-size >= 16px (prevents zoom)
- Test both portrait and landscape orientations
- Clear Safari cache if styles not updating

## Version History

### v1.3.4 (Current) - Complete Downtime Entry
- ✅ Full downtime entry form implementation
- ✅ iPad-optimized responsive interface
- ✅ Crew size tracking (1-10 associates)
- ✅ Auto-shift detection
- ✅ Cascading category selection
- ✅ Network accessibility improvements
- ✅ Production server support (Waitress)

### v1.3.3 - Single-Session Enforcement
- Implemented single-session enforcement
- Added session conflict detection
- Created ActiveSessions table
- Applied session validation to all routes

### v1.3.2 - Template Compatibility
- Fixed VS Code CSS parsing errors
- Separated Jinja2 from inline styles
- Implemented data attribute pattern

### v1.3.1 - Database Optimization
- Fixed SQL Server 2012 compatibility
- Implemented persistent connections
- Fixed category filtering

### v1.3 - User & Shift Management
- Complete shift management system
- User activity tracking
- Login monitoring

### v1.2 - Core Features
- Category management
- Audit logging
- Dashboard improvements

### v1.0 - Initial Release
- Basic facilities and lines
- Simple authentication

## Development Guidelines

### Adding New Features
1. Follow singleton pattern for database modules
2. Always soft delete (never hard delete)
3. Log all changes to audit trail
4. Add `@validate_session` to new routes
5. Maintain iPad compatibility (large touch targets)
6. Use dtUtils namespace for JavaScript functions

### Code Standards
- **Python**: Follow database singleton pattern
- **Templates**: No Jinja2 in inline styles
- **JavaScript**: Use data attributes for dynamic values
- **CSS**: Provide defaults for all dynamic properties
- **Security**: Never store sensitive data in localStorage

### Database Module Pattern
```python
class NewModuleDB:
    def __init__(self):
        self.db = get_db()
    
    def get_all(self, active_only=True):
        # Implementation
        pass
    
    def create(self, data, username):
        # Implementation with audit
        pass
    
    def update(self, id, data, username):
        # Implementation with change tracking
        pass
    
    def deactivate(self, id, username):
        # Soft delete only
        pass
```

## Future Development Roadmap

### Phase 1 (Next)
- [ ] Reports dashboard with charts
- [ ] Export to Excel functionality
- [ ] Email notifications for critical categories
- [ ] Batch downtime entry

### Phase 2
- [ ] REST API for integration
- [ ] Mobile app (React Native)
- [ ] Real-time dashboards
- [ ] Predictive analytics

### Phase 3
- [ ] Multi-plant support
- [ ] Integration with ERP systems
- [ ] Advanced analytics
- [ ] Machine learning for pattern detection

## Support & Contact

For issues or questions:
1. Check troubleshooting section
2. Review audit logs for errors
3. Test with `TEST_MODE=True`
4. Run network diagnostics
5. Check SQL Server logs

## Important Notes

- **Production Floor Usage**: System designed for iPad use on factory floor
- **Data Integrity**: All deletions are soft deletes
- **Compliance**: Full audit trail for regulatory requirements
- **Performance**: Persistent DB connections for speed
- **Security**: Single-session enforcement prevents credential sharing
- **Simplicity**: Interface optimized for quick data entry

---
*Downtime Tracker v1.3.4 - Production-ready manufacturing downtime tracking system*

Here's a new README section documenting the recent improvements and fixes:

```markdown

## Recent Updates & Fixes

### Version 1.3.5 (Latest) - Enhanced Collaboration & Database Compatibility
Released: September 2025

#### 🔧 Critical Fixes

##### Database Case-Insensitive Column Access
**Problem Solved**: SQL Server column name case sensitivity causing `KeyError: 'COLUMN_NAME'` errors

**Solution Implemented**: 
- Added `CaseInsensitiveDict` class to `database/connection.py`
- Database results now accept column names in any case (COLUMN_NAME, column_name, Column_Name)
- No changes required to existing database modules
- Improved compatibility across different SQL Server configurations

**Technical Details**:
```python
# Now all these work regardless of SQL Server's column casing:
result['COLUMN_NAME']  # Original case
result['column_name']  # Lowercase
result['Column_Name']  # Mixed case
```

#### ✨ New Features

##### Shared Downtime Visibility
**Enhancement**: All users can now see downtime entries from other users for the same production line

**Key Features**:
- **Collaborative Viewing**: View all entries for a selected facility/production line for the current day
- **User Attribution**: Each entry displays who submitted it (👤 username indicator)
- **Edit Protection**: Users can only edit/delete their own entries
- **Visual Distinction**: Other users' entries have a subtle different appearance for clarity
- **Real-time Collaboration**: Multiple operators can track downtime for the same line simultaneously

**Benefits**:
- Better shift handover visibility
- Complete downtime picture for supervisors
- Reduced duplicate entries
- Enhanced team coordination

**Implementation**:
- New database method: `get_all_entries_for_line_today()` in `database/downtimes.py`
- Updated route: `/downtime/api/today-entries/<line_id>` returns all entries with ownership flags
- Enhanced UI: Shows entry owner and restricts edit/delete to entry creator

#### 📋 Technical Improvements

##### Database Connection Enhancements
- **Persistent Connections**: Better connection pooling with auto-reconnect
- **Case-Insensitive Queries**: Robust handling of SQL Server metadata
- **Error Recovery**: Improved error handling and automatic retry logic

##### UI/UX Improvements
- **Entry Attribution**: Clear display of who entered each downtime record
- **Ownership Indicators**: Visual badges showing "your entries" vs "team entries"
- **Edit Restrictions**: Smart UI that only shows edit/delete buttons for user's own entries

## Migration Guide

### Upgrading from v1.3.4 to v1.3.5

1. **Update Database Connection Module**:
   ```bash
   # Replace database/connection.py with the new version
   # This includes CaseInsensitiveDict support
   ```

2. **Update Downtimes Module**:
   ```bash
   # Update database/downtimes.py
   # Adds get_all_entries_for_line_today() method
   ```

3. **Update Routes**:
   ```bash
   # Update routes/downtime.py
   # Modified get_today_entries() to show all users' entries
   ```

4. **No Database Schema Changes Required**:
   - All changes are code-level only
   - Existing database structure remains unchanged
   - Backward compatible with existing data

5. **Restart Application**:
   ```bash
   python app.py
   # or for production
   python run_production.py
   ```

## Usage Guide

### Viewing Shared Entries

1. **Navigate to Downtime Entry** (`/downtime`)
2. **Select Facility and Production Line**
3. **View "All Today's Entries for This Line"** section:
   - Shows all entries from all users for today
   - Each entry displays the username of who submitted it
   - Your entries have Edit/Delete buttons
   - Other users' entries are read-only with visual distinction

### Understanding Entry Ownership

- **Your Entries**: 
  - Full color background
  - Edit ✏️ and Delete 🗑️ buttons visible
  - Can be modified or removed

- **Team Entries**:
  - Slightly muted appearance
  - Shows 👤 username badge
  - Read-only (no action buttons)
  - Provides context for total line downtime

## Troubleshooting Guide

### Common Issues & Solutions

#### Issue: "KeyError: 'COLUMN_NAME'" Error
**Solution**: Update `database/connection.py` with the new CaseInsensitiveDict implementation

#### Issue: Can't See Other Users' Entries
**Solution**: 
1. Verify you're using the updated `database/downtimes.py` with `get_all_entries_for_line_today()` method
2. Check that the route `/downtime/api/today-entries/` is using the new method
3. Clear browser cache and refresh the page

#### Issue: Can Edit Other Users' Entries
**Solution**: Ensure the frontend JavaScript checks `entry.is_own_entry` flag before showing edit buttons

#### Issue: Database Connection Drops
**Solution**: The new connection.py includes auto-reconnect logic, but check:
1. SQL Server is running and accessible
2. Network connectivity is stable
3. Database credentials in .env are correct

## Performance Considerations

### Optimizations in v1.3.5

- **Connection Pooling**: Persistent database connections reduce overhead
- **Efficient Queries**: Single query retrieves all entries for a line
- **Client-Side Filtering**: Visual distinctions handled in browser
- **Minimal Network Traffic**: Only necessary data transmitted

### Scaling Recommendations

For high-traffic installations:
1. **Database Indexing**: Ensure indexes on:
   ```sql
   CREATE INDEX IX_Downtimes_LineDate ON Downtimes(line_id, start_time);
   CREATE INDEX IX_Downtimes_EnteredBy ON Downtimes(entered_by);
   ```

2. **Session Management**: Configure appropriate session timeout in .env:
   ```env
   SESSION_HOURS=8  # Adjust based on shift length
   ```

3. **Production Server**: Use Waitress for better concurrency:
   ```bash
   python run_production.py  # Handles multiple simultaneous users better
   ```

## Security Notes

### v1.3.5 Security Features

- **Entry Ownership Protection**: Server-side validation prevents editing others' entries
- **Session Validation**: Each request validates user session
- **SQL Injection Prevention**: All queries use parameterized statements
- **XSS Protection**: User input properly escaped in templates

### Best Practices

1. **Regular Audits**: Check the audit log regularly for unusual activity
2. **User Training**: Ensure users understand they can see but not edit others' entries
3. **Backup Strategy**: Regular database backups recommended before shifts
4. **Access Control**: Maintain proper AD group membership

## API Reference Update

### New/Modified Endpoints

#### GET `/downtime/api/today-entries/<line_id>`
Returns all downtime entries for a specific production line for the current day.

**Response Format**:
```json
{
  "success": true,
  "entries": [
    {
      "downtime_id": 123,
      "line_id": 5,
      "category_name": "Mechanical Issue",
      "start_time_str": "08:30",
      "end_time_str": "09:15",
      "duration_minutes": 45,
      "crew_size": 3,
      "entered_by": "jsmith",
      "is_own_entry": true,
      "shift_name": "Morning Shift",
      "reason_notes": "Conveyor belt adjustment"
    }
  ]
}
```

**Key Fields**:
- `entered_by`: Username of the person who created the entry
- `is_own_entry`: Boolean indicating if current user can edit/delete this entry

## Future Roadmap Additions

### Planned for v1.4.0
Based on the collaborative viewing success, planned enhancements include:

- **Entry Notifications**: Alert when someone adds entry to your line
- **Shift Summary**: Automatic shift report generation with all entries
- **Entry Templates**: Save common downtime scenarios for quick entry
- **Bulk Entry**: Submit multiple downtimes at once
- **Mobile App**: Progressive Web App for better mobile experience

### Long-term Vision
- **Cross-Facility Views**: See downtimes across multiple facilities
- **Predictive Analytics**: ML-based downtime prediction
- **Integration APIs**: Connect with MES/ERP systems
- **Real-time Dashboards**: WebSocket-based live updates

---
*End of v1.3.5 Update Documentation*
```

This new section provides comprehensive documentation of the recent changes and can be appended directly to your existing README. It includes:

1. **Clear problem/solution descriptions** for the fixes
2. **Step-by-step migration guide** for upgrading
3. **Usage instructions** for the new features
4. **Troubleshooting section** for common issues
5. **Performance and security considerations**
6. **API documentation** for the modified endpoints
7. **Future roadmap** based on the collaborative features

The documentation maintains the same professional style and structure as your original README while adding valuable information about the latest improvements.