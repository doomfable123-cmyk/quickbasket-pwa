from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from datetime import datetime
import os

# Create the base class for declarative models
class Base(DeclarativeBase):
    pass

class Recipe(Base):
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    ingredients = Column(Text, nullable=False)
    instructions = Column(Text, nullable=True)  # Make instructions optional
    source_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_added_to_grocery = Column(DateTime, nullable=True)  # Track when recipe was last added to grocery list

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'ingredients': self.ingredients.split('\n') if self.ingredients else [],
            'instructions': self.instructions.split('\n') if self.instructions else [],
            'source_url': self.source_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_added_to_grocery': self.last_added_to_grocery.isoformat() if self.last_added_to_grocery else None
        }

# Create database engine
def get_base_path():
    """Get the base path for the application, handling PyInstaller bundling"""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller executable
        return sys._MEIPASS
    else:
        # Running as normal Python script
        return os.path.dirname(os.path.abspath(__file__))

import sys
db_path = os.path.join(get_base_path(), 'recipes.db')
engine = create_engine(f'sqlite:///{db_path}')

# Create session factory
Session = sessionmaker(bind=engine)

def init_db():
    """Initialize the database, creating all tables"""
    Base.metadata.create_all(engine)

def get_session():
    """Get a new database session"""
    return Session()