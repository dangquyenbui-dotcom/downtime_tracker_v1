# Downtime Tracker v1.3.5 - Condensed Documentation

## Overview
Manufacturing downtime tracking system with Flask + SQL Server + Active Directory integration. iPad-optimized for production floor use with single-session enforcement.

**Current Version:** 1.3.5 (Production-ready)

## Tech Stack & Requirements
- **Backend:** Python 3.7+, Flask, Waitress (production)
- **Database:** SQL Server 2012+
- **Auth:** Active Directory (Windows Server 2012+) or TEST_MODE
- **Frontend:** iPad-optimized responsive web interface
- **Network:** Port 5000, accessible from factory floor iPads

## Core Features
✅ Single-session enforcement (one login per user)  
✅ iPad-optimized downtime entry with cascading dropdowns  
✅ Hierarchical categories (Main XX → Sub XX##) with color coding  
✅ Auto-shift detection based on time  
✅ Crew size tracking (1-10 associates)  
✅ **v1.3.5:** Shared downtime visibility - all users see entries for same line  
✅ Full audit trail (soft deletes only)  
✅ Admin panel with CRUD for all entities  

## Key Database Tables
- **Facilities** - Manufacturing locations
- **ProductionLines** - Lines per facility  
- **DowntimeCategories** - Hierarchical (parent_id), color-coded
- **Downtimes** - Main tracking (crew_size, duration computed)
- **Shifts** - Work schedules with overnight support
- **ActiveSessions** - Single-session enforcement
- **AuditLog** - Field-level change tracking
- **UserLogins** - Activity monitoring

## Project Structure
```
downtime-tracker/
├── app.py                     # Main entry, network config
├── run_production.py          # Waitress production server
├── config.py                  # Environment config
├── .env                       # Environment variables
├── auth/                      # AD authentication
├── database/                  # DB modules (singleton pattern)
│   ├── connection.py         # CaseInsensitiveDict for SQL compatibility
│   ├── downtimes.py         # Enhanced with shared viewing
│   └── [other CRUD modules]
├── routes/                   # Flask blueprints
│   ├── main.py              # Login with session conflict handling
│   ├── downtime.py          # iPad-optimized entry form
│   └── admin/               # Admin management routes
├── static/                  # CSS/JS with theme system
└── templates/               # Jinja2 templates
```

## Essential Configuration (.env)
```env
TEST_MODE=False                    # True bypasses AD
SECRET_KEY=your-secret-key
DB_SERVER=YOUR_SQL_SERVER
DB_NAME=ProductionDB
DB_USE_WINDOWS_AUTH=False
DB_USERNAME=username
DB_PASSWORD=password
AD_DOMAIN=DOMAIN.LOCAL
AD_SERVER=dc.domain.local
AD_ADMIN_GROUP=DowntimeTracker_Admin
AD_USER_GROUP=DowntimeTracker_User
SESSION_HOURS=8
```

## Running the System
```bash
# Development
pip install -r requirements.txt
python app.py                    # http://localhost:5000

# Production (recommended)
pip install waitress
python run_production.py         # More stable for network

# Windows Firewall
New-NetFirewallRule -DisplayName "Downtime Tracker" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

## Access Levels
- **Regular Users** (AD_USER_GROUP): Report downtime, view dashboard
- **Administrators** (AD_ADMIN_GROUP): Full system configuration + all user permissions
- **TEST_MODE**: Use test/test (user) or test1/test1 (admin)

## v1.3.5 Key Updates
1. **CaseInsensitiveDict** - Fixes SQL Server column name case sensitivity issues
2. **Shared Downtime Visibility** - Users see all entries for their selected line:
   - Shows who entered each record (👤 username indicator)
   - Users can only edit/delete their own entries
   - Other users' entries have muted appearance
   - Enhances shift handover and team coordination

## Implementation Patterns
- **Database:** Singleton pattern for all modules, persistent connections with auto-reconnect
- **Security:** Session validation decorator on all routes, single-session enforcement
- **UI:** Touch-friendly (min 50px height), no zoom (16px fonts), dark/light theme
- **Audit:** Never hard delete, track all field-level changes
- **Forms:** Cascading dropdowns, auto-populated times (30 min ago → now)

## Common Operations
- **Report Downtime:** `/downtime` - Select facility→line→category→subcategory
- **Session Conflicts:** Warning shown, option to force login
- **View Shared Entries:** Automatically shows all users' entries for selected line
- **Admin Tasks:** Manage facilities/lines/categories/shifts through `/admin`

## Critical Notes
- **iPad Optimized:** All interfaces designed for factory floor tablets
- **Data Integrity:** Soft deletes only, full audit trail
- **Performance:** Persistent DB connections, efficient queries
- **Compatibility:** SQL Server 2012+ (no STRING_AGG), handles case-insensitive columns

## Troubleshooting Quick Reference
- **Network Issues:** Check firewall port 5000, run with `host='0.0.0.0'`
- **DB Connection:** Verify SQL Server running, test both drivers (SQL Server/ODBC 17)
- **Column Name Errors:** v1.3.5 CaseInsensitiveDict handles this automatically
- **Session Issues:** Check ActiveSessions table, expires after SESSION_HOURS

## Future Roadmap
- Reports dashboard with charts
- Excel export functionality  
- Email notifications for critical categories
- REST API for ERP integration
- Predictive analytics for pattern detection

---
*Optimized for manufacturing floor use with focus on simplicity, reliability, and data integrity.*