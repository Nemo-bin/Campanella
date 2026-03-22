from app.infrastructure.db.base import Base
from app.infrastructure.db.session import engine
from sqlalchemy.orm import Session
from .session import SessionLocal

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


__all__ = ["get_db", "init_db"]