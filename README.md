Wordle CLI

A command-line version of Wordle written in Python. You have 6 attempts to guess a hidden 5-letter word. After each guess the game shows which letters are correct, which are in the word but misplaced, and which are not in the word at all. Results are saved between sessions so you can track your win streak.

Features
6 attempts to guess a 5-letter word chosen at random from words.txt
Clear feedback for every letter
Correct handling of duplicate letters
Invalid guesses (wrong length, not in the word list) do not use up an attempt
Persistent history: games played, wins, win percentage, current streak and best streak
Test suite written with pytest, linted with ruff
How to Read the Feedback
Symbol	Meaning
✓	Correct letter, correct position
~	Letter is in the word, but in the wrong position
✗	Letter is not in the word

Example (secret word: SPINE):

S  P  E  E  D
✓  ✓  ~  ✗  ✗

SPINE has only one E, so the first E in SPEED is marked present and the second is marked absent.

Project Structure
wordle/
├── words.txt          # word list (60 five-letter words, one per line)
├── game.py            # constants, exceptions, load_words, GuessResult, evaluate_guess, Game
├── history.py         # GameHistory class (reads/writes history.json)
├── wordle.py          # entry point and game loop
├── requirements.txt   # pytest, ruff
├── README.md
└── tests/
    └── test_game.py   # test suite

history.json is created automatically the first time you play.

Setup

Requires Python 3.9 or newer.

bash
cd wordle

# create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# install dependencies
pip install -r requirements.txt
Run the Game
bash
python wordle.py

Type a 5-letter word and press Enter. Keep guessing until you win or use all 6 attempts. At the end you will see the result and your stats.

Run the Tests and Linter
bash
pytest -v
ruff check .

The tests cover:

evaluate_guess with a fully correct guess, a mix of letter results, and duplicate letters
Game.make_guess rejecting words not in the list, wrong-length words, and guesses after the game is over
Game.is_won after a correct guess and Game.is_over after 6 failed guesses
GameHistory streak calculations and saving/loading from disk
Design Overview

GuessResult and evaluate_guess evaluate_guess(secret, guess) works in two passes. The first pass marks exact-position matches as correct and counts the secret's unmatched letters. The second pass marks a remaining letter as present only while an unmatched copy of it is left in that count; otherwise it is absent. This means correct matches always take priority and extra duplicate letters are marked absent.

Game Holds the secret word, the word list and all guesses made. make_guess validates the guess, then records and returns a GuessResult. is_won and is_over are properties. MAX_GUESSES and WORD_LENGTH are constants defined once in game.py.

Exceptions All custom errors inherit from GameError:

InvalidGuessError – wrong length or word not in the list
GameOverError – a guess was made after the game ended
InvalidWordListError – a line in words.txt is not a 5-letter word

The game loop catches GameError, prints the message and lets the player try again.

GameHistory Stores each completed game as {"won": bool, "attempts": int, "word": str} in history.json. current_streak walks backwards from the most recent game and counts consecutive wins until the first loss. best_streak scans the full history and keeps the longest run of wins.
