from itertools import product, permutations
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
        open("guess_log.txt", "w").close()
        
        """Constructor for Near Final Player (Deadline 4)"""

        super().__init__()
        self.player_name = "RubberCorn"
        self.color_count = {}  # Store color counts from guesses
        self.current_guess = ""
        self.inferences = []  # List of (color, possible positions)
        self.max_correct = 0

        self.current_index = 0  # Index of peg to evaluate currently

        # self.tied_colors = []  # List of (color, tied positions)
        # self.being_fixed = None
        # self.being_considered = None
        # self.current_guess = ""
        # self.done = False

    def make_guess(
        self,
        board_length: int,
        colors: list[str],
        scsa_name: str,
        last_response: tuple[int, int, int],
    ) -> str:
        """
        SCSA Algorithms:
        
        InsertColor:            use default guesser Rao (purely random)

        TwoColor:               use custom algorithm implemented

        ABColor:                Work In Progress (almost complete)

        TwoColorAlternating:    use custom algorithm implemented

        OnlyOnce:               Work In Progress (almost complete)

        FirstLast:              Work In Progress

        UsuallyFewer:           Work In Progress

        PreferFewer:            Work In Progress

        Mystery1:               Pattern Identified - working on cracking the algorithm

        Mystery2:               Work In Progress (almost complete)

        Mystery3:               Pattern Identified - working on cracking the algorithm

        Mystery4:               Pattern Identified - working on cracking the algorithm

        Mystery5:               use custom algorithm implemented
        """
        match scsa_name:
            case "TwoColor":
                # TwoColor Algorithm
                return self.TwoColor(board_length, colors, last_response)

            # WORK IN PROGRESS - DO NOT UNCOMMENT
            # case "OnlyOnce":
            #     OnlyOnce Algorithm
            #     return self.OnlyOnce(board_length, colors, last_response)

            case "TwoColorAlternating":
                # TwoColorAlternating Algorithm
                return self.TwoColorAlternating(board_length, colors, last_response)

            case "Mystery5":
                # Mystery5 Algorithm
                return self.Mystery5(board_length, colors, last_response)

            case _:
                # Default to Rao Algorithm
                return self.Rao(board_length, colors, last_response)

    # Completed Algorithm    
    def TwoColor(self, board_length, colors, last_response):
        """
        Algorithm to handle TwoColor SCSA
        """
        # Initial Move - Reset all member variable containers (knowledge base)
        if last_response[2] == 0:
            # Stores the dichromatic guesses that contain the correct colors
            self.colors = []

            # Stores the monochromatic guesses, based on the dichromatic pairs, to test for individual colors
            self.inferences = []

            # The two colors that are used in the code
            self.two_colors = []

            # Flag for if the monochromatic guesses are made
            # After the guesses are made, if only one pair of colors is in the set, the monochromatic colors are those two individual colors
            # If two pairs are in the set, the monochromatic colors are the four individual colors
            self.mono_made = False

            # Flag for if the monochromatic guesses have all been checked
            self.mono_checked = False

            # First Guess
            self.current_guess = "".join(
                colors[0] for _ in range(board_length // 2)
            ) + "".join(colors[1] for _ in range(board_length - board_length // 2))

            self.current_index = 0

            self.max_correct = 0

            return self.current_guess

        if len(self.colors) != 2 and (
            last_response[0] or last_response[1] or last_response[2] > len(colors) // 2
        ):  # if a color is found
            # Would add a string like "AB" to the dict
            # bool represents if in correct position
            self.colors.append("".join(self.current_guess[0] + self.current_guess[-1]))

        # Figuring out which two doubles contains the correct colors
        if len(self.colors) != 2 and last_response[2] < len(colors) // 2:
            self.current_guess = "".join(
                colors[last_response[2] * 2] for _ in range(board_length // 2)
            ) + "".join(
                colors[last_response[2] * 2 + 1]
                for _ in range(board_length - board_length // 2)
            )
            return self.current_guess

        if (
            len(self.colors) != 2
            and last_response[2] >= len(colors) // 2
            and len(colors) % 2 == 1
        ):
            self.colors.append(colors[-1] + colors[-1])

        # By this stage, either all colors are found or the last colors have been checked
        # Time to submit the 4 monochromatic colors
        if not self.mono_made:
            self.mono_made = True
            if len(self.colors) == 2:
                first, second = list(self.colors)
                self.inferences.append(first[0] * board_length)
                self.inferences.append(first[1] * board_length)
                self.inferences.append(second[0] * board_length)
                self.inferences.append(second[1] * board_length)
            else:
                # Only two colors means they are guaranteed the answer and are ready to be tested
                self.two_colors.append(list(self.colors)[0][0])
                self.two_colors.append(list(self.colors)[0][1])
                self.mono_checked = 2
                self.current_guess = self.two_colors[1] * board_length
                return self.current_guess

        if len(self.two_colors) != 2 and self.mono_checked > 0:
            if last_response[0] > 0:
                self.two_colors.append(self.current_guess[0])

        if len(self.two_colors) != 2:
            self.mono_checked += 1
            self.current_guess = self.inferences.pop(0)
            # print("curr guess", self.current_guess)
            return self.current_guess

        if last_response[0] < self.max_correct:
            self.current_guess = (
                self.current_guess[: self.current_index - 1]
                + self.two_colors[1]
                + self.two_colors[0]
                + self.current_guess[self.current_index + 1 : board_length]
            )

        else:
            self.current_guess = (
                self.current_guess[: self.current_index]
                + self.two_colors[0]
                + self.current_guess[self.current_index + 1 : board_length]
            )
            self.max_correct = last_response[0]

        self.current_index += 1

        return self.current_guess[:board_length]

    # Work in Progress
    def ABColor(self, board_length, colors, last_response): # WIP
        # First guess: reset variables and submit all A's
        if last_response[2] == 0:
            self.A_count, self.B_count = 0,0 # counts the number of A's and B's in the code
            
            self.A_index, self.B_index = 0,0 # tracks the current index of the A's and B's to flip
            
            self.current_guess = 'A'*board_length # submit monochromatic A the total A count
            
            self.max_bulls = 0 # Tracks the highest amount of bulls reached
            
            return self.current_guess
        
        # Second guess: track A_count and submit all B's
        if last_response[2] == 1:
            self.A_count = last_response[0] # track the number of A's found in the last submission
            
            # Note, A_index remains at 0
            # Since the number of B's will be added to the guess after the number of A's, the first B will be at the index equal to the A_count
            self.B_index = self.A_count
            
            self.current_guess = 'B'*board_length # submit monochromatic B the total B count
            return self.current_guess
        
        # Submit the base guess which will have it's A's and B's gradually flipped 
        if last_response[2] == 2: 
            self.B_count = last_response[0] # track the number of A's found in the last submission
            
            self.current_guess = 'A'*self.A_count + 'B'*self.B_count # initial guess with the correct amount of A's and B's
            return self.current_guess
        
        # At this point, the color flipping begins
        
        # If the last guess had two less bulls than the max, that means both flipped bits were orignally correct.
        # So unflip them and flip the next indices and increment the indexers
        if last_response[0] < self.max_bulls:
            
            
            first_part = self.current_guess[: self.A_index-1] + 'A' + 'B' + self.current_guess[self.A_index+1 : self.A_count]
            second_part = self.current_guess[self.A_count : self.B_index-1] + 'B' + 'A' + self.current_guess[self.B_index+1 :]
            
            print("\nparts:", first_part,second_part, "\na index is", self.A_index)
            # Flip the last A_index back to an A and try flipping the current A_index to B.
            # Flip the last B_index back to a B and the try flipping the current B_index to an A.
            self.current_guess = (self.current_guess[: self.A_index-1] + 'A' + 'B' + self.current_guess[self.A_index+1 : self.A_count] + 
                                  self.current_guess[self.A_count : self.B_index-1] + 'B' + 'A' + self.current_guess[self.B_index+1 :])            
            
            self.A_index += 1
            self.B_index += 1
            return self.current_guess
        
        # If the last guess had two more bulls than the max, that means both flipped bits are now correct.
        # So update max_bulls, flip the next indices, and increment the indexers
        if last_response[0] > self.max_bulls:
            self.max_bulls = last_response[0] # Update max_bulls
            
            # Try flipping the current A_index to B.
            # Try flipping the current B_index to A.
            first_part = self.current_guess[: self.A_index] + 'B' + self.current_guess[self.A_index+1 : self.A_count]
            second_part = self.current_guess[self.A_count : self.B_index] + 'A' + self.current_guess[self.B_index+1 :]
            
            print("\nparts:", first_part,second_part)
            self.current_guess = (self.current_guess[: self.A_index] + 'B' + self.current_guess[self.A_index+1 : self.A_count] + 
                                  self.current_guess[self.A_count : self.B_index] + 'A' + self.current_guess[self.B_index+1 :])   
            
            # print("\ncurrents:", self.current_guess[: self.A_count], self.current_guess[self.A_count :])
            
            self.A_index += 1
            self.B_index += 1
            return self.current_guess
        
        return "A" # Failure for testing

    # Work in Progress
    def OnlyOnce(self, board_length, colors, last_response):  # WIP
        """
        Algorithm to handle OnlyOnce SCSA
        """
        # Initial Move - Reset all member variable containers (knowledge base)
        if last_response[2] == 0:
            self.color_count = {}
            self.groups_to_search = []
            self.groups_added = False
            self.current_subgroup = ""
            self.individual_colors = []
            self.individual_start = False
            self.current_guess = "".join(i for i in colors[:board_length])
            return self.current_guess

        print(self.color_count)

        if sum(self.color_count.values()) < board_length and (
            last_response[0] or last_response[1]
        ):
            self.color_count[self.current_guess] = last_response[0] + last_response[1]

        current_index, next_index = (
            last_response[2] * board_length,
            (last_response[2] + 1) * board_length,
        )

        if sum(self.color_count.values()) < board_length:
            if last_response[2] * board_length <= len(colors) - 1:
                self.current_guess = "".join(
                    i for i in colors[current_index:next_index]
                )
                return self.current_guess

            else:
                final_colors = "".join(i for i in colors[current_index:next_index])
                final_seen = board_length - sum(self.color_count.values())

                if final_colors != "" and final_seen != 0:
                    self.color_count[final_colors] = final_seen

        if not self.groups_added:
            self.groups_to_search = list(self.color_count.keys())
            self.groups_added = True

        # Pop each group of letters from groups_to_search and check each letter in the subgroup monochromatically
        if len(self.individual_colors) < board_length:
            if self.individual_start and (last_response[0] or last_response[1]):
                self.individual_colors.append(self.current_guess[0])

            if self.groups_to_search and not self.current_subgroup:
                self.current_subgroup = self.groups_to_search.pop(0)
                self.individual_start = True

            if self.current_subgroup:
                self.current_guess = self.current_subgroup[0] * board_length
                self.current_subgroup = self.current_subgroup[1:]

            return self.current_guess

        # At this point, all colors have been found and you need to find what order to place the colors in

        return self.current_guess

    # Completed Algorithm
    def TwoColorAlternating(self, board_length, colors, last_response):
        """
        Algorithm to handle TwoColorAlternating SCSA
        """
        # Initial Move - Reset all member variable containers (knowledge base)
        if last_response[2] == 0:
            self.done = False
            self.color_count.clear()
            self.inferences.clear()
            self.current_guess = ((colors[0] + colors[1]) * (board_length // 2 + 1))[
                :board_length
            ]
            return self.current_guess

        if last_response[1] == board_length or last_response[1] == board_length - 1:
            return (
                (self.current_guess[1] + self.current_guess[0])
                * (board_length // 2 + 1)
            )[:board_length]

        color_found = last_response[0] in [
            board_length // 2,
            board_length // 2 + 1,
        ] or last_response[1] in [board_length // 2, board_length // 2 + 1]

        if color_found and len(self.color_count) != 2:  # if a color is found
            # Would add a string like "AB" to the dict
            # bool represents if in correct positon
            self.color_count[self.current_guess[:2]] = last_response[0] > 0

        if len(self.color_count) != 2 and last_response[2] * 2 + 1 == len(colors):
            self.color_count[colors[-1] * 2] = True

        if len(self.color_count) != 2:
            if last_response[2] * 2 + 1 < len(colors):
                self.current_guess = (
                    (colors[last_response[2] * 2] + colors[last_response[2] * 2 + 1])
                    * (board_length // 2 + 1)
                )[:board_length]
            else:
                self.current_guess = colors[-1] * board_length
            return self.current_guess

        elif not self.done:
            key1, key2 = list(self.color_count.keys())
            first = key1[0] if self.color_count[key1] else key1[1]
            second = key2[1] if self.color_count[key2] else key2[0]

            self.inferences.append(
                ((first + second) * (board_length // 2 + 1))[:board_length]
            )

            first = key2[0] if self.color_count[key2] else key2[1]
            second = key1[1] if self.color_count[key1] else key1[0]

            self.inferences.append(
                ((first + second) * (board_length // 2 + 1))[:board_length]
            )
            self.done = True
        return self.inferences.pop(0)

    def FirstLast(self, board_length, colors, last_response):
        pass

    def UsuallyFewer(self, board_length, colors, last_response):
        pass

    def PreferFewer(self, board_length, colors, last_response):
        pass

    def Mystery1(self, board_length, colors, last_response):
        pass

    # Work in Progress
    def Mystery2(self, board_length, colors, last_response):
        """
        Algorithm to handle Mystery2 SCSA

        First identify the 4 letter combo.
        Multiple ways to consider this:
        Simply play mastermind (rao algo) on a 4 board and repeat the found pattern.
        Possible to make it more efficient by utilizing the full board space. Only useful for larger boards. Maybe the dichromatic strategy?
        Idea: we can take advantage of the board size. Knowing that they repeat the 4 letter string, we can use monochromatic guessing of size 4 for each available 4 set. For example, if we are given an 8 board, guess AAAABBBB, or 12 board guess AAAABBBBCCCC. This becomes more efficient the larger the board size, but only up to a certain extent.
        After the colors are identified, use RAO to crack the code.
        """
        # Checks if this is the first guess
        if last_response[2] == 0:
            # Resets containers
            # Stores the dichromatic guesses that contain the correct colors
            self.colors = []

            # Stores the monochromatic guesses, based on the dichromatic pairs, to test for individual colors
            self.inferences = []

            # Stores The two colors that are used in the code
            self.two_colors = []

            # Flag for if the monochromatic guesses are made
            # After the guesses are made, if only one pair of colors is in the set, the monochromatic colors are those two individual colors
            # If two pairs are in the set, the monochromatic colors are the four individual colors
            self.mono_made = False

            # Flag for if the monochromatic guesses have all been checked
            self.mono_checked = False

            self.current_guess = "".join(
                colors[0] for _ in range(board_length // 2)
            ) + "".join(colors[1] for _ in range(board_length - board_length // 2))

            self.current_index = 0

            self.max_correct = 0

            return self.current_guess

        if len(self.colors) != 2 and (
            last_response[0] or last_response[1] or last_response[2] > len(colors) // 2
        ):  # if a color is found
            # Would add a string like "AB" to the dict
            # bool represents if in correct positon
            self.colors.append("".join(self.current_guess[0] + self.current_guess[-1]))

        # Figuring out which two doubles contains the correct colors
        if len(self.colors) != 2 and last_response[2] < len(colors) // 2:
            self.current_guess = "".join(
                colors[last_response[2] * 2] for _ in range(board_length // 2)
            ) + "".join(
                colors[last_response[2] * 2 + 1]
                for _ in range(board_length - board_length // 2)
            )
            return self.current_guess

        # By this stage, either all colors are found or the last colors have been checked
        # Time to submit the 4 monochromatic colors
        if not self.mono_made:
            self.mono_made = True
            if len(self.colors) == 2:
                first, second = list(self.colors)
                self.inferences.append(first[0] * board_length)
                self.inferences.append(first[1] * board_length)
                self.inferences.append(second[0] * board_length)
                self.inferences.append(second[1] * board_length)
            else:  # Only two colors means they are guaranteed the answer and are ready to be tested
                self.two_colors.append(list(self.colors)[0][0])
                self.two_colors.append(list(self.colors)[0][1])
                self.mono_checked = 2
                self.current_guess = self.two_colors[1] * board_length
                return self.current_guess

        if len(self.two_colors) != 2 and self.mono_checked > 0:
            if last_response[0] > 0:
                self.two_colors.append(self.current_guess[0])

        if len(self.two_colors) != 2:
            self.mono_checked += 1
            self.current_guess = self.inferences.pop(0)
            # print("curr guess", self.current_guess)
            return self.current_guess

    def Mystery3(self, board_length, colors, last_response):
        pass

    def Mystery4(self, board_length, colors, last_response):
        pass

    # Completed Algorithm
    def Mystery5(self, board_length, colors, last_response):
        """
        Algorithm to handle Mystery5 SCSA
        (Adapted code from our TwoColors algorithm)

        1. First Guess dichromatically all the colors or until we find the 2 colors that show valid placements.
        2. After identifying the two, we simply put them into the xyxyy xyxyy pattern.
        This can take one try or maybe two tries, depending on what we set for x and y.
        *Should scale to infinite board sizes*
        """
        # Checks if this is the first guess - Resets containers
        if last_response[2] == 0:
            # Stores the dichromatic guesses that contain the correct colors
            self.colors = []

            # Stores the monochromatic guesses, based on the dichromatic pairs, to test for individual colors
            self.inferences = []

            # Stores The two colors that are used in the code
            self.two_colors = []

            # Flag for if the monochromatic guesses are made
            # After the guesses are made, if only one pair of colors is in the set, the monochromatic colors are those two individual colors
            # If two pairs are in the set, the monochromatic colors are the four individual colors
            self.mono_made = False

            # Flag for if the monochromatic guesses have all been checked
            self.mono_checked = False

            self.current_guess = "".join(
                colors[0] for _ in range(board_length // 2)
            ) + "".join(colors[1] for _ in range(board_length - board_length // 2))

            self.current_index = 0

            self.max_correct = 0

            # After we identify the 2 colors, put the 2 potential combinations here
            self.solutions = []

            return self.current_guess

        if len(self.colors) != 2 and (
            last_response[0] or last_response[1] or last_response[2] > len(colors) // 2
        ):  # if a color is found
            # Would add a string like "AB" to the dict
            # bool represents if in correct positon
            self.colors.append("".join(self.current_guess[0] + self.current_guess[-1]))

        # Figuring out which two doubles contains the correct colors
        if len(self.colors) != 2 and last_response[2] < len(colors) // 2:
            self.current_guess = "".join(
                colors[last_response[2] * 2] for _ in range(board_length // 2)
            ) + "".join(
                colors[last_response[2] * 2 + 1]
                for _ in range(board_length - board_length // 2)
            )
            return self.current_guess

        if (
            len(self.colors) != 2
            and last_response[2] >= len(colors) // 2
            and len(colors) % 2 == 1
        ):
            self.colors.append(colors[-1] + colors[-1])

        # By this stage, either all colors are found or the last colors have been checked
        # Time to submit the 4 monochromatic colors
        if not self.mono_made:
            self.mono_made = True
            if len(self.colors) == 2:
                first, second = list(self.colors)
                self.inferences.append(first[0] * board_length)
                self.inferences.append(first[1] * board_length)
                self.inferences.append(second[0] * board_length)
                self.inferences.append(second[1] * board_length)
            else:
                # Only two colors means they are guaranteed the answer and are ready to be tested
                self.two_colors.append(list(self.colors)[0][0])
                self.two_colors.append(list(self.colors)[0][1])
                self.mono_checked = 2
                self.current_guess = self.two_colors[1] * board_length
                return self.current_guess

        if len(self.two_colors) != 2 and self.mono_checked > 0:
            if last_response[0] > 0:
                self.two_colors.append(self.current_guess[0])

        if len(self.two_colors) != 2:
            self.mono_checked += 1
            self.current_guess = self.inferences.pop(0)
            # print("curr guess", self.current_guess) # Debugging
            return self.current_guess

        # Colors found --> create and store potential solution strings
        if not self.solutions:
            x, y = self.two_colors[0], self.two_colors[1]

            # When the board length is divisible by 5 - repeat full pattern
            if board_length % 5 == 0:
                self.solutions.append(
                    ("".join([x, y, x, y, y]) * (board_length // 5))[:board_length]
                )
                self.solutions.append(
                    ("".join([y, x, y, x, x]) * (board_length // 5))[:board_length]
                )
            # Don't use full pattern - cut off to fit the board length
            else:
                pattern1 = ("".join([x, y, x, y, y]) * ((board_length // 5) + 1))[:board_length]
                pattern2 = ("".join([y, x, y, x, x]) * ((board_length // 5) + 1))[:board_length]
                self.solutions.append(pattern1)
                self.solutions.append(pattern2)
            
        # Try the two potential solutions
        self.current_guess = self.solutions.pop(0)
        return self.current_guess

    # Completed Algorithm
    def Rao(self, board_length, colors, last_response):
        """
        General Algorithm to handle SCSAs that we haven't cracked yet
        """
        def Getnext(N, colors):
            """Constructs the next trial arrangement based on the given logic."""
            valid_colors = []

            # Iterate through all positions to build the guess
            for i in range(N):
                # Case 1: If the position is tied to a color
                if Tied(i):
                    gi = Itscolor(i)  # Assign the tied color to the current position
                    if Itscolor(i) == None:
                        print("case1")
                        gi = colors[0]
                # Case 2: If the position is the next possible position for a color that is being fixed
                elif i == Nextpos(self.being_fixed):
                    gi = self.being_fixed  # Use the second unfixed color
                    if self.being_fixed == None:
                        print("case2")
                        gi = colors[i]
                # Case 3: If the length of inferences equals N, use the second unfixed color
                elif len(self.inferences) + len(self.tied_colors) == N:
                    gi = Secondunfixed()
                    if Secondunfixed() == None:
                        print("case3")
                        gi = colors[i]
                else:
                    # Case 4: Otherwise, use a color being considered
                    gi = self.being_considered

                    if self.being_considered == None:

                        gi = self.being_fixed if self.being_fixed != None else colors[i]

                valid_colors.append(
                    gi
                )  # Add the determined color for position i to the guess list

            self.current_guess = "".join(
                valid_colors
            )  # Combine the list of colors into a string
            return self.current_guess

        def Tied(i):
            """Returns True if position i is tied to a specific color."""
            for (
                color,
                positions,
            ) in self.tied_colors:  # Iterate over each color and its tied positions
                if i == positions:  # If the position is tied to a color
                    return True
            return False

        def Itscolor(i):
            """Returns the color tied to position i."""
            for color, positions in self.tied_colors:
                if i == positions:  # If the position is tied to this color
                    return color  # Return the color tied to position i
            return None  # Return None if no color is tied to position i

        def Nextpos(color):
            """Returns the next available position for color i."""
            for c, position in self.inferences:
                if c == color:
                    return position[0]
            return None

        def Secondunfixed():
            # Iterate through the inferences list
            for color, _ in self.inferences:
                # Return the first color that doesn't match self.being_fixed
                if color != self.being_fixed:
                    return color
            # If no different color is found, return None (or some default if needed)
            if len(self.inferences) > 1:
                return self.inferences[1][0]
            return self.being_fixed

        def update(colors, board_length, bulls, cows):
            """Updates inferences based on the latest guess results."""

            # Calculate gain
            num_fixed = len(self.tied_colors)

            gain = (bulls + cows) - num_fixed - (self.being_fixed != None)

            with open("guess_log.txt", "a") as file:
                file.write(f"Updating\n")
                file.write(
                    f"gain = (bulls{bulls} + cows{cows}) - num_fixed{num_fixed}  - (self.being_fixed != None)"
                )
                file.write(f"Gain: {gain}\n")

            add_lists(gain, board_length)

            # Handle cases based on the number of cows
            if cows == 0:
                # being_fixed is correct in current position
                fix(self.being_fixed)
                bump()

            elif cows == 1:
                # being_fixed and being_considered are incorrect in current position
                if self.being_fixed != None:
                    del_position(self.being_fixed, self.being_considered)
                del_position(self.being_fixed, self.being_fixed)
            elif cows == 2:
                with open("guess_log.txt", "a") as file:
                    file.write(
                        f"calling fix1 on {self.being_considered} to {self.being_fixed}\n"
                    )
                # Fix being_considered in the position of being_fixed
                if self.being_considered == None:
                    fix1(Secondunfixed(), self.being_fixed)
                else:
                    fix1(self.being_considered, self.being_fixed)

            with open("guess_log.txt", "a") as file:
                file.write(f"self.inferences before clean up: {self.inferences}\n")
                file.write(f"self.tied_color before clean up: {self.tied_colors}\n")

            # Final cleanup and preparation for the next round
            cleanup()
            nextcolor(board_length, colors)
            with open("guess_log.txt", "a") as file:
                file.write(f"self.inferences after update: {self.inferences}\n")
                file.write(f"self.tied_color after update: {self.tied_colors}\n")

        def add_lists(gain, board_length):
            """
            Adds sublists to inferences, equal to the number of gain.
            Each sublist starts with the header being_considered and has an empty list of positions.
            """
            known = len(self.inferences) + len(self.tied_colors)
            if known < board_length:
                all_positions = list(
                    range(0, board_length)
                )  # Create a list of all positions (1 to N)

                for _ in range(gain):
                    # Append a new sublist to inferences with being_considered as the color and all positions as potential choices
                    self.inferences.append(
                        (self.being_considered, all_positions.copy())
                    )

        def fix(color):
            """Fixes the given color in its next available position, removes it from inferences,
            and adds it to tied_colors with the first position."""
            for i, (col, positions) in enumerate(self.inferences):
                if col == color and positions:
                    first_position = positions[0]  # Get the first available position
                    # Add the color and its fixed position to tied_colors
                    self.tied_colors.append((color, first_position))
                    # Remove the color from inferences
                    with open("guess_log.txt", "a") as file:
                        file.write(f"removing poistion {i}")
                    self.inferences.pop(i)
                    # Perform cleanup to remove this position from other colors' lists
                    break
            cleanup()

        def bump():
            if self.inferences:
                self.being_fixed = self.inferences[0][0]
            else:
                self.being_fixed = None

        def del_position(color_i, color_j):
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

        def fix1(color_i, color_j):
            """
            Fixes color_i in the current position of color_j and removes this position from other lists in inferences.

            Parameters:
            - color_i: The color to be fixed.
            - color_j: The color whose current position will be used to fix color_i.
            """
            with open("guess_log.txt", "a") as file:
                file.write(
                    f"doing fix1 {self.being_considered} to {self.being_fixed}\n"
                )
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
                        cleanup()
                        break  # Exit after removing the first occurrence

        def cleanup():
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
                    updated_positions = [
                        pos for pos in positions if pos not in positions_to_remove
                    ]

                    # If there are fewer positions after cleanup, update inferences
                    if len(updated_positions) != len(positions):
                        self.inferences[i] = (color, updated_positions)
                        changes_made = True

                    if len(updated_positions) == 0:
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
            if self.inferences:
                self.being_fixed = self.inferences[0][0]

        def nextcolor(board_length, colors):
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

        if last_response[2] == 0:
            # with open("guess_log.txt", "a") as file:
            # file.write(f"emptying the inferences list\n")
            self.inferences = []  # List of (color, possible positions)
            self.tied_colors = []  # List of (color, tied positions)
            self.being_fixed = None
            self.being_considered = None
        """
        Makes guesses based on feedback, generating valid guesses based on known color distribution and inferences.
        """

        with open("guess_log.txt", "a") as file:
            # Write relevant information to the file
            file.write(f"Last Guess: {self.current_guess}\n")
            file.write(f"Last Response: {last_response}\n")

        with open("guess_log.txt", "a") as file:
            exact_matches, partial_matches, num_guesses = last_response
            current_guess = num_guesses + 1
            file.write(f"calling update\n")
        update(colors, board_length, exact_matches, partial_matches)

        with open("guess_log.txt", "a") as file:
            # Write inferences and tied_colors to the file
            file.write(f"Tied Colors: {self.tied_colors}\n")

            file.write(f"Being consider: {self.being_considered}\n")
            file.write(f"Being fixed   : {self.being_fixed}\n")
            self.current_guess = Getnext(board_length, colors)

            # Write the current guess to the file
            file.write(f"Current Guess: {self.current_guess}\n")
            file.write("\n")

        return self.current_guess
