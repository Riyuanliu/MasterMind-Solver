import itertools
import random
from abc import ABC, abstractmethod
from scsa import list_to_str, InsertColors
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

class SuperSmartPlayer(Player):
    def __init__(self):
        """Constructor for SuperSmartPlayer"""
        super().__init__()
        self.player_name = "SuperSmartPlayer"
        self.possible_guesses = []

    def make_guess(self, board_length: int, colors: list[str], scsa_name: str, last_response: tuple[int, int, int]) -> str:
        """Makes a strategic guess based on feedback."""
        if last_response[2] == 0:  # First guess
            self.possible_guesses = [''.join(p) for p in itertools.product(colors, repeat=board_length)]
            guess = colors[:2] * (board_length // 2) + colors[:board_length % 2]
        else:
            # Filter remaining possibilities based on last response
            self.possible_guesses = [
                g for g in self.possible_guesses
                if self.simulate_feedback(g, self.current_guess) == (last_response[0], last_response[1])
            ]
            guess = self.possible_guesses[0]  # Pick the first remaining guess

        self.current_guess = guess
        return guess

    def simulate_feedback(self, secret: str, guess: str) -> tuple[int, int]:
        """Simulates feedback for a given guess against a hypothetical secret."""
        black_pegs = sum(a == b for a, b in zip(secret, guess))
        white_pegs = sum(min(secret.count(c), guess.count(c)) for c in set(secret)) - black_pegs
        return black_pegs, white_pegs
