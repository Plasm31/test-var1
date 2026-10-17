"""Тесты бизнес-логики бросков и статистики."""

import pytest

from dice_app.logic import build_stats_lines, format_roll, format_stat, roll_dice


def test_roll_dice_returns_count_values_in_range(monkeypatch):
    """Результаты имеют нужную длину и принадлежат диапазону граней."""
    monkeypatch.setattr("dice_app.logic.random.randint", lambda low, high: high)

    assert roll_dice(3, 20) == [20, 20, 20]


@pytest.mark.parametrize(
    ("count", "sides", "message"),
    [
        (0, 6, "--count должно быть не меньше 1"),
        (-1, 6, "--count должно быть не меньше 1"),
        (1, 1, "--sides должно быть не меньше 2"),
        (1, 0, "--sides должно быть не меньше 2"),
        (1, -2, "--sides должно быть не меньше 2"),
    ],
)
def test_roll_dice_rejects_invalid_arguments(count, sides, message):
    """Некорректные параметры приводят к ValueError с подсказкой."""
    with pytest.raises(ValueError, match=message):
        roll_dice(count, sides)


def test_roll_dice_accepts_minimum_count_and_sides(monkeypatch):
    """Минимальные допустимые значения работают."""
    monkeypatch.setattr("dice_app.logic.random.randint", lambda low, high: low)

    assert roll_dice(1, 2) == [1]


def test_format_roll_shows_values_and_sum():
    """Результат форматируется с суммой всех костей."""
    assert format_roll([12, 1, 20]) == "🎲 [12, 1, 20]\nСумма: 33"


@pytest.mark.parametrize(
    ("count", "total", "view", "expected"),
    [
        (4, 30, "abs", "4"),
        (4, 30, "rel", "13.3%"),
        (4, 30, None, "4 (13.3%)"),
        (1, 0, "rel", "0.0%"),
        (1, 8, "rel", "12.5%"),
    ],
)
def test_format_stat_formats_each_view(count, total, view, expected):
    """Форматируются абсолютные значения, проценты и округление."""
    assert format_stat(count, total, view) == expected


def test_build_stats_lines_includes_missing_faces_and_sorts_sides():
    """Частоты включают нулевые грани и сортируются по числу граней."""
    counts = {6: {1: 2, 3: 1}, 2: {2: 1}}

    assert build_stats_lines(counts, "abs") == [
        "d2: 1 — 0, 2 — 1",
        "d6: 1 — 2, 2 — 0, 3 — 1, 4 — 0, 5 — 0, 6 — 0",
    ]


def test_build_stats_lines_formats_relative_and_combined_views():
    """Проценты рассчитываются от всех костей с таким числом граней."""
    counts = {2: {1: 1, 2: 2}}

    assert build_stats_lines(counts, "rel") == ["d2: 1 — 33.3%, 2 — 66.7%"]
    assert build_stats_lines(counts, None) == ["d2: 1 — 1 (33.3%), 2 — 2 (66.7%)"]


def test_build_stats_lines_returns_empty_list_for_empty_data():
    """Для пустой статистики строки не создаются."""
    assert build_stats_lines({}, None) == []
