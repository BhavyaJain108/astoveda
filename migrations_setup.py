#!/usr/bin/env python3
"""
Database migration setup script
Run this to initialize Flask-Migrate for database migrations
"""

from flask_migrate import init as migrate_init, migrate as create_migration, upgrade
from app_secure import create_app
import os

def setup_migrations():
    app = create_app()
    
    with app.app_context():
        # Initialize migration repository if it doesn't exist
        if not os.path.exists('migrations'):
            print("Initializing migration repository...")
            migrate_init()
            print("Migration repository created!")
        
        # Create initial migration
        print("Creating initial migration...")
        create_migration(message="Initial migration")
        print("Initial migration created!")
        
        # Apply migration to create tables
        print("Applying migration...")
        upgrade()
        print("Migration applied successfully!")

if __name__ == '__main__':
    setup_migrations()