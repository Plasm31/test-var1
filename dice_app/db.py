"""Модель и операции хранения результатов бросков в SQLite."""

import os
from collections.abc import Iterator, Sequence
from contextlib import contextmanager

from sqlalchemy import create_engine, func, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    """Базовый класс моделей SQLAlchemy."""


class Throw(Base):
    __tablename__ = "throws"

    id: Mapped[int] = mapped_column(primary_key=True)
    sides: Mapped[int]
    value: Mapped[int]


def get_engine() -> Engine:
    url = os.environ.get("DICE_DB_URL", "sqlite:///stats.db")
    return create_engine(url)


@contextmanager
def get_session() -> Iterator[Session]:
    engine = get_engine()
    try:
        Base.metadata.create_all(engine)
        with Session(engine) as session:
            yield session
    finally:
        engine.dispose()


def save_throws(session: Session, sides: int, values: Sequence[int]) -> None:
    try:
        session.add_all(Throw(sides=sides, value=value) for value in values)
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise


def count_throws(session: Session) -> dict[int, dict[int, int]]:
    rows = session.execute(
        select(Throw.sides, Throw.value, func.count())
        .group_by(Throw.sides, Throw.value)
        .order_by(Throw.sides, Throw.value)
    ).all()
    counts: dict[int, dict[int, int]] = {}
    for sides, value, count in rows:
        counts.setdefault(sides, {})[value] = count
    return counts
