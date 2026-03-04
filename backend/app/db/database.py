from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import SQL_DATABASE_URL, DATABASE_URL

SQLALCHEMY_DATABASE_URL = DATABASE_URL
engine = create_engine(
    DATABASE_URL, 
    # connect_args={"check_same_thread": False}, only for testing with SQLite3
    echo=True,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()