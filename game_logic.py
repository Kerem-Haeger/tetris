import time
import sys
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
        quit_requested = False  # NEW FLAG

        high_scores_text = get_high_scores()

        with term.cbreak(), Live(
            console=console,
            refresh_per_second=10
        ) as live:
            while True:  # Inner game loop
                # Custom key poll loop
                valid_keys = (
                    "KEY_LEFT",
                    "KEY_RIGHT",
                    "KEY_DOWN",
                    "KEY_UP",
                    "q"
                )
                start_time = time.time()
                key = None

                while time.time() - start_time < tick_rate:
                    k = term.inkey(timeout=0.01)
                    if not k:
                        continue
                    if k.name in valid_keys or str(k).lower() == "q":
                        key = k
                        break

                # Safely handle input
                if key:
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

                    elif str(key).lower() == "q":
                        quit_requested = True
                        break  # Exit gameplay loop

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

        # Handle early quit (skip score input and game over panel)
        if quit_requested:
            console.clear()
            console.print("👋  Thanks for playing!\n")
            sys.exit()

        # Prompt for name after game ends
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

        # Show clean game over screen with restart/quit
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
            continue
        else:
            break
