from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    from fastapi import Depends
    from sqlalchemy.orm import Session
    def _get_db():
        db: Session = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    return Depends(_get_db)