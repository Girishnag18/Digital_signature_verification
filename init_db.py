#!/usr/bin/env python3
"""
Database initialization script for the Digital Signature Application.
"""

import os
from app import create_app
from app.head import db
from app.models import User, DocumentLog

def init_database():
    """Initialize the database with tables and sample data."""
    app = create_app()
    
    with app.app_context():
        # Ensure database directory exists
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
        
        # Create all tables
        db.create_all()
        
        # Check if admin user already exists
        admin_user = db.session.execute(
            db.select(User).filter_by(username='admin')
        ).scalar_one_or_none()
        
        if not admin_user:
            # Create admin user
            admin_user = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created: username='admin', password='admin123'")
        else:
            print("Admin user already exists")
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()