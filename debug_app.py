"""
Diagnostic script to identify blueprint registration issues
Run this instead of app.py to debug the issue
"""

import sys
import os

print("=" * 60)
print("DOWNTIME TRACKER - BLUEPRINT DIAGNOSTIC")
print("=" * 60)
print()

# Step 1: Check Python version
print(f"1. Python Version: {sys.version}")
print()

# Step 2: Test imports one by one
print("2. Testing imports...")

try:
    from flask import Flask
    print("✅ Flask imported successfully")
except ImportError as e:
    print(f"❌ Flask import failed: {e}")
    sys.exit(1)

try:
    from config import Config
    print("✅ Config imported successfully")
except ImportError as e:
    print(f"❌ Config import failed: {e}")

print()
print("3. Testing blueprint imports individually...")
print("-" * 40)

blueprints_to_test = [
    ('routes.main', 'main_bp'),
    ('routes.downtime', 'downtime_bp'),
    ('routes.admin.panel', 'admin_panel_bp'),
    ('routes.admin.facilities', 'admin_facilities_bp'),
    ('routes.admin.production_lines', 'admin_lines_bp'),
    ('routes.admin.categories', 'admin_categories_bp'),
    ('routes.admin.audit', 'admin_audit_bp'),
    ('routes.admin.shifts', 'admin_shifts_bp'),
    ('routes.admin.users', 'admin_users_bp'),
]

imported_blueprints = {}
failed_imports = []

for module_name, blueprint_name in blueprints_to_test:
    try:
        # Import the module
        module = __import__(module_name, fromlist=[blueprint_name])
        # Get the blueprint
        blueprint = getattr(module, blueprint_name)
        imported_blueprints[blueprint_name] = blueprint
        
        # Check for duplicate endpoints
        endpoints = []
        for rule in blueprint.deferred_functions:
            if hasattr(rule, '__name__'):
                endpoints.append(rule.__name__)
        
        print(f"✅ {module_name}.{blueprint_name} imported successfully")
        
    except ImportError as e:
        print(f"❌ Failed to import {module_name}: {e}")
        failed_imports.append((module_name, str(e)))
    except AttributeError as e:
        print(f"❌ Blueprint {blueprint_name} not found in {module_name}: {e}")
        failed_imports.append((module_name, str(e)))
    except Exception as e:
        print(f"❌ Unexpected error with {module_name}: {e}")
        failed_imports.append((module_name, str(e)))

print()
print("4. Checking for endpoint conflicts...")
print("-" * 40)

# Create a test app and try registering blueprints
app = Flask(__name__)
app.secret_key = 'test-key'

registered_endpoints = {}
conflicts = []

for bp_name, blueprint in imported_blueprints.items():
    try:
        # Get the URL prefix if it's an admin blueprint
        url_prefix = '/admin' if 'admin' in bp_name else None
        
        # Check existing endpoints before registration
        before_endpoints = set(app.view_functions.keys())
        
        # Try to register the blueprint
        if url_prefix and bp_name != 'admin_panel_bp':
            app.register_blueprint(blueprint, url_prefix=url_prefix)
        else:
            app.register_blueprint(blueprint)
        
        # Check new endpoints after registration
        after_endpoints = set(app.view_functions.keys())
        new_endpoints = after_endpoints - before_endpoints
        
        print(f"✅ {bp_name} registered successfully")
        print(f"   New endpoints: {', '.join(new_endpoints) if new_endpoints else 'None'}")
        
        # Track all endpoints
        for endpoint in new_endpoints:
            if endpoint in registered_endpoints:
                conflicts.append(f"Conflict: {endpoint} from {bp_name} conflicts with {registered_endpoints[endpoint]}")
            else:
                registered_endpoints[endpoint] = bp_name
                
    except AssertionError as e:
        print(f"❌ {bp_name} registration failed: {e}")
        conflicts.append(f"{bp_name}: {str(e)}")
    except Exception as e:
        print(f"❌ {bp_name} unexpected error: {e}")

print()
print("=" * 60)
print("DIAGNOSTIC SUMMARY")
print("=" * 60)

if failed_imports:
    print("\n⚠️ IMPORT FAILURES:")
    for module, error in failed_imports:
        print(f"  - {module}: {error}")

if conflicts:
    print("\n⚠️ ENDPOINT CONFLICTS:")
    for conflict in conflicts:
        print(f"  - {conflict}")

if not failed_imports and not conflicts:
    print("\n✅ All blueprints imported and registered successfully!")
    print("\n📝 Registered endpoints:")
    for endpoint, blueprint in sorted(registered_endpoints.items()):
        print(f"  - {endpoint:40} from {blueprint}")
else:
    print("\n❌ Issues detected. Please review the errors above.")
    
print()
print("5. Checking for duplicate route definitions...")
print("-" * 40)

# Check each blueprint file for duplicate route definitions
import ast

files_to_check = [
    'routes/main.py',
    'routes/admin/shifts.py',
    'routes/admin/users.py'
]

for filepath in files_to_check:
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                
            # Count route decorators
            route_count = content.count('@main_bp.route') if 'main.py' in filepath else \
                         content.count('@admin_shifts_bp.route') if 'shifts.py' in filepath else \
                         content.count('@admin_users_bp.route')
            
            # Look for duplicate route patterns
            import re
            if 'main.py' in filepath:
                login_routes = re.findall(r"@main_bp.route\(['\"]\/login['\"]", content)
                if len(login_routes) > 1:
                    print(f"⚠️ {filepath}: Found {len(login_routes)} login route definitions!")
                else:
                    print(f"✅ {filepath}: No duplicate routes found")
            
        except Exception as e:
            print(f"❌ Could not check {filepath}: {e}")
    else:
        print(f"⚠️ {filepath} not found")

print()
print("=" * 60)
print("Diagnostic complete!")
print()
print("If you see any errors above, they indicate the source of the problem.")
print("Common solutions:")
print("1. Check for duplicate route definitions in the same file")
print("2. Ensure blueprints are only imported once")
print("3. Check for circular imports")
print("4. Verify all required files exist")
print("=" * 60)