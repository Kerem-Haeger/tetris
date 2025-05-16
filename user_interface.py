import sys
from rich.console import Console
from rich.panel import Panel
from blessed import Terminal
from constants import EMPTY


console = Console()
term = Terminal()


def show_welcome_screen():
    """ Display the welcome screen with game instructions and controls. """
    console.clear()
    welcome_text = """[bold magenta]
Welcome to Tetris!
[/bold magenta]

[bold white]Controls:[/bold white]
[cyan]←[/cyan] Move Left
[cyan]→[/cyan] Move Right
[cyan]↓[/cyan] Soft Drop
[cyan]↑[/cyan] Rotate
[magenta]Q[/magenta] Quit

Press [green]Enter[/green] to begin...
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
            elif str(key).lower() == "q":
                console.clear()
                console.print("👋  Thanks for playing!\n")
                sys.exit()


def render_board(board):
    """
    Convert the board's 2D array into a string representation for display.
    """
    return "\n".join("".join(str(cell) for cell in row) for row in board)


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
