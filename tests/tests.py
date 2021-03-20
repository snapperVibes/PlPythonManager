import logging
import os
from typing import Generator

import pytest
import sqlalchemy
# Tenacity allows code to retry until it works
from sqlalchemy.orm import sessionmaker
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


###################################################################################################
# Setup database
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

engine = sqlalchemy.create_engine(
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}",
    future=True,
    echo=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


###################################################################################################
# Fixtures
@pytest.fixture()
def db() -> Generator:
    yield SessionLocal()


###################################################################################################
max_tries = 15
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.ERROR),
)
def setup_database() -> None:
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
    except Exception as e:
        logger.warning(e)
        raise e


def test_hello():
    assert True


def test_test_setup():
    setup_database()

if __name__ == "__main__":
    pytest.main()
