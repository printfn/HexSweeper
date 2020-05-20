#!/usr/bin/env python3

"""
Entry-point for HexSweeper.
"""

import sys

if sys.version_info < (3, 6):
    print("Sorry, this program requires at least Python 3.6.")
    sys.exit(1)

# pylint: disable=wrong-import-position
from game_ui import GameUI
from difficulty import Difficulty

if __name__ == '__main__':
    GameUI(Difficulty.EASY)
