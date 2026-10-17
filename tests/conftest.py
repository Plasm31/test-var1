"""Общие фикстуры с изолированной SQLite-базой в памяти."""

from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from dice_app.db import Base


@pytest.fixture
def session() -> Generator[Session, None, None]:
    """Создать чистую SQLite-сессию для одного теста."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db_session:
        yield db_session
    engine.dispose()
