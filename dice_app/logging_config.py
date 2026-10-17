"""Настройка файлового логирования утилиты."""

import logging
from pathlib import Path


def setup_logging() -> None:
    """Настроить один UTF-8 файловый обработчик в текущей директории."""
    logger = logging.getLogger("dice_app")
    log_path = (Path.cwd() / "app.log").resolve()
    for handler in logger.handlers[:]:
        if getattr(handler, "_dice_app_file_handler", False):
            if Path(handler.baseFilename) == log_path:
                return
            logger.removeHandler(handler)
            handler.close()

    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler._dice_app_file_handler = True  # type: ignore[attr-defined]
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.addHandler(handler)
