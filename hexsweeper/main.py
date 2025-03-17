#!/usr/bin/env python3

"""
Entry-point for HexSweeper.
"""

import sys

if sys.version_info < (3, 6):
    print("Sorry, this program requires at least Python 3.6.")
    sys.exit(1)

def run():
    # pylint: disable=wrong-import-position
    from hexsweeper.game_ui import GameUI
    GameUI()

if __name__ == '__main__':
    run()
