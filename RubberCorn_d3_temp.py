# File contains implementations for the players for Mastermind.
# See main.py or examples.ipynb for example usages.
from itertools import product, permutations, combinations_with_replacement
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

class RubberCorn(Player):
    def __init__(self):
        """Constructor for Baseline4"""
        super().__init__()
        self.player_name = "Baseline4"
        self.color_count = {}  # Store color counts from guesses
        self.current_guess = ""
        self.inferences = []  # List of (color, possible positions)
        self.tied_colors = []  # List of (color, tied positions)
        self.being_fixed = None
        self.being_considered = None

        self.current_guess = ""

    def make_guess(self, board_length: int, colors: list[str], scsa_name: str, last_response: tuple[int, int, int]) -> str:
        if(last_response[2]==0):
            self.inferences = []  # List of (color, possible positions)
            self.tied_colors = []  # List of (color, tied positions)
            self.being_fixed = None
            self.being_considered = None
        """
        Makes guesses based on feedback, generating valid guesses based on known color distribution and inferences.
        """

        exact_matches, partial_matches, num_guesses = last_response
            
        self.update(colors, board_length, exact_matches, partial_matches)
            
        
        self.current_guess = self.Getnext(board_length)


        return self.current_guess

    def Getnext(self, N):
        
        """Constructs the next trial arrangement based on the given logic."""
        valid_colors = []

        # Iterate through all positions to build the guess
        for i in range(N):
            # Case 1: If the position is tied to a color
            if self.Tied(i):
                gi = self.Itscolor(i)  # Assign the tied color to the current position
                if(self.Itscolor(i)==None):
                    print("case1")
            # Case 2: If the position is the next possible position for a color that is being fixed
            elif i == self.Nextpos(self.being_fixed):
                gi = self.being_fixed  # Use the second unfixed color
                if(self.being_fixed==None):
                    print("case2")
            # Case 3: If the length of inferences equals N, use the second unfixed color
            elif len(self.inferences)+len(self.tied_colors) == N:
                gi = self.Secondunfixed()
                if(self.Secondunfixed()==None):
                    print("case3")
            else:
                # Case 4: Otherwise, use a color being considered
                gi = self.being_considered
                if(self.being_considered==None):
                    gi = self.being_fixed
    
            valid_colors.append(gi)  # Add the determined color for position i to the guess list
    
        self.current_guess = ''.join(valid_colors)  # Combine the list of colors into a string
        return self.current_guess

    def Tied(self, i):
        """Returns True if position i is tied to a specific color."""
        for color, positions in self.tied_colors:  # Iterate over each color and its tied positions
            if i == positions:  # If the position is tied to a color
                return True
        return False

    def Itscolor(self, i):
        """Returns the color tied to position i."""
        for color, positions in self.tied_colors:
            if i == positions:  # If the position is tied to this color
                return color  # Return the color tied to position i
        return None  # Return None if no color is tied to position i

    def Nextpos(self, color):
        """Returns the next available position for color i."""
        for c, position in self.inferences:
            if c == color:
                return position[0]
        return None

    def Secondunfixed(self):
        # Iterate through the inferences list
        for color, _ in self.inferences:
            # Return the first color that doesn't match self.being_fixed
            if color != self.being_fixed:
                return color
        # If no different color is found, return None (or some default if needed)
        if(len(self.inferences) > 1):
            return self.inferences[1][0]
        return self.being_fixed

    def update(self, colors, board_length, bulls, cows):
        """Updates inferences based on the latest guess results."""
        
        # Calculate gain
        num_fixed = len(self.tied_colors)

        gain = (bulls + cows) - num_fixed  - (self.being_fixed != None)
        

        
        self.add_lists(gain, board_length)

        # Handle cases based on the number of cows
        if cows == 0:
            # being_fixed is correct in current position
            self.fix(self.being_fixed)
            self.bump()

        elif cows == 1:
            # being_fixed and being_considered are incorrect in current position
            if self.being_fixed != None:
                self.del_position(self.being_fixed, self.being_considered)
            self.del_position(self.being_fixed, self.being_fixed)
        elif cows == 2:
            # Fix being_considered in the position of being_fixed
            if(self.being_considered == None):
                self.fix1(self.Secondunfixed(), self.being_fixed)
            else:
                self.fix1(self.being_considered, self.being_fixed)

        # Final cleanup and preparation for the next round
        self.cleanup()
        self.nextcolor(board_length, colors)
        
    def add_lists(self, gain, board_length):
        """
        Adds sublists to inferences, equal to the number of gain.
        Each sublist starts with the header being_considered and has an empty list of positions.
        """
        known = len(self.inferences) + len(self.tied_colors)
        if( known < board_length):
            all_positions = list(range(0, board_length))  # Create a list of all positions (1 to N)

            for _ in range(gain):
                # Append a new sublist to inferences with being_considered as the color and all positions as potential choices
                self.inferences.append((self.being_considered, all_positions.copy()))  

    def fix(self, color):
        """Fixes the given color in its next available position, removes it from inferences,
        and adds it to tied_colors with the first position."""
        for i, (col, positions) in enumerate(self.inferences):
            if col == color and positions:
                first_position = positions[0]  # Get the first available position
                # Add the color and its fixed position to tied_colors
                self.tied_colors.append((color, first_position))
                # Remove the color from inferences
                self.inferences.pop(i)
                # Perform cleanup to remove this position from other colors' lists
                break
        self.cleanup()

    def bump(self):
        if(self.inferences):
            self.being_fixed = self.inferences[0][0]
        else:
            self.being_fixed = None

    def del_position(self, color_i, color_j):
        """
        Deletes the current position of color_i from color_j's list of positions in inferences.

        Parameters:
        - color_i: The color whose position will be removed from color_j's position list.
        - color_j: The color from whose position list color_i's position will be removed.
        """
        # Find the position list of color_i in inferences
        pos_i = None
        for color, positions in self.inferences:
            if color == color_i and positions:
                pos_i = positions[0]  # Get the first (current) position of color_i
                break

        # If we found the current position of color_i, remove it from color_j's list
        if pos_i is not None:
            for idx, (color, positions) in enumerate(self.inferences):
                if color == color_j and pos_i in positions:
                    positions.remove(pos_i)
   
    def fix1(self, color_i, color_j):
        """
        Fixes color_i in the current position of color_j and removes this position from other lists in inferences.
        
        Parameters:
        - color_i: The color to be fixed.
        - color_j: The color whose current position will be used to fix color_i.
        """
        
        # Find the current position of color_j
        pos_j = None
        for color, positions in self.inferences:
            if color == color_j and positions:
                pos_j = positions[0]  # Get the first (current) position of color_j
                break

        # If we found the position for color_j, proceed to fix color_i
        if pos_j is not None:
            # Remove color_i from inferences and add it to tied_colors with its fixed position
            for i, (color, positions) in enumerate(self.inferences):
                if color == color_i:
                    # Remove color_i from inferences by deleting this entry
                    self.tied_colors.append((color_i, pos_j))
                    self.inferences.pop(i)
                    self.cleanup()
                    break  # Exit after removing the first occurrence

    def cleanup(self):
        """Cleans up the inferences by removing redundant positions based on tied colors."""
        
        # Set of all positions that are already tied to a specific color
        positions_to_remove = {pos for _, pos in self.tied_colors}

        while True:
            # Track if any changes were made during this pass
            changes_made = False

            # Go through each entry in inferences and remove tied positions
            for i in range(len(self.inferences)):
                color, positions = self.inferences[i]
                
                # Remove positions that are already tied
                updated_positions = [pos for pos in positions if pos not in positions_to_remove]
                
                # If there are fewer positions after cleanup, update inferences
                if len(updated_positions) != len(positions):
                    self.inferences[i] = (color, updated_positions)
                    changes_made = True

                if(len(updated_positions) == 0):
                    self.inferences.pop(i)
                    changes_made = True

                # If only one position is left, move this color to tied_colors
                if len(updated_positions) == 1:
                    tied_position = updated_positions[0]
                    # Add the color and its fixed position to tied_colors
                    self.tied_colors.append((color, tied_position))
                    # Add this position to positions_to_remove for future cleanup
                    positions_to_remove.add(tied_position)
                    # Remove the color from inferences
                    
                    self.inferences.pop(i)
                    changes_made = True
                    break  # Restart cleanup loop due to change

            # Exit loop if no changes were made in this pass
            if not changes_made:
                break
        if(self.inferences):
            self.being_fixed = self.inferences[0][0]
        
    def nextcolor(self, board_length, colors):
        """Gets the next color to be considered."""
        # Check if the total of tied colors and inferences matches the board length
        total_used_positions = len(self.tied_colors) + len(self.inferences)
        
        # If total used positions are less than the board length, proceed in order
        if total_used_positions < board_length:
            if self.being_considered is None:
                self.being_considered = colors[0]
            elif self.being_considered in colors:
                index = colors.index(self.being_considered)
                if index < len(colors) - 1:
                    self.being_considered = colors[index + 1]
                else:
                    self.being_considered = None
        else:
            
            self.being_considered = None
  