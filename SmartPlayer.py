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

class SmartPlayer(Player):
    def __init__(self):
        """Constructor for SmartPlayer"""
        super().__init__()
        self.player_name = "RubberCorn"
        self.color_count = {}  # Store color counts from guesses
        self.possible_codes = []  # List of valid codes based on feedback
        self.current_guess = ""
        self.know_colors = {}
    
    def make_guess(self, board_length: int, colors: list[str], scsa_name: str, last_response: tuple[int, int, int]) -> str:
        """
        Makes guesses based on feedback, generating valid guesses based on known color distribution.
        """
        if(last_response[2]==0):
            super().__init__()
            self.player_name = "RubberCorn"
            self.color_count = {}  # Store color counts from guesses
            self.possible_codes = []  # List of valid codes based on feedback
            self.current_guess = ""
            self.know_colors = {}
        
        bulls, cows, num_guesses = last_response
        current_guess = num_guesses + 1

        know = 0
        for color, count in self.know_colors.items():
            know += count

        # Handle first len(colors)-1 guesses with monochromatic colors
        if current_guess < len(colors):
            if know != board_length:
                if bulls > 0:
                    self.know_colors[colors[num_guesses-1]] = bulls

                self.current_guess = colors[num_guesses] * board_length  # All A's, all B's, etc.
                return self.current_guess
            else:
                guess_colors = []

                guess_colors = [color * count for color, count in self.know_colors.items()]

                self.possible_codes = list(set(permutations(''.join(guess_colors), board_length)))
                
                self.current_guess = ''.join(self.possible_codes.pop(0))
          
                return self.current_guess   
            
        
        if current_guess == len(colors):

            if bulls > 0:
                self.know_colors[colors[num_guesses-1]] = bulls
                    
            current_sum = 0

            for color, count in self.know_colors.items():
                current_sum += count

            if board_length - current_sum != 0:

                self.know_colors[colors[-1]] = board_length - current_sum
             
            guess_colors = []
            guess_colors = [color * count for color, count in self.know_colors.items()]

            self.possible_codes = list(set(permutations(''.join(guess_colors), board_length)))
            
            self.current_guess = ''.join(self.possible_codes.pop(0))
      
            return self.current_guess   

        self.possible_codes = self.filter_possible_codes(self.current_guess, bulls, cows,scsa_name)
        self.current_guess = ''.join(self.possible_codes.pop(0))
        return self.current_guess

    def filter_possible_codes(self, guess: str, bulls: int, cows: int, scsa_name: str) -> list[str]:
        """
        Filters the possible codes based on the bulls and cows feedback from the current guess.
        """
        # Filter the possible codes based on the feedback (bulls, cows)
        filtered_codes = [
            code for code in self.possible_codes if self.get_feedback(guess, code) == (bulls, cows)
        ]
    
        return filtered_codes
    
    def get_feedback(self, guess, secret):
        bulls = sum([1 for i in range(len(guess)) if guess[i] == secret[i]])
        cows = sum([1 for i in range(len(guess)) if guess[i] in secret and guess[i] != secret[i]])
        return bulls, cows