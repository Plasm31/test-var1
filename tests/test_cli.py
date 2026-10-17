"""Проверки пользовательского интерфейса Click."""

from contextlib import contextmanager

import pytest
from click.testing import CliRunner

import dice_app.cli as cli_module
from dice_app.cli import cli
from dice_app.db import count_throws, save_throws


@pytest.fixture
def cli_session(monkeypatch, tmp_path, session):
    """Изолировать CLI в каталоге теста и подключить БД в памяти."""
    monkeypatch.chdir(tmp_path)

    @contextmanager
    def memory_session():
        yield session

    monkeypatch.setattr(cli_module, "get_session", memory_session)
    return session


def test_roll_command_prints_result_and_saves_throws(monkeypatch, cli_session):
    """Команда выводит бросок и сохраняет каждую кость."""
    monkeypatch.setattr(cli_module, "roll_dice", lambda count, sides: [2, 6, 2])

    result = CliRunner().invoke(cli, ["roll", "-c", "3", "-s", "6"])

    assert result.exit_code == 0
    assert result.output == "🎲 [2, 6, 2]\nСумма: 10\n"
    assert count_throws(cli_session) == {6: {2: 2, 6: 1}}


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        (["roll", "-c", "0"], "--count должно быть не меньше 1"),
        (["roll", "-s", "1"], "--sides должно быть не меньше 2"),
    ],
)
def test_roll_command_reports_invalid_parameters(arguments, message, cli_session):
    """Ошибки параметров имеют ненулевой код и понятный текст."""
    result = CliRunner().invoke(cli, arguments)

    assert result.exit_code != 0
    assert message in result.output


def test_stats_command_reports_empty_database(cli_session):
    """Пустая база сопровождается понятным сообщением."""
    result = CliRunner().invoke(cli, ["stats"])

    assert result.exit_code == 0
    assert result.output == "Статистики пока нет\n"


@pytest.mark.parametrize(
    ("arguments", "expected"),
    [
        (["stats", "--view", "abs"], "d2: 1 — 1, 2 — 2\n"),
        (["stats", "--view", "rel"], "d2: 1 — 33.3%, 2 — 66.7%\n"),
        (["stats"], "d2: 1 — 1 (33.3%), 2 — 2 (66.7%)\n"),
    ],
)
def test_stats_command_prints_requested_view(arguments, expected, cli_session):
    """Команда поддерживает оба отдельных вида и объединённый вывод."""
    save_throws(cli_session, 2, [1, 2, 2])

    result = CliRunner().invoke(cli, arguments)

    assert result.exit_code == 0
    assert result.output == expected


def test_roll_command_converts_database_errors_to_click_error(monkeypatch, cli_session):
    """Ошибка файла БД не показывает traceback пользователю."""
    monkeypatch.setattr(cli_module, "roll_dice", lambda count, sides: [5])

    def fail_session():
        raise OSError("нет доступа к файлу")

    monkeypatch.setattr(cli_module, "get_session", fail_session)
    result = CliRunner().invoke(cli, ["roll"])

    assert result.exit_code == 1
    assert "🎲 [5]" in result.output
    assert "Сумма: 5" in result.output
    assert "Ошибка базы данных: нет доступа к файлу" in result.output
    assert "Traceback" not in result.output
