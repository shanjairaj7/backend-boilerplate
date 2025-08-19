# Database Integration Guide

## Overview
This project uses SQLite with SQLAlchemy ORM for database operations. SQLite is perfect for development and small to medium applications, with an easy upgrade path to PostgreSQL when needed.

## Getting Started

### 1. Database Setup
The `database.py` file is already configured with SQLite. No additional setup required!

```python
# database.py is already created with:
# - SQLite engine configuration
# - Session management  
# - Base class for models
# - Helper functions
```

### 2. Create Your Models

Create a new model file in `models/` directory:

```python
# models/your_model.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from database import Base

# SQLAlchemy ORM Model (Database)
class YourModelORM(Base):
    __tablename__ = "your_table"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# Pydantic Models (API)
class YourModelBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True

class YourModelCreate(YourModelBase):
    pass

class YourModelUpdate(YourModelBase):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class YourModelResponse(YourModelBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Pydantic v2 compatibility
```

### 3. Create Your Service

Create a service file in `services/` directory:

```python
# services/your_service.py
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from models.your_model import YourModelORM, YourModelCreate, YourModelUpdate, YourModelResponse
from database import get_db, create_tables

# Initialize tables
create_tables()

router = APIRouter(prefix="/your-endpoint", tags=["your-tag"])

@router.get("/", response_model=List[YourModelResponse])
def get_items(db: Session = Depends(get_db)):
    items = db.query(YourModelORM).order_by(YourModelORM.created_at.desc()).all()
    return items

@router.get("/{item_id}/", response_model=YourModelResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(YourModelORM).filter(YourModelORM.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/", response_model=YourModelResponse)
def create_item(item: YourModelCreate, db: Session = Depends(get_db)):
    db_item = YourModelORM(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/{item_id}/", response_model=YourModelResponse)
def update_item(item_id: int, item_update: YourModelUpdate, db: Session = Depends(get_db)):
    db_item = db.query(YourModelORM).filter(YourModelORM.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = item_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{item_id}/")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(YourModelORM).filter(YourModelORM.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted"}
```

## Key Patterns

### Model Naming Convention
- SQLAlchemy models: `ModelNameORM` 
- Pydantic schemas: `ModelNameBase`, `ModelNameCreate`, `ModelNameUpdate`, `ModelNameResponse`

### Common SQLAlchemy Column Types
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship

# Basic columns
id = Column(Integer, primary_key=True, index=True)
name = Column(String, nullable=False, index=True)
description = Column(Text)  # For longer text
price = Column(Float)
is_active = Column(Boolean, default=True)
created_at = Column(DateTime, server_default=func.now())

# Relationships
user_id = Column(Integer, ForeignKey("users.id"))
user = relationship("UserORM", back_populates="items")
```

### Database Session Dependency
Always use `db: Session = Depends(get_db)` in your route functions for automatic session management.

### Error Handling
```python
# Check if item exists
if not item:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Item with id {item_id} not found"
    )
```

## Database Operations

### Queries
```python
# Get all
items = db.query(ModelORM).all()

# Filter
active_items = db.query(ModelORM).filter(ModelORM.is_active == True).all()

# Order by
recent_items = db.query(ModelORM).order_by(ModelORM.created_at.desc()).all()

# Pagination
items = db.query(ModelORM).offset(skip).limit(limit).all()

# Single item
item = db.query(ModelORM).filter(ModelORM.id == item_id).first()
```

### Create/Update/Delete
```python
# Create
db_item = ModelORM(**item_data.dict())
db.add(db_item)
db.commit()
db.refresh(db_item)

# Update
for field, value in update_data.items():
    setattr(db_item, field, value)
db.commit()

# Delete
db.delete(db_item)
db.commit()
```

## Upgrading to PostgreSQL

When you need PostgreSQL, just change the DATABASE_URL:

```python
# In database.py
DATABASE_URL = "postgresql://user:password@localhost/dbname"
# Remove SQLite connect_args
engine = create_engine(DATABASE_URL)
```

Your models and services work unchanged!

## Best Practices

1. Always use `create_tables()` in your service files
2. Use dependency injection with `Depends(get_db)`
3. Handle 404s explicitly with proper error messages
4. Use `exclude_unset=True` for partial updates
5. Always call `db.refresh()` after creating items
6. Use proper HTTP status codes
7. Add indexes to frequently queried columns

## Database File

Your SQLite database will be created as `app_database.db` in your backend directory. This file contains all your data and can be backed up easily.