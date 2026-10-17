"""Тесты сохранения и подсчёта через SQLAlchemy."""

from dice_app.db import count_throws, save_throws


def test_save_throws_persists_each_die(session):
    """Каждая кость записывается отдельной строкой."""
    save_throws(session, 6, [2, 6, 2])

    assert count_throws(session) == {6: {2: 2, 6: 1}}


def test_count_throws_returns_empty_mapping_for_empty_database(session):
    """Пустая таблица возвращает пустое отображение."""
    assert count_throws(session) == {}


def test_save_throws_accumulates_multiple_calls(session):
    """Повторные сохранения накапливают результаты."""
    save_throws(session, 4, [1, 4])
    save_throws(session, 4, [4])

    assert count_throws(session) == {4: {1: 1, 4: 2}}
