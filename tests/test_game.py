"""Tests for the Wordle game logic and history."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game import (
    ABSENT,
    CORRECT,
    MAX_GUESSES,
    PRESENT,
    Game,
    GameOverError,
    InvalidGuessError,
    evaluate_guess,
)
from history import GameHistory

WORDS = ["spine", "speed", "crane", "apple", "brave", "house", "water"]


@pytest.fixture
def game() -> Game:
    return Game("spine", WORDS)


def test_evaluate_fully_correct() -> None:
    result = evaluate_guess("spine", "spine")
    assert result.statuses == [CORRECT] * 5
    assert result.is_correct


def test_evaluate_mixed() -> None:
    result = evaluate_guess("spine", "crane")
    assert result.statuses == [ABSENT, ABSENT, ABSENT, CORRECT, CORRECT]
    result = evaluate_guess("spine", "pines")
    assert result.statuses == [PRESENT, PRESENT, PRESENT, PRESENT, PRESENT]


def test_evaluate_duplicate_letters() -> None:
    result = evaluate_guess("spine", "speed")
    assert result.statuses == [CORRECT, CORRECT, PRESENT, ABSENT, ABSENT]


def test_correct_takes_priority_over_present() -> None:
    result = evaluate_guess("speed", "geese")
    assert result.statuses == [ABSENT, PRESENT, CORRECT, PRESENT, ABSENT]


def test_str_output() -> None:
    result = evaluate_guess("spine", "speed")
    assert str(result) == "S  P  E  E  D\n✓  ✓  ~  ✗  ✗"


def test_guess_not_in_word_list(game: Game) -> None:
    with pytest.raises(InvalidGuessError):
        game.make_guess("zzzzz")


def test_guess_wrong_length(game: Game) -> None:
    with pytest.raises(InvalidGuessError):
        game.make_guess("cat")


def test_invalid_guess_does_not_use_attempt(game: Game) -> None:
    with pytest.raises(InvalidGuessError):
        game.make_guess("zzzzz")
    assert game.attempts_left == MAX_GUESSES


def test_is_won_after_correct_guess(game: Game) -> None:
    game.make_guess("spine")
    assert game.is_won
    assert game.is_over


def test_is_over_after_six_failed_guesses(game: Game) -> None:
    for _ in range(MAX_GUESSES):
        game.make_guess("crane")
    assert game.is_over
    assert not game.is_won


def test_guess_after_game_over(game: Game) -> None:
    game.make_guess("spine")
    with pytest.raises(GameOverError):
        game.make_guess("crane")


def test_history_streaks(tmp_path: Path) -> None:
    history = GameHistory(tmp_path / "history.json")
    for won in [True, True, False, True, True, True]:
        history.record_game(won, 4, "spine")
    assert history.total_games == 6
    assert history.total_wins == 5
    assert history.current_streak == 3
    assert history.best_streak == 3
    assert round(history.win_percentage) == 83


def test_history_persists(tmp_path: Path) -> None:
    path = tmp_path / "history.json"
    GameHistory(path).record_game(True, 3, "crane")
    assert GameHistory(path).total_games == 1
