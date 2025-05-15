from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from blessed import Terminal
from constants import EMPTY


console = Console()
term = Terminal()


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
