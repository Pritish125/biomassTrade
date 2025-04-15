#!/usr/bin/env python3
"""
Database initialization script for BioPellet Trade platform.
This script creates all necessary database tables based on the models defined in the application.
"""

from app import app, db

def initialize_database():
    """Create all database tables based on the defined models"""
    print("Initializing database...")
    
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

if __name__ == "__main__":
    initialize_database()