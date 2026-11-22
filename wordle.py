"""Entry point: a command-line Wordle game."""

from __future__ import annotations

import random
from pathlib import Path

from game import MAX_GUESSES, Game, GameError, load_words
from history import GameHistory

BASE_DIR = Path(__file__).parent
WORDS_FILE = BASE_DIR / "words.txt"
HISTORY_FILE = BASE_DIR / "history.json"


def print_stats(history: GameHistory) -> None:
    """Print the player's overall statistics."""
    print("\n--- Your stats ---")
    print(f"Games played:   {history.total_games}")
    print(f"Wins:           {history.total_wins}")
    print(f"Win percentage: {history.win_percentage:.0f}%")
    print(f"Current streak: {history.current_streak}")
    print(f"Best streak:    {history.best_streak}")


def main() -> None:
    """Run one game of Wordle and record the result."""
    words = load_words(WORDS_FILE)
    secret = random.choice(words)
    game = Game(secret, words)
    history = GameHistory(HISTORY_FILE)

    print("Welcome to Wordle! Guess the 5-letter word.")
    print("✓ = correct spot   ~ = wrong spot   ✗ = not in word\n")

    while not game.is_over:
        print(game)
        try:
            guess = input("\nYour guess: ")
            game.make_guess(guess)
        except GameError as error:
            print(f"\n{error}\n")
        except (EOFError, KeyboardInterrupt):
            print("\nGame abandoned.")
            return
        else:
            print()

    print(game)
    if game.is_won:
        print(f"\nYou got it in {len(game.guesses)}/{MAX_GUESSES}!")
    else:
        print(f"\nThe word was {secret.upper()}")

    history.record_game(game.is_won, len(game.guesses), secret)
    print_stats(history)


if __name__ == "__main__":
    main()
