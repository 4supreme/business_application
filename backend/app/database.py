from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Для MVP используем SQLite (файл рядом с проектом)
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # нужно для SQLite в одном процессе
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
