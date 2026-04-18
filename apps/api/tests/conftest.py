from __future__ import annotations

from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.models.entities import Exercise, User
from app.services.auth import hash_password


@pytest.fixture
def test_engine(tmp_path):
    database_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{database_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    with TestingSessionLocal() as session:
        session.add(User(username="admin", password_hash=hash_password("admin")))
        session.add_all(
            [
                Exercise(name="Bench Press", modality="strength", default_measure_type="reps_weight"),
                Exercise(name="Running", modality="cardio", default_measure_type="distance"),
            ]
        )
        session.commit()
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(test_engine) -> Generator[Session, None, None]:
    TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False, future=True)
    with TestingSessionLocal() as session:
        yield session
