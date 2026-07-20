from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

# Bare load_dotenv() searches from the process CWD. lswsgi/Passenger do not
# guarantee the CWD is the project root, so point at the .env explicitly or
# DATABASE_URL comes back None and create_engine() raises at import time.
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        f"DATABASE_URL is not set. Looked for a .env file at: {ENV_PATH}"
    )

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