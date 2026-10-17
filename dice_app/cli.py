"""Click-команды утилиты dice."""

import logging

import click
from sqlalchemy.exc import SQLAlchemyError

from dice_app.db import count_throws, get_session, save_throws
from dice_app.logging_config import setup_logging
from dice_app.logic import build_stats_lines, format_roll, roll_dice

logger = logging.getLogger("dice_app")


@click.group()
def cli() -> None:
    setup_logging()
    logger.info("Запуск CLI")


@cli.command()
@click.option("--count", "-c", type=int, default=1, show_default=True)
@click.option("--sides", "-s", type=int, default=6, show_default=True)
def roll(count: int, sides: int) -> None:
    logger.info("Команда roll: count=%d, sides=%d", count, sides)
    try:
        values = roll_dice(count, sides)
    except ValueError as error:
        logger.warning("Ошибка валидации параметров roll: %s", error)
        raise click.BadParameter(str(error)) from error

    output = format_roll(values)
    click.echo(output)
    logger.info("Результат броска: %s", output.replace("\n", " | "))

    try:
        with get_session() as session:
            save_throws(session, sides, values)
    except (OSError, SQLAlchemyError) as error:
        logger.exception("Ошибка базы данных при сохранении броска")
        raise click.ClickException(f"Ошибка базы данных: {error}") from error
    logger.info("Сохранено записей: %d", len(values))


@cli.command()
@click.option(
    "--view",
    type=click.Choice(["abs", "rel"]),
    default=None,
    help="Вид статистики: abs — числа, rel — проценты.",
)
def stats(view: str | None) -> None:
    logger.info("Команда stats: view=%s", view)
    try:
        with get_session() as session:
            counts = count_throws(session)
    except (OSError, SQLAlchemyError) as error:
        logger.exception("Ошибка базы данных при запросе статистики")
        raise click.ClickException(f"Ошибка базы данных: {error}") from error

    if not counts:
        click.echo("Статистики пока нет")
        return
    for line in build_stats_lines(counts, view):
        click.echo(line)
