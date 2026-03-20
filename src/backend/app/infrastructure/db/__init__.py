from app.infrastructure.db.base import Base
from app.infrastructure.db.session import engine

from app.infrastructure.db.models import user_model
from app.infrastructure.db.models import refresh_token_model


def init_db():
    Base.metadata.create_all(bind=engine)