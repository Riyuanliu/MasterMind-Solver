import random
from abc import ABC, abstractmethod
from scsa import list_to_str, InsertColors


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


class Baseline1(Player):
    """Mastermind Player that exhaustively guesses in lexicographic order"""

    def __init__(self):
        """Constructor for Baseline1"""

        self.player_name = "Baseline1"
        
        # List of possible guesses used by Baseline Player 1
        self.guesses = []
        self.cur_guess = 0

    def generate_guesses(self, board_length: int, colors: list[str]):
        """Generate the first 100 possible guesses in lexicographic order"""
        guesses = []
        num_colors = len(colors)

        for i in range(100):
            guess = ""
            temp = i
            for _ in range(board_length):
                guess = colors[temp % num_colors] + guess
                temp //= num_colors
            guesses.append(guess)

        return guesses

    def make_guess(
        self,
        board_length: int,
        colors: list[str],
        scsa_name: str,
        last_response: tuple[int, int, int],
    ) -> str:
        """Makes the next lexicographic guess without considering feedback

        Args:
            board_length (int): Number of pegs of secret code.
            colors (list[str]]): All possible colors that can be used to generate a code.
            scsa_name (str): Name of SCSA used to generate secret code.
            last_response (tuple[int, int, int]): (First element in tuple is the number of pegs that match exactly with the secret
                                           code for the previous guess, the second element is the number of pegs that are
                                           the right color, but in the wrong location for the previous guess, and the third
                                           element is the number of guesses so far.)

        Returns:
            str: Returns guess
        """

        # Check if guesses are instantiated
        if not self.guesses:
            self.guesses = self.generate_guesses(board_length=board_length, colors=colors)

        # Get the current guess from the list of guesses
        guess = self.guesses[self.cur_guess % 100]
        self.cur_guess += 1
        
        return guess