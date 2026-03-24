from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os
import time

host = os.getenv("DB_HOST", "db")
port = os.getenv("DB_PORT", "5432")
dbname = os.getenv("DB_NAME", "appdb")
user = os.getenv("DB_USER", "appuser")
password = os.getenv("DB_PASSWORD", "password")

DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

for i in range(10):
    try:
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping = True
            )
        engine.connect()
        print("Connected to Postgres")
        break
    except Exception:
        print("Postgres not ready!")
        time.sleep(3)
else:
    raise Exception("Could not connect to Postgres")

SessionLocal = sessionmaker(
    bind = engine,
    autoflush = False,
    autocommit = False
)