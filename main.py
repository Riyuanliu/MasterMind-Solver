# Main file to run game of Mastermind based on command-line arguments.
# See example.ipynb for other ways to use the Mastermind representation.

import argparse
from scsa import *
from player import *
from mastermind import *
import numpy as np
import argparse

def play_mastermind_game():
    parser = argparse.ArgumentParser(description="Play a game of Mastermind.")
    parser.add_argument("--board_length", nargs="?", type=int, required=True)
    parser.add_argument(
        "--num_colors", nargs="?", type=int, required=True, choices=range(1, 27)
    )
    parser.add_argument(
        "--player_name",
        nargs="?",
        type=str,
        choices=[
            "RandomFolks",
            "Boring",
            "RubberCorn_B1",
            "RubberCorn_B2",
            "RubberCorn_B3",
            "RubberCorn_B4",
            "Smart_Player",
        ],
    )
    parser.add_argument(
        "--scsa_name",
        nargs="?",
        type=str,
        required=True,
        choices=[
            "InsertColors",
            "TwoColor",
            "ABColor",
            "TwoColorAlternating",
            "OnlyOnce",
            "FirstLast",
            "UsuallyFewer",
            "PreferFewer",
        ],
    )
    parser.add_argument("--num_rounds", nargs="?", type=int, required=True)

    args = parser.parse_args()

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
        else:
            raise ValueError("Unrecognized Player.")

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
        else:
            raise ValueError("Unrecognized SCSA.")

    player = str_to_player(args.player_name)
    scsa = str_to_scsa(args.scsa_name)
    colors = [chr(i) for i in range(65, 91)][: args.num_colors]
    mastermind = Mastermind(args.board_length, colors)
    mastermind.play_tournament(player, scsa, args.num_rounds)

def run_practice_tournament(board_length: int, num_colors: int, player: Player, scsa_name: str, code_file: str):
    """
    Sets up and runs a Mastermind practice tournament.
    
    Parameters:
        board_length (int): Number of pegs in the game.
        num_colors (int): Number of colors available for guesses.
        player (Player): The player object (e.g., Baseline4).
        scsa_name (str): Name of the SCSA method for tracking and analysis.
        code_file (str): File name to save tournament data.
    """
    colors = [chr(i) for i in range(65, 91)][:num_colors]  # Generate colors list based on num_colors
    mastermind = Mastermind(board_length, colors)  # Initialize the game
    mastermind.practice_tournament(player, scsa_name, code_file)  # Run the practice tournament

def auto_run_all():
    players_choice=[
            # "RubberCorn_B1",
            # "RubberCorn_B2",
            # "RubberCorn_B3",
            # "RubberCorn_B4",
            # "Smart_Player",
            # Main Player
            "RubberCorn",
            # "Super_Smart_Player"
        ],
    scsa_choices=[
            # "InsertColors",
            # "TwoColor",
            "ABColor",
            # "TwoColorAlternating",
            # "OnlyOnce",
            # "FirstLast",
            # "UsuallyFewer",
            # "PreferFewer",
            # "Mystery1",
            # "Mystery2",
            # "Mystery3",
            # "Mystery4",
            # "Mystery5"
        ],
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
    
    def isMystery(scsa_name):
        mystery = ["Mystery1", "Mystery2", "Mystery3", "Mystery4"]
        file_name = ["Mystery1_10_7_200.txt", "Mystery2_10_7_200.txt", "Mystery3_10_7_200.txt", "Mystery4_10_7_200.txt", "Mystery5_10_7_200.txt"]
        if scsa_name in mystery:
            return file_name[mystery.index(scsa_name)]
        return None

    num_colors =  26
    board_length = 21
    num_rounds = 1
    
    for player_name in players_choice[0]:
        scores = []
        print(player_name)
        for scsa_name in scsa_choices[0]:
            # print(scsa_name)
            if(isMystery(scsa_name) != None):
                player = str_to_player(player_name)
                file_name = isMystery(scsa_name)
                # print(file_name)
                colors = [chr(i) for i in range(65, 91)][: num_colors]
                mastermind = Mastermind(board_length, colors)
                print(mastermind.practice_tournament(player, scsa_name, file_name))
            else:
                player = str_to_player(player_name)
                scsa = str_to_scsa(scsa_name)
                colors = [chr(i) for i in range(65, 91)][: num_colors]
                mastermind = Mastermind(board_length, colors)
                scores.append(mastermind.play_tournament(player, scsa, num_rounds).getscore())
                
        print(np.mean(scores))
        
        # python3 main.py --board_length 5 --num_colors 25 --player_name RubberCorn --scsa_name Mystery1  --num_rounds 1
# run_practice_tournament(50, 26, RubberCorn(), "TwoColorAlternating", "testing.txt")

#play_mastermind_game()

auto_run_all()