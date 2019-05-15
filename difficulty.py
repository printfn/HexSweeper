"""
This defines the game's difficulty settings.
"""

from enum import Enum, auto

class Difficulty(Enum):
    """
    HexSweeper currently supports 3 standard difficulty levels,
    and a custom setting that lets the player choose a custom
    board size and mine count.
    """
    EASY = auto()
    INTERMEDIATE = auto()
    ADVANCED = auto()
    CUSTOM = auto()
