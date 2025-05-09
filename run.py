from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from blessed import Terminal
import gspread
from google.oauth2.service_account import Credentials
import time
import random
import copy

# Constants
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]
CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("leaderboard")
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

TETROMINO_EMOJIS = ["🟥", "🟦", "🟨", "🟩", "🟪", "🟧"]

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


def new_random_piece():
    name = random.choice(list(TETROMINOES.keys()))
    shape = TETROMINOES[name]
    emoji = random.choice(TETROMINO_EMOJIS)
    return Piece(name, shape, emoji)


def create_board():
    return [[EMPTY for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]


def can_move(piece, board, dr=1, dc=0):
    for r, c in piece.get_coords():
        nr, nc = r + dr, c + dc
        if nr >= BOARD_HEIGHT or nc < 0 or nc >= BOARD_WIDTH:
            return False
        if board[nr][nc] != EMPTY:
            return False
    return True


def lock_piece(piece, board):
    for r, c in piece.get_coords():
        if 0 <= r < BOARD_HEIGHT and 0 <= c < BOARD_WIDTH:
            board[r][c] = piece.emoji


def add_piece_to_board(piece, board):
    temp_board = copy.deepcopy(board)
    for r, c in piece.get_coords():
        if 0 <= r < BOARD_HEIGHT and 0 <= c < BOARD_WIDTH:
            temp_board[r][c] = piece.emoji
    return temp_board


def render_board(board):
    return "\n".join("".join(row) for row in board)


def render_next_piece(piece):
    lines = []
    for row in piece.shape:
        line = ""
        for val in row:
            line += piece.emoji if val else EMPTY
        lines.append(line)
    return "\n".join(lines)


def render_score_panel(score):
    return Panel(f"[bold green]{score}[/bold green]", title="SCORE", width=20)


def render_next_panel(next_piece):
    return Panel(render_next_piece(next_piece), title="NEXT", width=20)


def render_controls_panel():
    controls_text = (
        "[bold]←[/bold] Move Left\n"
        "[bold]→[/bold] Move Right\n"
        "[bold]↓[/bold] Soft Drop\n"
        "[bold]↑[/bold] Rotate\n"
        "[bold]Q[/bold] Quit"
    )
    return Panel(controls_text, title="CONTROLS", width=20)


def clear_lines(board, live, score, next_piece):
    """
    Animates and clears full lines with a wiping effect.
    Returns the updated board and number of lines cleared.
    """
    next_panel = render_next_panel(next_piece)
    score_panel = render_score_panel(score)
    controls_panel = render_controls_panel()

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
            temp_board[idx][col] = "⬜"

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
                Layout(controls_panel)
            )

            live.update(Panel(layout, height=24, width=80, border_style="dim"))
            time.sleep(0.02)

    # Remove the full rows
    new_board = [row for i, row in enumerate(board) if i not in full_rows]
    while len(new_board) < BOARD_HEIGHT:
        new_board.insert(0, [EMPTY for _ in range(BOARD_WIDTH)])

    return new_board, lines_cleared


def main():
    while True:  # Outer loop to support restarting the game
        board = create_board()
        score = 0
        level = 1
        lines_total = 0
        tick_rate = 0.5
        current_piece = new_random_piece()
        next_piece = new_random_piece()
        restart_requested = False

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

                    board, lines = clear_lines(board, live, score, next_piece)
                    score += lines * 100
                    lines_total += lines

                    if lines_total >= level * 5:
                        level += 1

                    tick_rate = max(0.1, 0.5 - (level - 1) * 0.05)

                    current_piece = next_piece
                    next_piece = new_random_piece()

                    if not can_move(current_piece, board, dr=0):
                        game_over_panel = Panel(
                            f"[bold red]Game Over![/bold red]\n"
                            f"[bold]Score:[/bold] {score}\n\n"
                            f"""
Press [green]R[/green] to restart or [cyan]Q[/cyan] to quit.
                            """,
                            title="GAME OVER",
                            border_style="red",
                            width=40
                        )
                        live.update(game_over_panel)

                        # Wait for R or Q
                        while True:
                            key = term.inkey()
                            if key.lower() == "q":
                                return
                            elif key.lower() == "r":
                                restart_requested = True
                                break  # Exit inner loop

                        break

                # Render the updated board each frame
                temp_board = add_piece_to_board(current_piece, board)
                next_panel = render_next_panel(next_piece)
                score_panel = render_score_panel(score)
                controls_panel = render_controls_panel()
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
                    Layout(controls_panel)
                )

                live.update(Panel(
                    layout,
                    height=24,
                    width=80,
                    border_style="dim")
                )

        if restart_requested:
            console.clear()
            continue  # Restart outer loop
        else:
            break  # Quit the game


main()
