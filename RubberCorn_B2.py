import random
from abc import ABC, abstractmethod
from scsa import list_to_str, InsertColors
from itertools import product, permutations, combinations_with_replacement

class Player(ABC):
    """Player for Mastermind"""

    def __init__(self):
        """Constructor for Player"""

        self.player_name = ""

    @abstractmethod
    def make_guess(
        self,
        board_length: int,
        colors: list[str],
        scsa_name: str,
        last_response: tuple[int, int, int],
    ) -> str:
        """Makes a guess of the secret code for Mastermind

        Args:
            board_length (int): Number of pegs of secret code.
            colors (list[str]]): All possible colors that can be used to generate a code.
            scsa_name (str): Name of SCSA used to generate secret code.
            last_response (tuple[int, int, int]): (First element in tuple is the number of pegs that match exactly with the secret
                                           code for the previous guess, the second element is the number of pegs that are
                                           the right color, but in the wrong location for the previous guess, and the third
                                           element is the number of guesses so far.)

        Raises:
            NotImplementedError: Function must be implemented by subclasses.
        """

        raise NotImplementedError

class Baseline2(Player):
    """Mastermind Player that exhaustively guesses in lexicographic order, ruling out guesses based on responses."""

    def __init__(self):
        """Constructor for Baseline2"""
        super().__init__()
        self.player_name = "Baseline2"
        self.guesses = []  # List of all possible guesses in lexicographic order
        self.current_guess = ""
        self.invalid_positions = {}  # Dictionary to track invalid positions for each color

    def make_guess(
        self,
        board_length: int,
        colors: list[str],
        scsa_name: str,
        last_response: tuple[int, int, int],
    ) -> str:
        """Make the next guess, removing guesses based on responses with 0 bulls."""
        bulls, cows, last_guess_count = last_response

        # If it's the first guess or game just started
        if last_guess_count == 0:
            self.guesses=list(product(colors, repeat=board_length))
            self.current_guess = ''.join(self.guesses.pop(0))
  
            return self.current_guess

        # Apply constraints if last response had 0 bulls
        if bulls == 0:
            # Update invalid positions based on the previous guess
            for idx, char in enumerate(self.current_guess):
                self.guesses = [guess for guess in self.guesses if guess[idx] != char]

        # Filter guesses based on invalid positions
    

        # Pick the next guess in lexicographic order
        self.current_guess = ''.join(self.guesses.pop(0))  # Choose the first guess in lexicographic order

        return self.current_guess
