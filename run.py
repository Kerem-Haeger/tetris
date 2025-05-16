from user_interface import show_welcome_screen
from game_logic import game_logic


def main():
    """
    Entry point for the Tetris game: shows welcome screen and
    starts the game loop.
    """
    show_welcome_screen()
    game_logic()


if __name__ == "__main__":
    main()
