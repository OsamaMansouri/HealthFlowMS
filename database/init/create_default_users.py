"""
Script to create default users in the HealthFlowMS database.

Run this script after the database is initialized to create default user accounts.

Usage:
    python create_default_users.py
    OR
    docker exec -it healthflow-score-api python /app/database/init/create_default_users.py
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../score-api'))

from app.database import SessionLocal
from app.services import UserService
from app.models import User

# Default users as documented in Rapport.tex
DEFAULT_USERS = [
    {"username": "admin", "password": "admin123", "role": "admin", "email": "admin@healthflow.local", "full_name": "Administrator"},
    {"username": "clinician", "password": "admin123", "role": "clinician", "email": "clinician@healthflow.local", "full_name": "Clinical User"},
    {"username": "researcher", "password": "admin123", "role": "researcher", "email": "researcher@healthflow.local", "full_name": "Researcher"},
    {"username": "auditor", "password": "admin123", "role": "auditor", "email": "auditor@healthflow.local", "full_name": "Auditor"},
]


def create_default_users():
    """Create default users if they don't exist."""
    db = SessionLocal()
    user_service = UserService(db)
    
    created_count = 0
    skipped_count = 0
    
    for user_data in DEFAULT_USERS:
        # Check if user already exists
        existing_user = user_service.get_user_by_username(user_data["username"])
        
        if existing_user:
            print(f"⚠️  User '{user_data['username']}' already exists. Skipping.")
            skipped_count += 1
        else:
            try:
                user = user_service.create_user(
                    username=user_data["username"],
                    email=user_data["email"],
                    password=user_data["password"],
                    full_name=user_data["full_name"],
                    role=user_data["role"]
                )
                print(f"✅ Created user: {user.username} (role: {user.role})")
                created_count += 1
            except Exception as e:
                print(f"❌ Error creating user '{user_data['username']}': {e}")
    
    db.close()
    
    print(f"\n📊 Summary: {created_count} users created, {skipped_count} users already existed")
    
    if created_count > 0:
        print("\n🔐 Default Login Credentials:")
        print("=" * 50)
        for user_data in DEFAULT_USERS:
            print(f"  Username: {user_data['username']:<12} Password: {user_data['password']:<12} Role: {user_data['role']}")
        print("=" * 50)
        print("\n⚠️  IMPORTANT: Change these passwords in production!")


if __name__ == "__main__":
    print("🚀 Creating default users for HealthFlowMS...")
    print("-" * 50)
    create_default_users()
    print("-" * 50)
    print("✅ Done!")

