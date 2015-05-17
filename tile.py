class Tile:
    """
    This class contains all data required to define a tile.
    As Python does not support access control, any members that
    must not be accessed externally are prefixed with an underscore.
    """
    def __init__(self, game, x, y):
        self.game = game
        self.x = x
        self.y = y
        self._revealed = False
        self._mine = False
        self._flag = False
    # accessors (getters) for the private instance variables
    def is_revealed(self):
        return self._revealed
    def has_mine(self):
        return self._mine
    def has_flag(self):
        return self._flag

    # colour to use for rendering this tile as a hexagon
    def color(self):
        if self.is_revealed():
            if self.has_mine():
                return 'red'
            if self.game.adjacent_mine_count(self.x, self.y) > 0:
                return 'orange'
            return 'lightgreen'
        else:
            if self.has_flag():
                return 'purple'
            return 'lightblue'
    def text(self):
        if not self.has_mine():
            if self.is_revealed():
                if self.game.adjacent_mine_count(self.x, self.y) > 0:
                    return str(self.game.adjacent_mine_count(self.x, self.y))
        # otherwise return None, which will prevent
        # any text from being shown on this tile
        return None
    def can_toggle_flag(self):
        if self.has_flag():
            return True
        old_color = self.color()
        self._flag = True
        new_color = self.color()
        self._flag = False
        if old_color == new_color:
            return False
        return True
    # Tile.__init__ only creates non-mine tiles. This method
    # can then be used to change some of those tiles into mines
    def change_into_mine(self):
        self._mine = True
    def set_flag(self):
        if self.has_flag():
            return
        if not self.can_toggle_flag():
            return
        self._flag = True
    def unset_flag(self):
        if not self.has_flag():
            return
        if not self.can_toggle_flag():
            return
        self._flag = False
    # called on left-click and also when the game is over
    # and all tiles (incl. mine positions) are revealed to the user.
    def reveal(self):
        if not self.has_flag():
            self._revealed = True
    # useful only for debugging: this text is printed to the console when
    # you try to print a tile object.
    def __repr__(self):
        return '<Tile revealed={} mine={} flag={}>' \
            .format(self.is_revealed(), self.has_mine(), self.has_flag())
