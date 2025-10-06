#!/usr/bin/env python3
"""
Health check script for the Digital Signature Application.
Verifies that all components are working correctly.
"""

import os
import sys
import sqlite3
import requests

def check_file_structure():
    """Check if all required files exist."""
    print("🔍 Checking file structure...")
    
    required_files = [
        'run.py',
        'app/__init__.py',
        'app/head.py',
        'app/models.py',
        'app/routes.py',
        'app/forms.py',
        'app/admin.py',
        'app/templates/layout.html',
        'app/templates/login.html',
        'app/templates/register.html',
        'app/templates/dashboard.html',
        'app/templates/upload.html',
        'app/static/css/styles.css',
        'app/static/js/scripts.js',
        'requirements.txt',
        '.env'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present")
        return True

# NOTE: Keep this function using the Flask app config (single source of truth).
# Avoid reintroducing path guessing lists here, as they caused conflicts before.

def check_database():
    """Check if database exists and has required tables."""
    print("🔍 Checking database...")
    
    # Determine database path from the actual Flask app configuration
    try:
        from app import create_app
        app = create_app()
        with app.app_context():
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    except Exception as e:
        print(f"❌ Could not load app configuration: {e}")
        return False

    if db_uri.startswith('sqlite:///'):
        db_path = db_uri.replace('sqlite:///', '')
    else:
        print(f"⚠️ Unsupported or missing DB URI for direct check: {db_uri}")
        return False

    if not os.path.exists(db_path):
        print(f"❌ Database file not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if required tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['user', 'document_log']
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            print(f"❌ Missing database tables: {', '.join(missing_tables)}")
            return False
        
        # Check if admin user exists
        cursor.execute("SELECT COUNT(*) FROM user WHERE username='admin'")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            print("⚠️  Admin user not found in database")
        else:
            print("✅ Admin user exists")
        
        conn.close()
        print("✅ Database structure is correct")
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_imports():
    """Check if all Python imports work correctly."""
    print("🔍 Checking Python imports...")
    
    try:
        from app import create_app
        from app.models import User, DocumentLog
        from app.forms import LoginForm, RegistrationForm, UploadForm
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def check_app_creation():
    """Check if Flask app can be created successfully."""
    print("🔍 Checking Flask app creation...")
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from app.head import db
            # Try to query the database
            from app.models import User
            user_count = db.session.execute(db.select(User)).scalars().all()
            print(f"✅ Flask app created successfully. Found {len(user_count)} users in database")
            return True
    except Exception as e:
        print(f"❌ Flask app creation error: {e}")
        return False

def check_server_running():
    """Check if the server is running and responding."""
    print("🔍 Checking if server is running...")
    
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and responding")
            return True
        else:
            print(f"⚠️  Server responded with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️  Server is not running or not accessible")
        return False
    except Exception as e:
        print(f"❌ Server check error: {e}")
        return False

def main():
    """Run all health checks."""
    print("🏥 Digital Signature Application Health Check")
    print("=" * 50)
    
    checks = [
        ("File Structure", check_file_structure),
        ("Database", check_database),
        ("Python Imports", check_imports),
        ("Flask App Creation", check_app_creation),
        ("Server Status", check_server_running)
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}")
        result = check_func()
        results.append((check_name, result))
    
    print("\n" + "=" * 50)
    print("📊 HEALTH CHECK SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:<20} {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL CHECKS PASSED! Application is healthy.")
        print("\n🚀 You can access the application at: http://localhost:5000")
        print("👤 Default admin credentials: admin / admin123")
    else:
        print("⚠️  SOME CHECKS FAILED! Please review the issues above.")
        sys.exit(1)

if __name__ == '__main__':
    main()