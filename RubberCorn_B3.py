import random
from abc import ABC, abstractmethod
from itertools import permutations

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


class Baseline3(Player):
    def __init__(self):
        """Constructor for Baseline3"""
        super().__init__()
        self.player_name = "Baseline3"
        self.color_count = {}  # Store color counts from guesses
        self.possible_codes = []  # List of valid codes based on feedback
        self.current_guess = ""

    def make_guess(self, board_length: int, colors: list[str], scsa_name: str, last_response: tuple[int, int, int]) -> str:
        """
        Makes guesses based on feedback, generating valid guesses based on known color distribution.
        """
        exact_matches, partial_matches, num_guesses = last_response
        current_guess = num_guesses + 1

        # Handle first len(colors)-1 guesses with monochromatic colors
        if current_guess < len(colors):
            
            if(num_guesses != 0):
                self.color_count[colors[num_guesses-1]] = exact_matches

            self.current_guess = colors[num_guesses] * board_length  # All A's, all B's, etc.
            return self.current_guess
        
        # After the first len(colors)-1 guesses, calculate color distribution and generate valid codes
        if current_guess == len(colors):

            self.color_count[colors[num_guesses-1]] = exact_matches
            
            # Generate valid codes based on the known color distribution
            valid_colors = []
            current_sum = 0

            for color, count in self.color_count.items():
                current_sum += count
                valid_colors.extend([color] * count)  # Add each color as many times as it matched

            valid_colors.extend(colors[-1] * (board_length - current_sum))

            # Generate all valid codes that match the color distribution
            self.possible_codes = list(set(permutations(valid_colors, board_length)))
        
        # Ensure possible_codes isn't empty before trying to pop
        if self.possible_codes:

            self.current_guess = ''.join(self.possible_codes.pop(0))  # Use the next valid permutation
        else:
            
            self.current_guess = colors[0] * board_length  # Fallback: Make a random guess
        
        return self.current_guess
