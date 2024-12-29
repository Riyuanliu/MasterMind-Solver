import argparse
from scsa import *
from player import *
from mastermind import *
import numpy as np

# Helper function to convert player name to player object
def str_to_player(player_name: str) -> Player:
    if player_name == "RandomFolks":
        return RandomFolks()
    elif player_name == "Boring":
        return Boring()
    elif player_name == "RubberCorn_B1":
        return Baseline1()
    elif player_name == "RubberCorn_B2":
        return Baseline2()
    elif player_name == "RubberCorn_B3":
        return Baseline3()
    elif player_name == "RubberCorn_B4":
        return Baseline4()
    elif player_name == "Smart_Player":
        return SmartPlayer()
    elif player_name == "Super_Smart_Player":
        return SuperSmartPlayer()
    elif player_name == "RubberCorn":
        return RubberCorn()
    else:
        raise ValueError("Unrecognized Player.")

# Helper function to convert SCSA name to SCSA object
def str_to_scsa(scsa_name: str) -> SCSA:
    if scsa_name == "InsertColors":
        return InsertColors()
    elif scsa_name == "TwoColor":
        return TwoColor()
    elif scsa_name == "ABColor":
        return ABColor()
    elif scsa_name == "TwoColorAlternating":
        return TwoColorAlternating()
    elif scsa_name == "OnlyOnce":
        return OnlyOnce()
    elif scsa_name == "FirstLast":
        return FirstLast()
    elif scsa_name == "UsuallyFewer":
        return UsuallyFewer()
    elif scsa_name == "PreferFewer":
        return PreferFewer()
    elif scsa_name == "Mystery5":
        return Mystery5()
    else:
        raise ValueError("Unrecognized SCSA.")

# Helper function to check if the SCSA is a mystery one
def isMystery(scsa_name):
    mystery = ["Mystery1", "Mystery2", "Mystery3", "Mystery4"]
    file_name = ["Mystery1_10_7_200.txt", "Mystery2_10_7_200.txt", "Mystery3_10_7_200.txt", "Mystery4_10_7_200.txt", "Mystery5_10_7_200.txt"]
    if scsa_name in mystery:
        return file_name[mystery.index(scsa_name)]
    return None

# Main function to run the automatic tournament
def auto_run_all():
    global players_choice, scsa_choices, num_colors, board_length, num_rounds

    for player_name in players_choice:
        scores = []
        print(f"Running tournament for player: {player_name}")
        
        for scsa_name in scsa_choices:
            if isMystery(scsa_name) != None:
                # Handle mystery SCSA
                player = str_to_player(player_name)
                file_name = isMystery(scsa_name)
                colors = [chr(i) for i in range(65, 91)][:num_colors]
                mastermind = Mastermind(board_length, colors)
                print(f"Running Mystery SCSA: {scsa_name} using file {file_name}")
                mastermind.practice_tournament(player, scsa_name, file_name)
            else:
                # Handle regular SCSA
                player = str_to_player(player_name)
                scsa = str_to_scsa(scsa_name)
                colors = [chr(i) for i in range(65, 91)][:num_colors]
                mastermind = Mastermind(board_length, colors)
                result = mastermind.play_tournament(player, scsa, num_rounds)
                scores.append(result.getscore())
        
        # Print average score for the current player
        print(f"Average score for {player_name}: {np.mean(scores)}")


# Global variables for players_choice, scsa_choices, num_colors, and board_length
players_choice = [
    "RubberCorn",
    # "RandomFolks", 
    # "Boring", 
    # "Smart_Player",
    # "Super_Smart_Player"
]

scsa_choices = [
    "ABColor",
    # "InsertColors", 
    # "TwoColor", 
    # "TwoColorAlternating",
    # "OnlyOnce", 
    # "FirstLast", 
    # "Mystery1", 
    # "Mystery2", 
    # "Mystery3",
    # "Mystery4"
]

num_colors = 5  # Number of colors available
board_length = 4  # Number of pegs in the code
num_rounds = 1  # Number of rounds for the tournament

# Run the auto-run function
auto_run_all()
