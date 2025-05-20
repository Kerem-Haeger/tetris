import time
import sys
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.document import Document
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from board import (
    create_board,
    can_move,
    lock_piece,
    add_piece_to_board,
    clear_lines
)
from piece import new_random_piece
from user_interface import (
    render_board, render_next_panel, render_score_panel,
    render_controls_panel, console, term
)
from highscores import get_high_scores, submit_score
from constants import VALID_KEYS


class MaxLengthValidator(Validator):
    """
    Validator to ensure the input length does
    not exceed 10 characters.
    """
    def validate(self, document: Document):
        if len(document.text) > 10:
            raise ValidationError(
                message="Maximum 10 characters allowed.",
                cursor_position=10
            )


def handle_post_game_input():
    """
    Waits for user input after the game ends and handles restart or quit
    commands.
    """
    with term.cbreak():
        while True:
            key = term.inkey(timeout=0.5)
            if key:
                key_str = str(key).lower()
                if key_str == "q":
                    console.clear()
                    console.print("👋  Thanks for playing!\n")
                    sys.exit()
                elif key_str == "r":
                    return True
    return False


def run_game_loop():
    """
    Main game loop that handles Tetris gameplay, user input, rendering,
    score tracking, level progression, and game over behavior.
    Returns the final score and whether the user requested to quit.
    """
    console.clear()  # Safeguard to clear screen before starting
    board = create_board()
    score = 0
    level = 1
    lines_total = 0
    tick_rate = 0.5
    current_piece = new_random_piece()
    next_piece = new_random_piece()
    quit_requested = False
    high_scores_text = get_high_scores()

    with term.cbreak(), Live(
                            console=console,
                            refresh_per_second=10,
                            transient=True
                            ) as live:
        while True:
            start_time = time.time()
            key = None

            while time.time() - start_time < tick_rate:
                k = term.inkey(timeout=0.01)
                if not k:
                    continue
                key_name = k.name if hasattr(k, "name") else None
                key_str = str(k).lower()
                if key_name in VALID_KEYS or key_str == "q":
                    key = k
                    break

            if key:
                key_name = key.name if hasattr(key, "name") else None
                key_str = str(key).lower()

                if key_name == "KEY_LEFT" and can_move(
                                                        current_piece,
                                                        board,
                                                        dr=0,
                                                        dc=-1
                                                    ):
                    current_piece.col -= 1
                elif key_name == "KEY_RIGHT" and can_move(
                                                        current_piece,
                                                        board,
                                                        dr=0,
                                                        dc=1
                                                        ):
                    current_piece.col += 1
                elif key_name == "KEY_DOWN" and can_move(
                                                        current_piece,
                                                        board,
                                                        dr=1
                                                        ):
                    current_piece.row += 1
                elif key_name == "KEY_UP":
                    current_piece.rotate(board)
                elif key_str == "q":
                    quit_requested = True
                    break

            if can_move(current_piece, board, dr=1):
                current_piece.row += 1
            else:
                lock_piece(current_piece, board)
                score += 10
                board, lines = clear_lines(
                    board, live, score, next_piece, high_scores_text
                )
                score += lines * 100
                lines_total += lines

                if lines_total >= level * 5:
                    level += 1
                tick_rate = max(0.1, 0.5 - (level - 1) * 0.05)

                current_piece = next_piece
                next_piece = new_random_piece()

                if not can_move(current_piece, board, dr=0):
                    break

            temp_board = add_piece_to_board(current_piece, board)
            layout = Layout()
            layout.split_row(
                Layout(
                    Panel(
                        render_board(temp_board),
                        title="TETRIS",
                        border_style="bold red",
                        width=24
                        ),
                    name="game",
                    size=24
                ),
                Layout(name="sidebar", size=28),
                Layout(
                    Panel(high_scores_text, title="LEADERBOARD", width=24),
                    name="leaderboard"
                )
            )
            layout["sidebar"].split_column(
                Layout(render_next_panel(next_piece)),
                Layout(render_score_panel(score)),
                Layout(render_controls_panel())
            )
            live.update(Panel(layout, height=24, width=80, border_style="dim"))

    return score, quit_requested


def post_game_prompt(score):
    """
    Handles the game over screen and input for
    score saving or restarting.
    """
    leaderboard_visible = False

    previous_state = None

    while True:
        if leaderboard_visible != previous_state:
            console.clear()
            if leaderboard_visible:
                high_scores_text = get_high_scores(limit=20, two_columns=True)
                console.print(Panel(
                    high_scores_text,
                    title="LEADERBOARD",
                    border_style="blue",
                    width=50,
                    expand=False
                ), justify="center")
                console.print(
                    "\nPress [bold cyan]L[/bold cyan] to return.",
                    justify="center"
                    )
            else:
                console.print(Panel(
                    f"""
[bold]Score:[/bold] {score}

Would you like to record your score?

Press [bold cyan]Enter[/bold cyan] to save your score to the leaderboard,
[green]R[/green] to restart, [magenta]Q[/magenta] to quit,
or [blue]L[/blue] to view leaderboard.
                    """,
                    title="GAME OVER",
                    border_style="red",
                    width=50,
                    expand=False
                ), justify="center")
            previous_state = leaderboard_visible

        with term.cbreak():
            key = term.inkey(timeout=0.5)
            if not key:
                continue
            key_str = str(key).lower()
            key_name = key.name if hasattr(key, "name") else None

            if key_str == "q":
                console.clear()
                console.print("\n\n👋  Thanks for playing!\n")
                sys.exit()
            elif key_str == "r":
                return False, True  # no score save, restart
            elif key_name == "KEY_ENTER":
                return True, False  # save score, do not restart
            elif key_str == "l":
                leaderboard_visible = not leaderboard_visible


def handle_score_submission(score):
    """Prompts for name, submits score, and handles post-save actions."""
    console.clear()
    console.print("""
[bold cyan]Enter a username for the leaderboard:[/bold cyan]
(max 10 characters, or press [cyan]Enter[/cyan] to skip)
    """, justify="center")

    name = prompt(
                "> ",
                validator=MaxLengthValidator(),
                validate_while_typing=True
                ).strip()

    if not name:
        name = "Player"

    submit_score(name, score)

    leaderboard_visible = False
    previous_state = None

    while True:
        if leaderboard_visible != previous_state:
            console.clear()
            if leaderboard_visible:
                high_scores_text = get_high_scores(limit=20, two_columns=True)
                console.print(Panel(
                    high_scores_text,
                    title="LEADERBOARD",
                    border_style="blue",
                    width=50,
                    expand=False
                ), justify="center")
                console.print(
                    "\nPress [bold cyan]L[/bold cyan] to return.",
                    justify="center"
                    )
            else:
                console.print(
                    Panel(
                        f"""
[bold]Your score has been recorded![/bold]

[bold]Score:[/bold] {score}

Press [green]R[/green] to restart, [magenta]Q[/magenta] to quit,
or [blue]L[/blue] to view the leaderboard.
                        """,
                        title="GAME OVER",
                        border_style="red",
                        width=50,
                        expand=False
                    ),
                    justify="center"
                )
            previous_state = leaderboard_visible

        with term.cbreak():
            key = term.inkey(timeout=0.5)
            if key:
                key_str = str(key).lower()
                if key_str == "r":
                    return True
                elif key_str == "q":
                    console.clear()
                    console.print("👋  Thanks for playing!\n")
                    sys.exit()
                elif key_str == "l":
                    leaderboard_visible = not leaderboard_visible


def game_logic():
    """
    Main game loop that handles Tetris gameplay, user input, rendering,
    score tracking, level progression, and game over behavior.
    """
    while True:
        score, quit_requested = run_game_loop()

        if quit_requested:
            console.clear()
            console.print("👋  Thanks for playing!\n")
            sys.exit()

        record_score, restart_requested = post_game_prompt(score)

        if record_score:
            restart_requested = handle_score_submission(score)

        if not restart_requested:
            break

        console.clear()
