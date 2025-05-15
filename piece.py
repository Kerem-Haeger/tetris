import random
from constants import (
    TETROMINOES,
    TETROMINO_EMOJIS,
    BOARD_WIDTH,
    BOARD_HEIGHT,
    EMPTY
)


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


def new_random_piece():
    """
    Generate a new random Tetromino piece with a random shape and color.
    """
    name = random.choice(list(TETROMINOES.keys()))
    shape = TETROMINOES[name]
    block = random.choice(TETROMINO_EMOJIS)
    return Piece(name, shape, block)
