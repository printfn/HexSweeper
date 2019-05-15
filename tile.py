"""
This module contains the Tile class, which described a
single hexagonal tile.
"""

from typing import Optional, Any

class Tile:
    """
    This class contains all data required to define a tile.
    As Python does not support access control, any members that
    must not be accessed externally are prefixed with an underscore.
    """
    def __init__(self, game: Any, x: int, y: int) -> None:
        self.game = game
        self.x_coord = x
        self.y_coord = y
        self._revealed = False
        self._mine = False
        self._flag = False

    def is_revealed(self) -> bool:
        """
        Checks if the tile is revealed (i.e. has been clicked on)
        """
        return self._revealed

    def has_mine(self) -> bool:
        """
        Checks if the tile has a mine
        """
        return self._mine

    def has_flag(self) -> bool:
        """
        Checks if the user has set a flag on this tile
        """
        return self._flag

    def adjacent_mine_count(self) -> int:
        """
        Returns the number of adjacent mines to this current tile
        """
        return self.game.adjacent_mine_count(self.x_coord,
                                             self.y_coord)

    def has_adjacent_mines(self) -> bool:
        """
        Returns whether the current tile has any adjacent mines.
        """
        return self.adjacent_mine_count() > 0

    def color(self) -> str:
        """
        Colour to use for rendering this tile as a hexagon
        """
        if self.is_revealed():
            if self.has_mine():
                return 'red'
            if self.has_adjacent_mines():
                return 'orange'
            return 'lightgreen'
        if self.has_flag():
            return 'purple'
        return 'lightblue'

    def text(self) -> Optional[str]:
        """
        Text that should be shown on this tile
        """
        if not self.has_mine() and self.is_revealed():
            if self.has_adjacent_mines():
                return str(self.adjacent_mine_count())
        # otherwise return None, which will prevent
        # any text from being shown on this tile
        return None

    def can_toggle_flag(self) -> bool:
        """
        Whether the user is allowed to set/unset flags on this tile
        """
        if self.has_flag():
            return True
        old_color = self.color()
        self._flag = True
        new_color = self.color()
        self._flag = False
        if old_color == new_color:
            return False
        return True

    def change_into_mine(self) -> None:
        """
        Tile.__init__ only creates non-mine tiles. This method
        can then be used to change some of those tiles into mines.
        """
        self._mine = True

    def set_flag(self) -> None:
        """ If allowed, change this tile to have a flag """
        if self.has_flag():
            return
        if not self.can_toggle_flag():
            return
        self._flag = True

    def unset_flag(self) -> None:
        """ If allowed, change this tile to not have a flag """
        if not self.has_flag():
            return
        if not self.can_toggle_flag():
            return
        self._flag = False

    def reveal(self) -> None:
        """
        Called on left-click and also when the game is over
        and all tiles (incl. mine positions) are revealed to the user.
        """
        if not self.has_flag():
            self._revealed = True

    def __repr__(self) -> str:
        """
        Useful only for debugging: this text is printed to the console
        when you try to print a tile object.
        """
        return (f'<Tile revealed={self.is_revealed()} '
                + f'mine={self.has_mine()} '
                + f'flag={self.has_flag()}>')
