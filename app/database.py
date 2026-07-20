from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()



DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    url = DATABASE_URL,
    # Passenger forks worker processes from a preloaded parent. A pooled MySQL
    # socket opened at import time would be inherited by every child, desyncing
    # the wire protocol and hanging queries. pre_ping also drops connections
    # that MySQL closed on its own (wait_timeout) instead of erroring on them.
    pool_pre_ping = True,
    pool_recycle = 280,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()

def get_db():
    db = SessionLocal()

    try: 
        yield db
    finally:
        db.close()