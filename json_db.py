"""
JSON File Database - Simple JSON-based Database Alternative to SQLAlchemy
Contains all database operations using JSON files for storage
"""
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
import secrets
from pathlib import Path

class JsonDB:
    def __init__(self, db_name: str = "database"):
        """Initialize JSON database with specified name"""
        # Use /root/json_data for Modal volume mount, fallback to local for development
        if os.path.exists("/root/json_data"):
            self.db_dir = Path("/root/json_data")
        else:
            self.db_dir = Path("json_data")
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.db_name = db_name

    def get_table_path(self, table_name: str) -> Path:
        """Get the file path for a table"""
        return self.db_dir / f"{self.db_name}_{table_name}.json"

    def load_table(self, table_name: str) -> List[Dict[str, Any]]:
        """Load data from a JSON table file"""
        table_path = self.get_table_path(table_name)
        if not table_path.exists():
            return []

        try:
            with open(table_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_table(self, table_name: str, data: List[Dict[str, Any]]) -> None:
        """Save data to a JSON table file"""
        table_path = self.get_table_path(table_name)
        with open(table_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def _get_next_id(self, table_name: str) -> int:
        """Get the next auto-increment ID for a table"""
        data = self.load_table(table_name)
        if not data:
            return 1
        return max(item.get('id', 0) for item in data) + 1

    def insert(self, table_name: str, record: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new record into a table"""
        data = self.load_table(table_name)

        # Add auto-increment ID if not present
        if 'id' not in record:
            record['id'] = self._get_next_id(table_name)

        # Add timestamp if not present
        if 'created_at' not in record:
            record['created_at'] = datetime.now().isoformat()

        data.append(record)
        self.save_table(table_name, data)
        return record

    def find_one(self, table_name: str, **filters) -> Optional[Dict[str, Any]]:
        """Find one record matching the filters"""
        data = self.load_table(table_name)

        for record in data:
            match = True
            for key, value in filters.items():
                if record.get(key) != value:
                    match = False
                    break
            if match:
                return record

        return None

    def find_all(self, table_name: str, **filters) -> List[Dict[str, Any]]:
        """Find all records matching the filters"""
        data = self.load_table(table_name)

        if not filters:
            return data

        results = []
        for record in data:
            match = True
            for key, value in filters.items():
                if record.get(key) != value:
                    match = False
                    break
            if match:
                results.append(record)

        return results

    def update_one(self, table_name: str, filters: Dict[str, Any], updates: Dict[str, Any]) -> bool:
        """Update one record matching the filters"""
        data = self.load_table(table_name)

        for i, record in enumerate(data):
            match = True
            for key, value in filters.items():
                if record.get(key) != value:
                    match = False
                    break
            if match:
                # Update the record
                data[i].update(updates)
                data[i]['updated_at'] = datetime.now().isoformat()
                self.save_table(table_name, data)
                return True

        return False

    def delete_one(self, table_name: str, **filters) -> bool:
        """Delete one record matching the filters"""
        data = self.load_table(table_name)

        for i, record in enumerate(data):
            match = True
            for key, value in filters.items():
                if record.get(key) != value:
                    match = False
                    break
            if match:
                data.pop(i)
                self.save_table(table_name, data)
                return True

        return False

    def count(self, table_name: str, **filters) -> int:
        """Count records matching the filters"""
        return len(self.find_all(table_name, **filters))

    def exists(self, table_name: str, **filters) -> bool:
        """Check if any records match the filters"""
        return self.find_one(table_name, **filters) is not None

# Global database instance
db = JsonDB()

# Context manager for database sessions (compatibility with SQLAlchemy pattern)
class JsonDBSession:
    def __init__(self):
        self.db = db

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

def get_db():
    """FastAPI dependency injection for database session - JSON DB compatible"""
    yield JsonDBSession()

def create_tables(table_names: List[str] = None):
    """Create database tables - for JSON DB, this ensures the directory exists and each table file is created if missing

    Args:
        table_names: List of table names to create. If None, just creates the database directory.
    """
    db.db_dir.mkdir(parents=True, exist_ok=True)

    if table_names:
        for table_name in table_names:
            table_path = db.get_table_path(table_name)
            if not table_path.exists():
                db.save_table(table_name, []) # Create empty JSON array for the table
        print(f"🗄️ JSON Database initialized with tables {table_names}: {db.db_dir}")
    else:
        print(f"🗄️ JSON Database directory initialized: {db.db_dir}")

def drop_tables():
    """Drop all database tables - removes all JSON files"""
    import shutil
    if db.db_dir.exists():
        shutil.rmtree(db.db_dir)
        print(f"🗑️ JSON Database dropped: {db.db_dir}")
