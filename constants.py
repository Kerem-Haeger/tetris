import os

# Constants
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
EMPTY = "  "
TICK_RATE = 0.5

TETROMINOES = {
    "I": [
        [1, 1, 1, 1]
        ],
    "O": [
        [1, 1],
        [1, 1]
        ],
    "L": [
        [1, 0],
        [1, 0],
        [1, 1]
        ],
    "J": [
        [0, 1],
        [0, 1],
        [1, 1]
        ],
    "T": [
        [1, 1, 1],
        [0, 1, 0]
        ],
    "S": [
        [0, 1, 1],
        [1, 1, 0]
        ],
    "Z": [
        [1, 1, 0],
        [0, 1, 1]
        ]
}

IS_HEROKU = os.getenv("DYNO") is not None

TETROMINO_EMOJIS = (
    ["🟥", "🟦", "🟨", "🟩", "🟪", "🟧"] if not IS_HEROKU else
    ["[red]▓▓[/red]", "[blue]▓▓[/blue]", "[yellow]▓▓[/yellow]",
        "[green]▓▓[/green]", "[magenta]▓▓[/magenta]", "[cyan]▓▓[/cyan]"]
)

VALID_KEYS = ("KEY_LEFT", "KEY_RIGHT", "KEY_DOWN", "KEY_UP", "q")
