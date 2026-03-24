from sqlalchemy.orm import Session
from app.infrastructure.db.session import SessionLocal

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()