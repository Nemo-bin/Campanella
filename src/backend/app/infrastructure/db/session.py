from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os

host = os.getenv("DB_HOST", "db"),
port = os.getenv("DB_PORT", "5432"),
dbname = os.getenv("DB_NAME", "appdb"),
user = os.getenv("DB_USER", "appuser"),
password = os.getenv("DB_PASSWORD", "password")

DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping = True
    )

SessionLocal = sessionmaker(
    bind = engine,
    autoflush = False,
    autocommit = False
)