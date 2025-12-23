"""
Script to initialize the HealthFlowMS database.

This script creates all necessary tables for the score-api service.

Usage:
    python init_database.py
    OR
    docker exec -it healthflow-score-api python /app/database/init/init_database.py
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../score-api'))

from app.database import Base, engine
from app.models import User, ApiAuditLog, RiskPrediction, DeidPatient

def init_database():
    """Create all database tables."""
    print("🚀 Initializing HealthFlowMS database...")
    print("-" * 50)
    
    try:
        # Create all tables
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        
        # List created tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n📊 Created {len(tables)} tables:")
        for table in sorted(tables):
            print(f"  - {table}")
        
        print("\n✅ Database initialization complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)

