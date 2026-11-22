"""Persistent record of completed games and the stats derived from it."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class GameHistory:
    """Loads, stores and summarises completed games in a JSON file."""

    def __init__(self, path: str | Path = "history.json") -> None:
        self.path = Path(path)
        self.records: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        """Read records from disk, creating an empty file if needed."""
        if not self.path.exists():
            self._save()
            return
        try:
            with open(self.path, encoding="utf-8") as file:
                self.records = json.load(file)
        except json.JSONDecodeError:
            self.records = []

    def _save(self) -> None:
        """Write all records to disk."""
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(self.records, file, indent=2)

    def record_game(self, won: bool, attempts: int, word: str) -> None:
        """Add a completed game and persist it."""
        self.records.append({"won": won, "attempts": attempts, "word": word})
        self._save()

    @property
    def total_games(self) -> int:
        """Total number of games played."""
        return len(self.records)

    @property
    def total_wins(self) -> int:
        """Total number of games won."""
        return sum(1 for record in self.records if record["won"])

    @property
    def win_percentage(self) -> float:
        """Percentage of games won (0.0 if no games played)."""
        if not self.records:
            return 0.0
        return self.total_wins / self.total_games * 100

    @property
    def current_streak(self) -> int:
        """Consecutive wins ending at the most recent game.

        Walk backwards from the latest game and count wins until the first
        loss; a loss as the latest game gives a streak of 0.
        """
        streak = 0
        for record in reversed(self.records):
            if not record["won"]:
                break
            streak += 1
        return streak

    @property
    def best_streak(self) -> int:
        """Longest run of consecutive wins ever recorded."""
        best = current = 0
        for record in self.records:
            current = current + 1 if record["won"] else 0
            best = max(best, current)
        return best
