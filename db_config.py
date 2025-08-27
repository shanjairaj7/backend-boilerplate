"""
JSON Database Configuration - Compatibility layer for db_config imports
This ensures existing imports of db_config still work after JSON DB migration
"""

# Re-export JSON DB functions for compatibility
from json_db import JsonDBSession, get_db, create_tables, drop_tables, db

print(f"🗄️ Using JSON Database: {db.db_dir}")

# For backward compatibility with any remaining SQLAlchemy references
class MockEngine:
    """Mock engine for health checks that expect SQLAlchemy engine"""
    def connect(self):
        # Simulate a successful connection
        return self

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

# Mock engine for compatibility
engine = MockEngine()

# For any remaining Base references
class MockBase:
    """Mock base class for compatibility"""
    class metadata:
        @staticmethod
        def create_all(bind=None):
            create_tables()
        
        @staticmethod
        def drop_all(bind=None):
            drop_tables()

Base = MockBase()