#!/usr/bin/env python3
"""
Database Initialization Script for Brøndby IF Stock Tracker
This script creates the necessary database tables
"""

import os
import sys
from sqlalchemy import create_engine, text
from models import Base, StockData, NewsArticle
from config import Config

def init_database():
    """Initialize the database with required tables"""
    print("🏗️  Initializing database...")
    
    # Create database engine
    engine = create_engine(Config.DATABASE_URL)
    
    try:
        # Create all tables
        Base.metadata.create_all(engine)
        print("✅ Database tables created successfully!")
        
        # Test the connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]
            print(f"📋 Available tables: {tables}")
            
        print("🎉 Database initialization complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
