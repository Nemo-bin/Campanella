from app.infrastructure.db.base import Base
from app.infrastructure.db.session import engine

def init_db():
    Base.metadata.create_all(bind=engine)