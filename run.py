import os
import sys
import time
import random
import copy
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from blessed import Terminal
from highscores import get_high_scores, submit_score

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

console = Console()
term = Terminal()


class Piece:
    def __init__(self, shape_name, shape, emoji):
        self.shape_name = shape_name
        self.shape = shape
        self.emoji = emoji
        self.row = 0
        self.col = BOARD_WIDTH // 2 - len(shape[0]) // 2

    def get_coords(self):
        """
        Return a list of (row, col) coordinates for all blocks in the piece
        based on its current position.
        """
        coords = []
        for r, row in enumerate(self.shape):
            for c, val in enumerate(row):
                if val:
                    coords.append((self.row + r, self.col + c))
        return coords

    def rotate(self, board):
        """
        Attempt to rotate the piece clockwise. Only applies
        if no collision occurs.
        """
        # Rotate shape clockwise
        rotated = [list(row) for row in zip(*self.shape[::-1])]

        # Get width and height of rotated shape
        rotated_width = len(rotated[0])
        rotated_height = len(rotated)

        # Check if rotation would cause collision or go off-grid
        for r in range(rotated_height):
            for c in range(rotated_width):
                if rotated[r][c]:
                    board_r = self.row + r
                    board_c = self.col + c
                    if (board_r >= BOARD_HEIGHT or
                        board_c < 0 or
                        board_c >= BOARD_WIDTH or
                            board[board_r][board_c] != EMPTY):
                        return  # Invalid rotation, so cancel

        self.shape = rotated


def show_welcome_screen():
    console.clear()
    welcome_text = """[bold magenta]
Welcome to Tetris!
[/bold magenta]

[bold white]Controls:[/bold white]
← Move Left
→ Move Right
↓ Soft Drop
↑ Rotate
Q Quit

Press [bold green]Enter[/bold green] to begin...
"""
    console.print(Panel(
        welcome_text,
        title="TETRIS",
        border_style="cyan",
        width=60
        ), justify="center")

    # Wait for Enter key
    with term.cbreak():
        while True:
            key = term.inkey()
            if key.name == "KEY_ENTER":
                console.clear()
                break


def new_random_piece():
    """
    Generate a new random Tetromino piece with a random shape and color.
    """
    name = random.choice(list(TETROMINOES.keys()))
    shape = TETROMINOES[name]
    block = random.choice(TETROMINO_EMOJIS)
    return Piece(name, shape, block)


def create_board():
    """
    Create and return an empty game board with predefined width and height.
    """
    return [[EMPTY for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]


def can_move(piece, board, dr=1, dc=0):
    """
    Check if a piece can move in the specified direction without collisions.
    """
    for r, c in piece.get_coords():
        nr, nc = r + dr, c + dc
        if nr >= BOARD_HEIGHT or nc < 0 or nc >= BOARD_WIDTH:
            return False
        if board[nr][nc] != EMPTY:
            return False
    return True


def lock_piece(piece, board):
    """ Permanently place a piece onto the board at its current position. """
    for r, c in piece.get_coords():
        if 0 <= r < BOARD_HEIGHT and 0 <= c < BOARD_WIDTH:
            board[r][c] = piece.emoji


def add_piece_to_board(piece, board):
    """ Create a copy of the board with the active piece visually added. """
    temp_board = copy.deepcopy(board)
    for r, c in piece.get_coords():
        if 0 <= r < BOARD_HEIGHT and 0 <= c < BOARD_WIDTH:
            temp_board[r][c] = piece.emoji
    return temp_board


def render_board(board):
    """
    Convert the board's 2D array into a string representation for display.
    """
    return "\n".join("".join(row) for row in board)


def render_next_piece(piece):
    """ Generate the string preview of the upcoming Tetromino piece. """
    lines = []
    for row in piece.shape:
        line = ""
        for val in row:
            line += piece.emoji if val else EMPTY
        lines.append(line)
    return "\n".join(lines)


def render_score_panel(score):
    """ Create a Rich panel displaying the current score. """
    return Panel(f"[bold green]{score}[/bold green]", title="SCORE", width=20)


def render_next_panel(next_piece):
    """ Create a Rich panel showing the next upcoming Tetromino. """
    return Panel(render_next_piece(next_piece), title="NEXT", width=20)


def render_controls_panel():
    """ Create a Rich panel listing available control key bindings. """
    controls_text = (
        "[bold]←[/bold] Move Left\n"
        "[bold]→[/bold] Move Right\n"
        "[bold]↓[/bold] Soft Drop\n"
        "[bold]↑[/bold] Rotate\n"
        "[bold]Q[/bold] Quit"
    )
    return Panel(controls_text, title="CONTROLS", width=20)


def clear_lines(board, live, score, next_piece, high_scores_text):
    """
    Animates and clears full lines with a wiping effect.
    Returns the updated board and number of lines cleared.
    """
    next_panel = render_next_panel(next_piece)
    score_panel = render_score_panel(score)
    controls_panel = render_controls_panel()
    high_scores_panel = Panel(high_scores_text, title="LEADERBOARD", width=24)

    full_rows = [
                i for i, row in enumerate(board) if
                all(cell != EMPTY for cell in row)
                ]
    lines_cleared = len(full_rows)

    if lines_cleared == 0:
        return board, 0

    temp_board = copy.deepcopy(board)

    for idx in full_rows:
        for col in range(BOARD_WIDTH):
            temp_board[idx][col] = "[white]▓▓[/white]"

            # Only the game board is changing
            game_panel = Panel(
                render_board(temp_board),
                title="TETRIS",
                border_style="bold red",
                width=24
                )

            layout = Layout()
            layout.split_row(
                Layout(game_panel, name="game", size=24),
                Layout(name="sidebar")
            )

            layout["sidebar"].split_column(
                Layout(next_panel),
                Layout(score_panel),
                Layout(controls_panel),
                Layout(high_scores_panel)
            )

            live.update(Panel(layout, height=24, width=80, border_style="dim"))
            time.sleep(0.02)

    # Remove the full rows
    new_board = [row for i, row in enumerate(board) if i not in full_rows]
    while len(new_board) < BOARD_HEIGHT:
        new_board.insert(0, [EMPTY for _ in range(BOARD_WIDTH)])

    return new_board, lines_cleared


def game_logic():
    while True:  # Outer loop to support restarting the game
        board = create_board()
        score = 0
        level = 1
        lines_total = 0
        tick_rate = 0.5
        current_piece = new_random_piece()
        next_piece = new_random_piece()
        restart_requested = False

        high_scores_text = get_high_scores()

        with term.cbreak(), Live(
            console=console,
            refresh_per_second=10
        ) as live:
            while True:  # Inner game loop
                key = term.inkey(timeout=tick_rate)

                # Handle key input
                if key.name == "KEY_LEFT":
                    if can_move(current_piece, board, dr=0, dc=-1):
                        current_piece.col -= 1

                elif key.name == "KEY_RIGHT":
                    if can_move(current_piece, board, dr=0, dc=1):
                        current_piece.col += 1

                elif key.name == "KEY_DOWN":
                    if can_move(current_piece, board, dr=1):
                        current_piece.row += 1

                elif key.name == "KEY_UP":
                    current_piece.rotate(board)

                elif key == "q":
                    live.update(Panel(f"Quit! Final score: {score}"))
                    return  # Exit the game

                # Apply gravity
                if can_move(current_piece, board, dr=1):
                    current_piece.row += 1
                else:
                    lock_piece(current_piece, board)
                    score += 10

                    board, lines = clear_lines(
                        board,
                        live,
                        score,
                        next_piece,
                        high_scores_text
                    )
                    score += lines * 100
                    lines_total += lines

                    if lines_total >= level * 5:
                        level += 1

                    tick_rate = max(0.1, 0.5 - (level - 1) * 0.05)

                    current_piece = next_piece
                    next_piece = new_random_piece()

                    if not can_move(current_piece, board, dr=0):
                        # Display final Game Over panel
                        game_over_panel = Panel(
                            f"[bold red]Game Over![/bold red]\n"
                            f"[bold]Score:[/bold] {score}\n\n"
                            f"(press Enter below to submit your name)",
                            title="GAME OVER",
                            border_style="red",
                            width=40
                        )
                        live.update(game_over_panel)
                        break

                # Render the updated board each frame
                temp_board = add_piece_to_board(current_piece, board)
                next_panel = render_next_panel(next_piece)
                score_panel = render_score_panel(score)
                controls_panel = render_controls_panel()
                high_scores_panel = Panel(
                    high_scores_text,
                    title="LEADERBOARD",
                    width=24
                )
                game_panel = Panel(
                    render_board(temp_board),
                    title="TETRIS",
                    border_style="bold red",
                    width=24
                )
                layout = Layout()
                layout.split_row(
                    Layout(game_panel, name="game", size=24),
                    Layout(name="sidebar", size=28),
                    Layout(name="leaderboard")
                )

                layout["sidebar"].split_column(
                    Layout(next_panel),
                    Layout(score_panel),
                    Layout(controls_panel)
                )

                layout["leaderboard"].update(high_scores_panel)

                live.update(Panel(
                    layout,
                    height=24,
                    width=80,
                    border_style="dim")
                )

        # Prompt for name while leaderboard and game screen are still visible
        console.print("""
\n[bold cyan]Enter your name for the leaderboard:[/bold cyan]
(max 10 characters, or press Enter to skip)
                    """)
        name = console.input("> ").strip()
        if not name:
            name = "Player"
        else:
            name = name[:10]

        submit_score(name, score)

        # Now clear everything and show the nice Game Over panel
        console.clear()
        console.print(Panel(
            f"\n\n[bold]Score:[/bold] {score}\n\n"
            f"Press [green]R[/green] to restart or [cyan]Q[/cyan] to quit.",
            title="GAME OVER",
            border_style="red",
            width=40,
            expand=False
        ), justify="center")

        with term.cbreak():
            while True:
                key = term.inkey(timeout=0.5)
                if key:
                    pressed = str(key).lower()
                    if pressed == "q":
                        console.clear()
                        console.print("👋  Thanks for playing!\n")
                        sys.exit()
                    elif pressed == "r":
                        restart_requested = True
                        break

        if restart_requested:
            console.clear()
            high_scores_text = get_high_scores()
            continue  # Restart outer loop
        else:
            break


def main():
    show_welcome_screen()
    game_logic()


if __name__ == "__main__":
    main()
