from mastermind import *
from scsa import *
from player import *
from RubberCorn_d4 import *
import time

# TESTING MYSTERY5 SCSA Created
# board_length = 10
# num_colors = 7
# colors = [chr(i) for i in range(65, 91)][
#     :num_colors
# ]  # Retrieves first num_colors from list of all colors
# scsa = Mystery2()

# codes = scsa.generate_codes(board_length, colors, num_codes=10)

# print(codes)

board_length = 501  # Number of pegs
num_colors = 6  # Number of colors
colors = [chr(i) for i in range(65, 91)][
    :num_colors
]  # Retrieves first num_colors from list of all colors
player = RubberCorn()
scsa = Mystery5()
num_rounds = 100

mastermind = Mastermind(board_length, colors)

mastermind.play_tournament(player, scsa, num_rounds)