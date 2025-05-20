# Terminal Tetris

![Terminal Tetris Screenshot](documentation/terminal_tetris_screenshot.png)

*A link to [play Terminal Tetris on Heroku](https://tetris-kh-c29675af7f73.herokuapp.com/)*

Terminal Tetris is a Python-based reimagining of the classic arcade game, designed to run entirely within the terminal.

The game uses the [Rich](https://github.com/Textualize/rich) library to enhance the interface with colorful emoji blocks and live score tracking. It also utilizes [Blessed](https://pypi.org/project/blessed/) for handling keypresses and terminal behavior, and [Prompt Toolkit](https://python-prompt-toolkit.readthedocs.io/en/master/) to manage input for features like the leaderboard.

Despite the absence of a graphical window, the game remains engaging, responsive, and faithful to the spirit of the original.

## How to Play

1. Click this [link to Terminal Tetris](https://tetris-kh-c29675af7f73.herokuapp.com/) or paste it into your browser.
2. Click **“Run Program”** to start the game in the terminal.
3. Press **Enter** to begin.
4. Use the following controls to play:

   - **←** Move Left
   - **→** Move Right
   - **↓** Soft Drop
   - **↑** Rotate
   - **Q** Quit the Game
   - **R** Restart the Game
   - **Enter** Submit Score (after game over, as well as various other functionalities)

5. As blocks fall, try to fill horizontal lines to clear them and earn points.
6. The game ends when the board is full and new pieces can’t spawn.
7. After the game, you’ll be prompted to enter a name for the leaderboard (max 10 characters).
8. You can restart the game, quit, or save your score, as well as view the leaderboard!

## User Stories

### First-Time Visitor Goals

- As a First-Time Visitor, I want to understand the game's purpose quickly so that I know what I’m about to play.
- As a First-Time Visitor, I want to see clear instructions and controls so that I can learn how to play easily.
- As a First-Time Visitor, I want the terminal interface to be visually appealing so that the experience is fun and engaging.
- As a First-Time Visitor, I want to be able to submit my score so that I feel rewarded for my performance.

### Returning User Goals

- As a Returning User, I want the controls to feel intuitive and responsive so that I can improve my gameplay.
- As a Returning User, I want to be able to restart the game quickly so that I can try to beat my high score.
- As a Returning User, I want to view and submit my name to the leaderboard so that I can track my progress over time.


## Features

### Welcome Screen

- When the game launches, users are greeted with a colorful welcome screen rendered using the Rich library.
- Instructions and controls are displayed clearly with styled arrow keys and color-coded options.

![Welcome Screen](documentation/features/welcome_screen.png)

---

### Game Interface

- The game board is drawn entirely in the terminal using colored emoji blocks (e.g., 🟥, 🟦) for a vibrant and engaging experience.
- The layout is designed to render correctly on **Heroku’s terminal emulator**, even with its limited emoji/font support.
- The game detects the operating system and terminal type:
  - **If running locally** (on Windows or macOS with full emoji support), emoji blocks like 🟥 are used.
  - **If running on Heroku**, it falls back to alternative block characters (e.g., `▓`) to ensure full compatibility.
- Tetrominoes fall from the top of the board and can be moved or rotated using the arrow keys.
- Real-time rendering is handled with `blessed`, keeping the experience smooth and responsive.

![Game Interface](documentation/features/game_board.png)

---

### Score Tracking

- The current score is displayed on the side of the board.
- The game tracks cleared lines and increases the score accordingly.
- The score updates live as you play.

![Score Tracking](documentation/features/score_tracking.png)

---

### Tetromino Preview (Optional)

- The next tetromino is previewed next to the game board to help players plan ahead.
- Each shape has its own color, making them easier to distinguish.

![Next Piece Preview](documentation/features/next_piece.png)

---

### Leaderboard Input

- When the game ends, players are prompted to enter a name (max 10 characters).
- Input is handled using `prompt_toolkit` for clean, styled input.
- Players can skip this step or save their score to a leaderboard.

![Leaderboard Prompt](documentation/features/leaderboard_prompt.png)

---

### Game Over & Options

- After the game ends, users can:
  - Submit their score
  - Restart the game
  - Quit the application
- The game handles invalid input and gently guides the user to make a selection.

![Game Over Menu](documentation/features/game_over_menu.png)

## Flowchart

The following flowchart represents the core logic of the Terminal Tetris application, from initial launch to game over and score submission.

It illustrates how the game interacts with user input (movement, rotation, quit), score updates, row clearing, and end-game options like restarting or submitting to the leaderboard.

![Terminal Tetris Flowchart](documentation/flowchart.png)
