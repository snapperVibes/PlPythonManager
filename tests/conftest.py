""" Setup file the test runner 'pytest' uses """
import os
from typing import Generator, Any

import pytest
from sqlalchemy import Column, INT, TEXT, BOOLEAN, ForeignKey, create_engine as _create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import relationship, sessionmaker, declarative_base


def create_test_engine() -> Engine:
    return _create_engine(
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('POSTGRES_SERVER')}:"
        f"{os.getenv('POSTGRES_PORT')}/"
        f"{os.getenv('POSTGRES_DB')}",
        future=True,
        echo=True,
    )


@pytest.fixture
def db() -> Generator:
    engine = create_test_engine()
    Base = declarative_base(bind=engine)
    try:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        # register_tables(tables)
        Base.metadata.create_all()
        yield SessionLocal()
    finally:
        Base.metadata.drop_all()


@pytest.fixture
def db__users_and_items() -> Generator:
    engine = create_test_engine()
    Base = declarative_base(bind=engine)
    try:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        class Items(Base):
            __tablename__ = "items"
            id = Column(INT, primary_key=True, index=True)
            title = Column(TEXT, index=True)
            description = Column(TEXT, index=True)
            owner_id = Column(INT, ForeignKey("users.id"))
            owner = relationship("User", back_populates="items")

        class Users(Base):
            __tablename__ = "users"
            id = Column(INT, primary_key=True, index=True)
            full_name = Column(TEXT, index=True)
            email = Column(TEXT, unique=True, index=True, nullable=False)
            hashed_password = Column(TEXT, nullable=False)
            is_active = Column(BOOLEAN, default=True)
            is_superuser = Column(BOOLEAN, default=False)
            items = relationship("Items", back_populates="owner")

        Base.metadata.create_all()
        db = SessionLocal()
        yield db
    finally:
        Base.metadata.drop_all()
