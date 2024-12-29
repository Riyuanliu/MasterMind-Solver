from itertools import product, permutations
import itertools
import random
from abc import ABC, abstractmethod
from scsa import list_to_str, InsertColors
import time
import threading

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


import time
import threading

class RubberCorn(Player):
    def __init__(self):
        open("guess_log.txt", "w").close()
        """Constructor for RubberCorn"""
        super().__init__()
        self.player_name = "RubberCorn"
        self.color_count = {}  # Store color counts from guesses
        self.current_guess = ""
        self.inferences = []  # List of (color, possible positions)
        self.max_correct = 0
        self.possible_guesses = []
        self.possible_set_guess = []
        self.current_index = 0  # Index of peg to evaluate currently
        self.start_time = 0  # Store the initial start time
        self.total_elapsed_time = 0  # Tracks cumulative elapsed time across calls
        

    def make_guess(
            self,
            board_length: int,
            colors: list[str],
            scsa_name: str,
            last_response: tuple[int, int, int],
        ) -> str:
            result = {"value": None}

            # Start the timer on the first call (last_response[2] == 0)
            if last_response[2] == 0:
                self.start_time = time.time()
                self.total_elapsed_time = 0  # Reset elapsed time for a new round
                # print(f"Timer started at {self.start_time:.1f}")

            # Update elapsed time
            current_time = time.time()
            elapsed_since_last_guess = current_time - self.start_time
            self.total_elapsed_time += elapsed_since_last_guess
            self.start_time = current_time  # Update start_time for the next guess

            # Calculate remaining time for this guess
            remaining_time = 5 - self.total_elapsed_time

            # Define a helper function to handle the guess generation
            def guess_logic():
                nonlocal result  # Allow modification of result from inside the thread
                # Proceed with the normal guessing logic
                if len(colors) <= 8 and board_length <= 7 and scsa_name != "TwoColorAlternating":
                    result["value"] = self.SuperSmartPlayer(board_length, colors, last_response)
                    return

                match scsa_name:
                    case "TwoColor":
                        result["value"] = self.TwoColor(board_length, colors, last_response)
                        return

                    case "OnlyOnce":
                        # if board_length <= len(colors) and board_length <= 7:
                        #     result["value"] = self.OnlyOnce(board_length, colors, last_response)
                        # else:
                        result["value"] = self.Rao(board_length, colors, last_response)
                        return

                    case "TwoColorAlternating":
                        result["value"] = self.TwoColorAlternating(board_length, colors, last_response)
                        return

                    case "ABColor":
                        if board_length > 21:
                            result["value"] = self.Rao(board_length, colors, last_response)
                        else:
                            result["value"] = self.ABColor(board_length, colors, last_response)
                        return

                    case "Mystery2":
                        result["value"] = self.Mystery2(board_length, colors, last_response)
                        return

                    case "Mystery5":
                        result["value"] = self.Mystery5(board_length, colors, last_response)
                        return

                    case _:
                        result["value"] = self.Rao(board_length, colors, last_response)

            # If there is enough remaining time, execute the guess logic in a thread
            if remaining_time > 0:
                guess_thread = threading.Thread(target=guess_logic)
                guess_thread.start()
                guess_thread.join(timeout=remaining_time)  # Wait for the thread to finish or timeout

            # After the thread has finished or timed out
            if result["value"] is None:
                # print(f"Timeout reached. Returning default guess after {self.total_elapsed_time:.1f} seconds.")
                return "A" * board_length
            else:
                # print(f"Returning computed guess after {self.total_elapsed_time:.1f} seconds.")
                return result["value"]

    def ABColor(self, board_length, colors, last_response):
        """Implements the SuperSmartPlayer strategy."""

        if last_response[2] == 0:  # First guess
            if not self.possible_set_guess:  # Generate only if empty
                subset_colors = ['A', 'B']
                self.possible_set_guess = [''.join(p) for p in itertools.product(subset_colors, repeat=board_length)]
            self.possible_guesses = self.possible_set_guess.copy()
            # Create an initial guess pattern
            guess = ''.join(colors[:2] * (board_length // 2) + colors[:board_length % 2])
        else:
            # Define the feedback simulation function inside SuperSmartPlayer
            def simulate_feedback(secret: str, guess: str) -> tuple[int, int]:
                """Simulates feedback for a given guess against a hypothetical secret."""
                black_pegs = sum(a == b for a, b in zip(secret, guess))
                white_pegs = sum(min(secret.count(c), guess.count(c)) for c in set(secret)) - black_pegs
                return black_pegs, white_pegs

            # Filter remaining possibilities based on the last response
            self.possible_guesses = [
                g for g in self.possible_guesses
                if simulate_feedback(g, self.current_guess) == (last_response[0], last_response[1])
            ]
            # Pick the first valid guess from the remaining possibilities
            if(self.possible_guesses):
                guess = "A" * board_length
            else:
                guess = self.possible_guesses[0]

        # Update the current guess
        self.current_guess = guess
        return guess

    def TwoColor(self, board_length, colors, last_response):  # WIP
        if last_response[2] == 0:
            # Resets containers
            # Stores the dic
            # hromatic guesses that contain the correct colors
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

    def OnlyOnce(self, board_length, colors, last_response):  # WIP
        if last_response[2] == 0:  # First guess
            if not self.possible_set_guess:  # Generate only if empty
                self.possible_set_guess = [''.join(p) for p in itertools.permutations(colors, board_length)]
            self.possible_guesses = self.possible_set_guess.copy()
            # Create an initial guess pattern
            guess = ''.join(colors[:board_length])
        else:
            # Define the feedback simulation function inside SuperSmartPlayer
            def simulate_feedback(secret: str, guess: str) -> tuple[int, int]:
                """Simulates feedback for a given guess against a hypothetical secret."""
                black_pegs = sum(a == b for a, b in zip(secret, guess))
                white_pegs = sum(min(secret.count(c), guess.count(c)) for c in set(secret)) - black_pegs
                return black_pegs, white_pegs

            # Filter remaining possibilities based on the last response
            self.possible_guesses = [
                g for g in self.possible_guesses
                if simulate_feedback(g, self.current_guess) == (last_response[0], last_response[1])
            ]
            # Pick the first valid guess from the remaining possibilities
            guess = self.possible_guesses[0]

        # Update the current guess
        self.current_guess = guess
        return guess

    def TwoColorAlternating(self, board_length, colors, last_response):

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

    def Mystery2(self, board_length, colors, last_response):
        """
        Algorithm:
        First identify the 4 letter combo.
        Multiple ways to consider this:
        Simply play mastermind (rao algo) on a 4 board and repeat the found pattern.
        Possible to make it more efficient by utilizing the full board space. Only useful for larger boards. Maybe the dichromatic strategy?
        Idea: we can take advantage of the board size. Knowing that they repeat the 4 letter string, we can use monochromatic guessing of size 4 for each available 4 set. For example, if we are given an 8 board, guess AAAABBBB, or 12 board guess AAAABBBBCCCC. This becomes more efficient the larger the board size, but only up to a certain extent.
        After the colors are identified, use RAO to crack the code.
        """
        def Getnext(N, colors):
            """Constructs the next trial arrangement based on the given logic."""
            valid_colors = []

            if len(self.tied_colors) == 4:
                # Sort tied colors by their tied position (second value in the tuple)
                tied_colors_order = [color for color, _ in sorted(self.tied_colors, key=lambda x: x[1])]
                # Generate the repeating pattern based on the sorted order
                repeated_pattern = (tied_colors_order * (N // len(tied_colors_order) + 1))[:N]

                # Set the current guess as a string pattern
                self.current_guess = "".join(repeated_pattern)

                return self.current_guess


            # Iterate through all positions to build the guess
            for i in range(N):
                # Case 1: If the position is tied to a color
                if Tied(i):
                    gi = Itscolor(i)  # Assign the tied color to the current position
                    if Itscolor(i) == None:
                        # print("case1")
                        gi = colors[0]
                # Case 2: If the position is the next possible position for a color that is being fixed
                elif i == Nextpos(self.being_fixed):
                    gi = self.being_fixed  # Use the second unfixed color
                    if self.being_fixed == None:
                        # print("case2")
                        gi = colors[i]
                # Case 3: If the length of inferences equals N, use the second unfixed color
                elif len(self.inferences) + len(self.tied_colors) == N:
                    gi = Secondunfixed()
                    if Secondunfixed() == None:
                        # print("case3")
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
            for (color,positions) in self.tied_colors:  # Iterate over each color and its tied positions
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

            # with open("guess_log.txt", "a") as file:
            #     file.write(f"Updating\n")
            #     file.write(
            #         f"gain = (bulls{bulls} + cows{cows}) - num_fixed{num_fixed}  - (self.being_fixed != None)"
            #     )
            #     file.write(f"Gain: {gain}\n")

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
                # with open("guess_log.txt", "a") as file:
                #     file.write(
                #         f"calling fix1 on {self.being_considered} to {self.being_fixed}\n"
                #     )
                # Fix being_considered in the position of being_fixed
                if self.being_considered == None:
                    fix1(Secondunfixed(), self.being_fixed)
                else:
                    fix1(self.being_considered, self.being_fixed)

            # with open("guess_log.txt", "a") as file:
            #     file.write(f"self.inferences before clean up: {self.inferences}\n")
            #     file.write(f"self.tied_color before clean up: {self.tied_colors}\n")

            # Final cleanup and preparation for the next round
            cleanup()
            nextcolor(board_length, colors)
            # with open("guess_log.txt", "a") as file:
            #     file.write(f"self.inferences after update: {self.inferences}\n")
            #     file.write(f"self.tied_color after update: {self.tied_colors}\n")

        def add_lists(gain, board_length):
            """
            Adds sublists to inferences, equal to the number of gain.
            Each sublist starts with the header being_considered and has an empty list of positions.
            """
            known = len(self.inferences) + len(self.tied_colors)
            if known < board_length:
                all_positions = list(
                    range(0, 4)
                )  # Create a list of all positions (1 to N)

                # for _ in range(gain):
                #     # Append a new sublist to inferences with being_considered as the color and all positions as potential choices
                #     self.inferences.append(
                #         (self.being_considered, all_positions.copy())
                #     )
                if(self.being_considered != None and gain > 0 ):
                    self.inferences.append(
                            (self.being_considered, all_positions)
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
                    # with open("guess_log.txt", "a") as file:
                    #     file.write(f"removing poistion {i}")
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
            # with open("guess_log.txt", "a") as file:
                # file.write(
                #     f"doing fix1 {self.being_considered} to {self.being_fixed}\n"
                # )
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
            for color, _ in self.inferences:
                if color not in self.tied_colors:
                    self.being_fixed = color
                    break

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
            self.not_need_to_consider = []
            self.being_fixed = None
            self.being_considered = None
        """
        Makes guesses based on feedback, generating valid guesses based on known color distribution and inferences.
        """

        # with open("guess_log.txt", "a") as file:
        #     # Write relevant information to the file
        #     file.write(f"Last Guess: {self.current_guess}\n")
        #     file.write(f"Last Response: {last_response}\n")

        # with open("guess_log.txt", "a") as file:
        exact_matches, partial_matches, num_guesses = last_response
        current_guess = num_guesses + 1
            # file.write(f"calling update\n")
        update(colors, board_length, exact_matches, partial_matches)

        # with open("guess_log.txt", "a") as file:
        #     # Write inferences and tied_colors to the file
        #     file.write(f"Tied Colors: {self.tied_colors}\n")

        #     file.write(f"Being consider: {self.being_considered}\n")
        #     file.write(f"Being fixed   : {self.being_fixed}\n")
        self.current_guess = Getnext(board_length, colors)

            # # Write the current guess to the file
            # file.write(f"Current Guess: {self.current_guess}\n")
            # file.write("\n")

        return self.current_guess

    def Mystery5(self, board_length, colors, last_response):
        """
        Algorithm:
        Adapted code from TwoColorsAlternating algorithm
        """

        # Check if this is the first guess (last_response[2] indicates the attempt number)
        if last_response[2] == 0:
            self.done = False  # Reset the "done" state for a new round
            self.color_count.clear()  # Clear previously identified colors
            self.inferences.clear()  # Clear any inferences made in previous rounds
            
            # Create an initial alternating pattern of the first two colors
            # Repeat it enough times to cover the board, then slice to fit
            self.current_guess = (
                (colors[0] + colors[1] + colors[0] + colors[1] + colors[1]) * (board_length // 5 + 1)
            )[:board_length]
            return self.current_guess

        # Check if the response indicates that more than 2/3 of the board has the correct colors
        if last_response[1] > board_length * 2 / 3:  # Naive threshold for high match
            x = self.current_guess[0]
            y = self.current_guess[1]
            # Alternate x and y to refine the guess and cover the board length
            return (
                (y + x + y + x + x)
                * (board_length // 5 + 1)
            )[:board_length]

        # Check if a correct color is identified based on the response
        color_found = last_response[0] > 0 or last_response[1] > 0

        # If a color is found and fewer than 2 colors are identified, update color_count
        if color_found and len(self.color_count) != 2:
            self.color_count[self.current_guess[:2]] = last_response[0] > 0  # Map color pair to response

        # If fewer than 2 colors have been identified
        if len(self.color_count) != 2:
            # Determine the next color pair to guess based on response index
            if last_response[2] * 2 + 1 < len(colors):
                x = colors[last_response[2] * 2]
                y = colors[last_response[2] * 2 + 1]
                self.current_guess = (
                    (x + y + x + y + y) * (board_length // 5 + 1)
                )[:board_length]
            else:
                # Default to the last color if out of pairs
                self.current_guess = colors[-1] * board_length
            return self.current_guess

        # If 2 colors have been identified but further refinement is required
        elif not self.done:
            key1, key2 = list(self.color_count.keys())  # Extract the two identified color pairs
            
            # Infer the sequence based on the color mapping
            first = key1[0] if self.color_count[key1] else key1[1]  # First color from key1
            second = key2[1] if self.color_count[key2] else key2[0]  # Second color from key2
            
            # Append a possible inference pattern
            self.inferences.append(
                ((first + second + first + second + second) * (board_length // 5 + 1))[:board_length]
            )

            # Create another inference pattern by swapping roles of key1 and key2
            first = key2[0] if self.color_count[key2] else key2[1]
            second = key1[1] if self.color_count[key1] else key1[0]
            
            self.inferences.append(
                ((first + second + first + second + second) * (board_length // 5 + 1))[:board_length]
            )
            self.done = True  # Mark as done once inferences are generated

        # Return and remove the next inference pattern from the list
        return self.inferences.pop(0)

    def Rao(self, board_length, colors, last_response):

        def Getnext(N, colors):
            """Constructs the next trial arrangement based on the given logic."""
            valid_colors = []

            # Iterate through all positions to build the guess
            for i in range(N):
                # Case 1: If the position is tied to a color
                if Tied(i):
                    gi = Itscolor(i)  # Assign the tied color to the current position
                    if Itscolor(i) == None:
                        # print("case1")
                        gi = colors[0]
                # Case 2: If the position is the next possible position for a color that is being fixed
                elif i == Nextpos(self.being_fixed):
                    gi = self.being_fixed  # Use the second unfixed color
                    if self.being_fixed == None:
                        # print("case2")
                        gi = colors[i]
                # Case 3: If the length of inferences equals N, use the second unfixed color
                elif len(self.inferences) + len(self.tied_colors) == N:
                    gi = Secondunfixed()
                    if Secondunfixed() == None:
                        # print("case3")
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

            # with open("guess_log.txt", "a") as file:
            #     file.write(f"Updating\n")
            #     file.write(
            #         f"gain = (bulls{bulls} + cows{cows}) - num_fixed{num_fixed}  - (self.being_fixed != None)"
            #     )
            #     file.write(f"Gain: {gain}\n")

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
                # with open("guess_log.txt", "a") as file:
                #     file.write(
                #         f"calling fix1 on {self.being_considered} to {self.being_fixed}\n"
                #     )
                # Fix being_considered in the position of being_fixed
                if self.being_considered == None:
                    fix1(Secondunfixed(), self.being_fixed)
                else:
                    fix1(self.being_considered, self.being_fixed)

            # with open("guess_log.txt", "a") as file:
            #     file.write(f"self.inferences before clean up: {self.inferences}\n")
            #     file.write(f"self.tied_color before clean up: {self.tied_colors}\n")

            # Final cleanup and preparation for the next round
            cleanup()
            nextcolor(board_length, colors)
            # with open("guess_log.txt", "a") as file:
            #     file.write(f"self.inferences after update: {self.inferences}\n")
            #     file.write(f"self.tied_color after update: {self.tied_colors}\n")

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
                    # with open("guess_log.txt", "a") as file:
                    #     file.write(f"removing poistion {i}")
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
            # with open("guess_log.txt", "a") as file:
            #     file.write(
            #         f"doing fix1 {self.being_considered} to {self.being_fixed}\n"
            #     )
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
            positions_to_remove = {pos for _, pos in self.tied_colors}

            while True:
                changes_made = False
                new_inferences = []

                for color, positions in self.inferences:
                    # Remove tied positions
                    updated_positions = [pos for pos in positions if pos not in positions_to_remove]

                    if len(updated_positions) == 1:
                        tied_position = updated_positions[0]
                        # Add the color and position to tied_colors
                        self.tied_colors.append((color, tied_position))
                        # Mark position to be removed in future passes
                        positions_to_remove.add(tied_position)
                        changes_made = True
                    elif len(updated_positions) > 1:
                        # Keep only inferences with multiple positions remaining
                        new_inferences.append((color, updated_positions))

                # Update self.inferences after processing all changes
                self.inferences = new_inferences

                # Exit loop if no changes were made in this pass
                if not changes_made:
                    break

            # If there are still inferences left, pick the next color to fix
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

        # with open("guess_log.txt", "a") as file:
            # Write relevant information to the file
            # file.write(f"Last Guess: {self.current_guess}\n")
            # file.write(f"Last Response: {last_response}\n")
        exact_matches, partial_matches, num_guesses = last_response
        current_guess = num_guesses + 1
        # with open("guess_log.txt", "a") as file:
        #     file.write(f"calling update\n")
        update(colors, board_length, exact_matches, partial_matches)

        # with open("guess_log.txt", "a") as file:
        #     # Write inferences and tied_colors to the file
        #     file.write(f"Tied Colors: {self.tied_colors}\n")

        #     file.write(f"Being consider: {self.being_considered}\n")
        #     file.write(f"Being fixed   : {self.being_fixed}\n")
        self.current_guess = Getnext(board_length, colors)

            # # Write the current guess to the file
            # file.write(f"Current Guess: {self.current_guess}\n")
            # file.write("\n")

        return self.current_guess

    def SuperSmartPlayer(self, board_length: int, colors: list[str], last_response: tuple[int, int, int]) -> str:
        """Implements the optimized SuperSmartPlayer strategy."""

        # Helper function for simulating feedback
        def _simulate_feedback(secret: str, guess: str) -> tuple[int, int]:
            """Simulates feedback for a given guess against a hypothetical secret."""
            black_pegs = sum(a == b for a, b in zip(secret, guess))
            white_pegs = sum(min(secret.count(c), guess.count(c)) for c in set(guess)) - black_pegs
            return black_pegs, white_pegs

        if last_response[2] == 0:  # First guess
            if not self.possible_set_guess:  # Generate only if empty
                self.possible_set_guess = [''.join(p) for p in itertools.product(colors, repeat=board_length)]
            self.possible_guesses = self.possible_set_guess.copy()
            # Create an initial guess pattern (balanced distribution of first two colors)
            guess = ''.join(colors[:2] * (board_length // 2) + colors[:board_length % 2])
        else:
            # Use list comprehension to filter guesses efficiently
            self.possible_guesses = [
                g for g in self.possible_guesses
                if _simulate_feedback(g, self.current_guess) == (last_response[0], last_response[1])
            ]
            # Pick the first valid guess (or optimize selection for minimal remaining possibilities)
            guess = self.possible_guesses[0]

        # Update the current guess
        self.current_guess = guess
        return guess
