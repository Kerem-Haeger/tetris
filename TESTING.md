# Testing

Return back to the [README.md](README.md) file.

## Testing Overview

The Terminal Tetris game was tested continuously throughout development, both manually and with help from external users. These tests focused on functionality, visual consistency in the terminal, game logic, and user experience. Special care was taken to ensure compatibility across platforms — especially between local terminals and Heroku’s hosted terminal emulator.

---

## Manual Testing

### Core Gameplay

- Game starts with welcome screen.
- All controls function as expected:
  - Arrow keys move and rotate tetrominoes.
  - Q quits the game gracefully.
  - Down arrow soft-drops a piece.
- Pieces lock when reaching the bottom or landing on another block.
- Lines clear correctly when a full row is filled.
- Game over screen triggers only once.
- Restart, submit score, and quit options work as expected.

### Visual & UX Testing

- Emoji blocks display correctly on local terminals.
- Fallback block characters render on Heroku (via `os.name` check).
- Score updates live and is always visible.
- Input for leaderboard is centered and accepts max 10 characters.
- Warning for character limit appears if exceeded.

---

## Peer/User Testing

Several peers were asked to test the game on both Windows and macOS terminals as well as in Heroku. Key feedback included:

- Clear controls and intuitive UI.
- Enjoyable gameplay and responsive keys.
- No major bugs during testing.
- Emoji fallback worked as intended.

---

## Validators

The project’s Python code was checked using [PEP8 Online](http://pep8online.com/) to ensure full PEP 8 compliance. Each file was copy-pasted manually into the validator, and no critical issues were found.

### Validation Results

- **run.py**  
  ![Python Validator](documentation/pep8_validator/validator_run_file.png)

- **game_logic.py**  
  ![Python Validator](documentation/pep8_validator/validator_game_logic_file.png)

- **tetromino.py**  
  ![Python Validator](documentation/pep8_validator/validator_tetromino_file.png)

- **leaderboard.py**  
  ![Python Validator](documentation/pep8_validator/validator_leaderboard_file.png)

- **input_handler.py**  
  ![Python Validator](documentation/pep8_validator/validator_input_handler_file.png)

- **utils.py**  
  ![Python Validator](documentation/pep8_validator/validator_utils_file.png)

---

## End-of-File Line Warnings

PEP8 validator sometimes showed “missing newline at end of file” even when GitHub confirmed the file ended correctly. Screenshots below confirm those files are compliant:

- **run.py**  
  ![EOF Line](documentation/pep8_validator/run_line_at_the_end.png)

- **game_logic.py**  
  ![EOF Line](documentation/pep8_validator/game_logic_line_at_the_end.png)

- **tetromino.py**  
  ![EOF Line](documentation/pep8_validator/tetromino_line_at_the_end.png)

- **leaderboard.py**  
  ![EOF Line](documentation/pep8_validator/leaderboard_line_at_the_end.png)

- **input_handler.py**  
  ![EOF Line](documentation/pep8_validator/input_handler_line_at_the_end.png)

- **utils.py**  
  ![EOF Line](documentation/pep8_validator/utils_line_at_the_end.png)
