"""Бизнес-логика бросков и подготовки статистики."""

import random
from collections.abc import Mapping, Sequence
from typing import Literal

View = Literal["abs", "rel"] | None


def roll_dice(count: int, sides: int) -> list[int]:
    if count < 1:
        raise ValueError("--count должно быть не меньше 1")
    if sides < 2:
        raise ValueError("--sides должно быть не меньше 2")
    return [random.randint(1, sides) for _ in range(count)]


def format_roll(values: Sequence[int]) -> str:
    return f"🎲 {list(values)}\nСумма: {sum(values)}"


def format_stat(count: int, total: int, view: View) -> str:
    percent = count / total * 100 if total else 0
    if view == "abs":
        return f"{count}"
    if view == "rel":
        return f"{percent:.1f}%"
    return f"{count} ({percent:.1f}%)"


def build_stats_lines(counts: Mapping[int, Mapping[int, int]], view: View) -> list[str]:
    lines: list[str] = []
    for sides in sorted(counts):
        face_counts = counts[sides]
        total = sum(face_counts.values())
        faces = ", ".join(
            f"{value} — {format_stat(face_counts.get(value, 0), total, view)}"
            for value in range(1, sides + 1)
        )
        lines.append(f"d{sides}: {faces}")
    return lines
