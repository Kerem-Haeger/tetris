import copy
import time
from rich.panel import Panel
from rich.layout import Layout
from user_interface import (
    render_board,
    render_next_panel,
    render_score_panel,
    render_controls_panel
)
from constants import BOARD_WIDTH, BOARD_HEIGHT, EMPTY


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
