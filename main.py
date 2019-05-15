#!/usr/bin/env python3

"""
Entry-point for HexSweeper.
"""

from game_ui import GameUI
from difficulty import Difficulty

if __name__ == '__main__':
    GameUI(Difficulty.EASY)
