"""Core Wordle game logic: word loading, guess evaluation and game state."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

MAX_GUESSES = 6
WORD_LENGTH = 5

CORRECT = "correct"
PRESENT = "present"
ABSENT = "absent"

SYMBOLS = {CORRECT: "✓", PRESENT: "~", ABSENT: "✗"}


class GameError(Exception):
    """Base class for all game-related errors."""


class InvalidWordListError(GameError):
    """Raised when the word list file contains an invalid entry."""


class InvalidGuessError(GameError):
    """Raised when a guess has the wrong length or is not in the word list."""


class GameOverError(GameError):
    """Raised when a guess is made after the game has finished."""


def load_words(path: str | Path) -> list[str]:
    """Load words from a file, validating that each is WORD_LENGTH letters."""
    words: list[str] = []
    with open(path, encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            word = line.strip().lower()
            if not word:
                continue
            if len(word) != WORD_LENGTH or not word.isalpha():
                raise InvalidWordListError(
                    f"Line {line_number}: {word!r} is not a "
                    f"{WORD_LENGTH}-letter word."
                )
            words.append(word)
    return words


class GuessResult:
    """The outcome of a single guess.

    Stores the guessed word and one status per letter, each being
    ``correct`` (right letter, right spot), ``present`` (right letter,
    wrong spot) or ``absent`` (letter not in the secret word).
    """

    def __init__(self, guess: str, statuses: list[str]) -> None:
        self.guess = guess.lower()
        self.statuses = statuses

    @property
    def is_correct(self) -> bool:
        """Return True if every letter is in the correct position."""
        return all(status == CORRECT for status in self.statuses)

    def __str__(self) -> str:
        letters = "  ".join(self.guess.upper())
        symbols = "  ".join(SYMBOLS[status] for status in self.statuses)
        return f"{letters}\n{symbols}"


def evaluate_guess(secret: str, guess: str) -> GuessResult:
    """Compare a guess with the secret word and return a GuessResult.

    Works in two passes so duplicate letters are handled correctly:

    1. Mark exact-position matches as ``correct`` and count the secret
       letters that are still unmatched.
    2. For the remaining letters, mark ``present`` only while an unmatched
       copy of that letter is left in the secret; otherwise ``absent``.

    Correct matches therefore always take priority over present ones.
    """
    secret = secret.lower()
    guess = guess.lower()
    statuses = [ABSENT] * WORD_LENGTH

    remaining: Counter[str] = Counter()
    for i in range(WORD_LENGTH):
        if guess[i] == secret[i]:
            statuses[i] = CORRECT
        else:
            remaining[secret[i]] += 1

    for i in range(WORD_LENGTH):
        if statuses[i] == CORRECT:
            continue
        if remaining[guess[i]] > 0:
            statuses[i] = PRESENT
            remaining[guess[i]] -= 1

    return GuessResult(guess, statuses)


class Game:
    """A single game of Wordle: tracks the secret word and all guesses."""

    def __init__(self, secret: str, words: list[str]) -> None:
        self.secret = secret.lower()
        self.words = {word.lower() for word in words}
        self.guesses: list[GuessResult] = []

    @property
    def is_won(self) -> bool:
        """Return True if the most recent guess was the secret word."""
        return bool(self.guesses) and self.guesses[-1].is_correct

    @property
    def is_over(self) -> bool:
        """Return True if the game was won or all attempts were used."""
        return self.is_won or len(self.guesses) >= MAX_GUESSES

    @property
    def attempts_left(self) -> int:
        """Return the number of guesses remaining."""
        return MAX_GUESSES - len(self.guesses)

    def make_guess(self, word: str) -> GuessResult:
        """Validate and record a guess, returning its GuessResult.

        Raises:
            GameOverError: if the game has already finished.
            InvalidGuessError: if the guess has the wrong length or is not
                in the word list.
        """
        if self.is_over:
            raise GameOverError("The game is already over.")
        word = word.strip().lower()
        if len(word) != WORD_LENGTH:
            raise InvalidGuessError(
                f"Guess must be exactly {WORD_LENGTH} letters long."
            )
        if word not in self.words:
            raise InvalidGuessError(f"'{word}' is not in the word list.")

        result = evaluate_guess(self.secret, word)
        self.guesses.append(result)
        return result

    def __str__(self) -> str:
        blocks = [str(result) for result in self.guesses]
        blocks.append(f"Attempts remaining: {self.attempts_left}")
        return "\n\n".join(blocks)
