# MasterMind-Solver

## Overview

The MasterMind-Solver is a Python-based solution that automatically solves the board game Mastermind. The program implements an efficient algorithm to guess the correct sequence of colors within a specified number of turns, using feedback from previous guesses to refine its next moves. This solver is designed for a customizable `N x N` board and supports different code lengths and color options.

## Features

- Solves the Mastermind game in under 5 seconds.
- Supports multiple board sizes (`N x N`), where `N` is the length of the code and the number of colors.
- Offers a general-purpose solution that can be easily adapted for different Mastermind variations.
- Feedback processing to refine guesses based on previous attempts.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Riyuanliu/MasterMind-Solver.git
   cd mastermind-solver
   ```
2. Install dependencies (if any):

   ```bash
   pip install -r requirements.txt
   ```

## How to Configure

To customize the game settings, such as the player choices, SCSA methods, number of colors, and board length, you can modify the global variables in the script.

### Global Variables

You can change the following global variables to modify the game's configuration:

- **`players_choice`**: List of player names to participate in the tournament. You can include or exclude different players by modifying this list.
  Example:

  ```python
  players_choice = ["RubberCorn", "Smart_Player"]
  ```
- **`scsa_choices`**: List of SCSA (Search for Code Sequence Analysis) methods to use in the tournament. Modify this list to use different SCSA strategies.
  Example:

  ```python
  scsa_choices = ["ABColor", "TwoColor", "OnlyOnce"]
  ```
- **`num_colors`**: The number of available colors for the game. This value determines the size of the color pool.
  Example:

  ```python
  num_colors = 5  # Set to 5 colors for the game
  ```
- **`board_length`**: The number of pegs in the code. Adjust this value to change the length of the code.
  Example:

  ```python
  board_length = 4  # Set to a board with 4 pegs
  ```
- **`num_rounds`**: The number of rounds to run in the tournament. This is the number of times each player will play against each SCSA.
  Example:

  ```python
  num_rounds = 1  # Run 1 round for each player
  ```

### Example Configuration

Modify the variables in the script to your desired configuration:

```python
players_choice = ["RubberCorn", "Smart_Player"]
scsa_choices = ["ABColor", "InsertColors"]
num_colors = 6
board_length = 5
num_rounds = 3
```

### Running the Game

After modifying the global variables, you can run the game by calling the `auto_run_all()` function, which will automatically use the values set in these global variables for the tournament.

```bash
python3 main.py
```

```
