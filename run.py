from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.columns import Columns
import time
from blessed import Terminal
import random
import copy

# Constants
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
EMPTY = "  "
TICK_RATE = 0.5

console = Console()
term = Terminal()

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


def render_side_panel(score, next_piece):
    score_panel = Panel(f"""
[bold green]{score}[/bold green]""",
                        title="SCORE",
                        width=20
                        )
    next_panel = Panel(render_next_piece(next_piece), title="NEXT", width=20)
    return [score_panel, next_panel]


def clear_lines(board, live):
    """
    Animates and clears full lines with a wiping effect.
    Returns the updated board and number of lines cleared.
    """
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
            temp_board[idx][col] = "⬜"  # Replace one cell at a time
            game_panel = Panel(
                            render_board(temp_board),
                            title="TETRIS",
                            border_style="bold red",
                            width=24
                            )
            live.update(Columns([game_panel]))
            time.sleep(0.02)  # adjust speed for faster/slower wipe

    # Remove the full rows
    new_board = [row for i, row in enumerate(board) if i not in full_rows]
    while len(new_board) < BOARD_HEIGHT:
        new_board.insert(0, [EMPTY for _ in range(BOARD_WIDTH)])

    return new_board, lines_cleared


def main():
    board = create_board()
    score = 0
    level = 1
    lines_total = 0
    tick_rate = 0.5
    current_piece = new_random_piece()
    next_piece = new_random_piece()

    with term.cbreak(), Live(
        console=console, refresh_per_second=10, screen=True
                            ) as live:
        while True:
            key = term.inkey(timeout=tick_rate)

            # handle key presses
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
                break

            # apply gravity
            if can_move(current_piece, board, dr=1):
                current_piece.row += 1
            else:
                lock_piece(current_piece, board)
                score += 10

                board, lines = clear_lines(board, live)
                score += lines * 100
                lines_total += lines

                # Every 10 lines, level up
                if lines_total >= level * 10:
                    level += 1

                tick_rate = max(0.1, 0.5 - (level - 1) * 0.05)

                current_piece = next_piece
                next_piece = new_random_piece()

                if not can_move(current_piece, board, dr=0):
                    live.update(Panel(f"""
[bold red]Game Over![/bold red]\n\nFinal Score: {score}
                                    """))
                    break

            temp_board = add_piece_to_board(current_piece, board)
            side_panels = render_side_panel(score, next_piece)
            game_panel = Panel(
                render_board(temp_board),
                title="TETRIS",
                border_style="bold red",
                width=24
                )
            live.update(Columns([game_panel] + side_panels))


main()
