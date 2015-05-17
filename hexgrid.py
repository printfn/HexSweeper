import random
import math
import time

from tile import Tile
from math import floor

class HexGrid:
    """
    This class represents a hexagonal grid of tiles, and has all methods
    required to support a game of Minesweeper, except for graphics support.
    Rendering is implemented separately in HexGridUIUtilities and in the other
    Tkinter-specific UI classes. This means that HexGrid is UI-agnostic and
    that other UI frameworks can be used without needing to modify this class.

    The hexagonal grid is stored in a 2-dimensional nested array.
    In the context of this class:
        - 'size' refers to the number of tiles in the topmost or bottommost row.
          All size and coordinate calculations are based on this number.
        - 'y' refers to the row of a specific tile, with
          y = 0 at the top and y = 2 * size - 2 at the bottom.
        - 'x' refers to the horizontal position of a tile. x = 0 always refers
          to the first tile in a given row. The highest x coordinate changes
          depending on the y coordinate, but it changes between size - 1 and
          2 * size - 2. Because x coordinates depend on y coordinates, the
          nested array used internally (called self.grid) stores coordinates
          y first and x second, i.e. self.grid[y][x]

    y coordinates in a hexagonal grid (size = 3):
       0 0 0
      1 1 1 1
     2 2 2 2 2
      3 3 3 3
       4 4 4

    x coordinates in a hexagonal grid (size = 3):
       0 1 2
      0 1 2 3
     0 1 2 3 4
      0 1 2 3
       0 1 2
    The 'bending' of the vertical lines is clearly visible in this diagram.

    Here we can also see that the centre tile is (size - 1, size - 1).
    This is used for the 'safe' tile in the difficulty selection window.

    This is how the number of cells in a row is calculated:
       0 0 0   count = size + 0 (size + y)
      1 1 1 1  count = size + 1 (size + y)
     2 2 2 2 2 count = size + 2 (size + y or size + (2 * size - 2) - y)
      3 3 3 3  count = size + 1 (size + (2 * size - 2) - y)
       4 4 4   count = size + 0 (size + (2 * size - 2) - y)

    In general: count = size + min(y, 2 * size - 2 - y)

    Finally, the total number of tiles in a
    hexagonal grid of size s is 3s^2 - 3s + 1.
    The highest possible mine count is 1 less than this.
    """
    def __init__(self, size, mine_count):
        if mine_count > HexGrid.highest_possible_mine_count_for_size(size):
            # as the mine count is controlled by a slider, this
            # exception should *never* be thrown.
            raise Exception(
                ('Invalid mine count! The chosen field size '
               + 'of {} has {} tiles, '
               + 'but you chose to generate {} mines. '
               + 'Note that at least one field must be left '
               + 'blank for the game to be winnable.')
                .format(size,
                    self.highest_possible_mine_count_for_size(size) + 1,
                    mine_count))

        # validation completed successfully, now initialise the HexGrid
        self.size = size
        self.grid = []
        self.start_time = time.time() # save number of seconds since epoch
        self.mine_count = mine_count
        for y in range(self.row_count()): # 0 to 2 * size - 2, explained above
            cell_count_in_current_row = self.cell_count_in_row(y)
            row = []
            for x in range(cell_count_in_current_row):
                # as explained in tile.py, all new tiles initially have no mines
                # mines are only generated on first click to avoid unfair deaths
                row.append(Tile(self, x, y))
            self.grid.append(row)

        self.mines_have_been_generated = False

    # the following few functions implement basic
    # calculations outlined at the top of this file
    def row_count(self):
        return 2 * self.size - 1

    def cell_count_in_row(self, y):
        return self.size + min(y, 2 * self.size - 2 - y)

    def highest_row_cell_count(self):
        return 2 * self.size - 1

    def highest_possible_mine_count_for_size(size):
        total_tile_count = 3 * size ** 2 - 3 * size + 1
        return total_tile_count - 1

    def all_valid_coords(self):
        """
        Return a list of (x, y) tuples that represent all valid coordinates
        """
        coords = []
        for y in range(self.row_count()):
            for x in range(self.cell_count_in_row(y)):
                coords.append((x, y))
        return coords

    def __getitem__(self, pos):
        """
        Implement Python's array subscripting operator [].
        This allows code to write hexgrid[x, y] instead of hexgrid.grid[y][x].
        """
        (x, y) = pos
        return self.grid[y][x]

    def __setitem__(self, pos, item):
        """
        Also required for array subscripting, but for lvalues being assigned to,
        i.e. hexgrid[x, y] = tile instead of hexgrid.grid[y][x] = tile.
        """
        (x, y) = pos
        self.grid[y][x] = item

    # Validation functions for grid coordinates
    # Required to validate mouse clicks to ensure the user
    # actually clicked on a tile
    def is_y_valid(self, x, y):
        return y >= 0 and y <= 2 * self.size - 2

    def is_x_valid(self, x, y):
        return x >= 0 and x < self.cell_count_in_row(y)

    def is_position_valid(self, x, y):
        return self.is_y_valid(x, y) and self.is_x_valid(x, y)

    def adjacent_positions(self, x, y):
        """
        Return a list (x, y) tuples of adjacent positions
        """
        possible_positions = [(x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y)]
        # these three cases are required for the 'bend' in
        # the x-coordinate lines on the hexagonal grid
        if y < self.size - 1: # fields above the center row
            possible_positions.append((x + 1, y + 1))
            possible_positions.append((x - 1, y - 1))
        elif y == self.size - 1: # fields on the center row
            possible_positions.append((x - 1, y + 1))
            possible_positions.append((x - 1, y - 1))
        else: # fields below the center row
            possible_positions.append((x + 1, y - 1))
            possible_positions.append((x - 1, y + 1))
        # the exact coordinate offsets can be verified by checking the graph
        # and the coordinates of adjacent tiles.

        # here, the asterisk is used as the tuple unpacking operator.
        # filtering possible_positions is required for any edge or corner tiles.
        # filter takes a lambda expression and returns a 'filter object', which
        # is essentially a lazy list.
        # calling the list conversion function on this lazy list forces the
        # list to be fully evaluated, which is required for many operations
        # including getting the length of a list.
        return list(
            filter(
                lambda pos: self.is_position_valid(*pos),
                possible_positions
            )
        )

    def adjacent_mine_count(self, x, y):
        return len(
            list(
                filter(
                    # lambda only returns true if
                    # there is a mine at position pos
                    lambda pos: self[pos].has_mine(),
                    self.adjacent_positions(x, y)
                ) # this means that the filter statement returns a lazy list
                  # that contains all adjacent tile coordinates with mines
            ) # this lazy list is then computed and converted
              # to an eager list before I can get its
              # length, as in the method HexGrid.adjacent_positions above
        ) # and finally its length is calculated
          # this length now describes the number
          # of adjacent mines of a given position


    def total_flag_count(self):
        # (A) Get all valid coordinates                         (A)
        # (B) For each coordinate pos:                          (B)
        # (C)   - Get the tile at pos                           (C)
        # (D)   - Is there a flag on this tile?                 (D)
        # (E)   - True = 1, False = 0                           (E)
        # (F) Sum of ones and zeroes is the number flags on map (F)

        return sum(
            #  ~^~
            #   F
            #
            [int(self[pos].has_flag()) for pos in self.all_valid_coords()]
        ) #   ^  ~~~~^~~~~ ~~~~^~~~~~  ~^~        ^~~~~~~~~~~~~~~~~~~~~~~
          #   E      C         D        B         A

    def flag_limit_reached(self):
        return self.total_flag_count() >= self.mine_count

    def restart_game(self, size = None, mine_count = None):
        # size and mine_count are optional parameters
        # here they are initialized to previous values if
        # no explicit parameters were used
        if not size:
            size = self.size
        if not mine_count:
            mine_count = self.mine_count
        # reinitialize the object in place by explicitly calling __init__
        self.__init__(size, mine_count)

    def restart_if_game_is_over(self, redraw, show_alert):
        #     checking for game over:
        # (A)   - mines have not yet been generated    -> return  (A)
        # (B)   - all flags have been placed correctly -> win     (B)
        # (C)   - all non-mine tiles are revealed      -> win     (C)
        # (D)   - a mine is revealed                   -> lose    (D)
        # (E)   - otherwise                            -> return  (E)

        # A
        if not self.mines_have_been_generated:
            redraw()
            return

        game_won = False

        # B
        # list of booleans showing flag positions
        flag_list = [self[pos].has_flag() for pos in self.all_valid_coords()]
        # list of booleans showing mine positions
        mine_list = [self[pos].has_mine() for pos in self.all_valid_coords()]
        if mine_list == flag_list: # compare the two lists element by element
            # game over and player won as all
            # flags have been placed correctly
            game_won = True

        # C
        number_of_safe_hidden_tiles = len(
            [pos for pos in self.all_valid_coords()
                if not self[pos].has_mine()
                and not self[pos].is_revealed()])
        if number_of_safe_hidden_tiles == 0:
            # no safe but hidden tiles -> win (C)
            game_won = True

        # handle B and C
        if game_won:
            for pos in self.all_valid_coords():
                if not self[pos].has_flag():
                    self[pos].reveal()
            redraw()
            end_time = time.time()
            m, s = divmod(end_time - self.start_time, 60)
            duration = ""
            if m == 0:
                if s == 1:
                    duration = "1 second"
                else:
                    duration = "%01d seconds" % s
            elif m == 1:
                if s == 1:
                    duration = "1 minute and 1 second"
                else:
                    duration = "1 minute and %01d seconds" % s
            else:
                if s == 1:
                    duration = "%01d minutes and 1 second" % m
                else:
                    duration = "%01d minutes and %01d seconds" % (m, s)
            show_alert(
                "Minesweeper",
                "Congratulations!\nYou won the game in {}." \
                    .format(duration))
            self.restart_game()
            redraw()
            return

        # D
        # check for game loss
        # backslash tells python to continue
        # this statement onto the next line
        revealed_mine_positions = \
            [pos for pos in self.all_valid_coords() # check all valid positions
                 if self[pos].has_mine()            # if there is a mine
                 and self[pos].is_revealed()]       # and there it's
                                                    # been clicked on
        # if any mine has been revealed, handle game loss
        if len(revealed_mine_positions) > 0:
            for pos in self.all_valid_coords():
                if not self[pos].has_flag():
                    self[pos].reveal()
            redraw()
            show_alert("Minesweeper", "Game over.\nTry again!")
            self.restart_game()
            redraw()
            return

        # E
        # game continues
        redraw()

    def try_generate_mines(self, x, y):
        """
        Handle mine generation when user first clicks on a tile.
        The x and y coordinates passed to this function represent.
        The location the user clicked on. This position will never contain a
        mine as that would be an unfair game loss.
        """

        if self.mines_have_been_generated:
            return

        possible_mine_locations = self.all_valid_coords()
        possible_mine_locations.remove((x, y)) # don't place a mine where
                                               # the user clicked
        # randomly place self.mine_count mines
        # random_sample prevents multiple mines from being generated
        # on the same tile
        mine_positions = random.sample(possible_mine_locations, self.mine_count)
        for pos in mine_positions:
            self[pos].change_into_mine() # turn all selected tiles into mines
                                         # see tile.py for more info on this

        self.mines_have_been_generated = True

    def primary_click(self, screen_x, screen_y, apothem, redraw, show_alert):
        (x, y) = self.screen_coordinates_to_game_position(
            screen_x,
            screen_y,
            apothem)
        if not self.is_position_valid(x, y): # error handling
            return
        if self[x, y].has_flag():
            # flags prevent accidental clicks, so don't
            # reveal anything if you click on a flag
            return

        # does nothing (nop) if mines have already been generated
        self.try_generate_mines(x, y)

        # reveal the tile the user clicked on
        # (it has already been check for validity)
        self[x, y].reveal()

        if self.adjacent_mine_count(x, y) > 0:
            # don't show any more tiles, just redraw,
            # check for game over and exit
            redraw()
            self.restart_if_game_is_over(redraw, show_alert)
            return

        # now search for all possible adjacent tiles to reveal as well
        # queue-based iterative (non-recursive) implementation of flood fill
        queue = [(x, y)]
        complete = []
        while len(queue) > 0:
            if queue[0] in complete:
                del queue[0]
                continue
            # destructuring tuple assignment
            (current_x, current_y) = queue[0]
            # append tuple of current position ((double brackets required))
            complete.append((current_x, current_y))
            self[current_x, current_y].reveal()
            del queue[0]
            adjacent_tiles = self.adjacent_positions(current_x, current_y)
            # reveal tiles with adjacent mines, but don't search
            # any further (if they have adjacent mines) (or unless they
            # don't have adjacent mines)
            for adj_tile in adjacent_tiles:
                self[adj_tile].reveal()
                if self.adjacent_mine_count(*adj_tile) == 0:
                    queue.append(adj_tile)

        # finally check for game over, passing
        # the two function objects as this code
        # has no access to UI objects
        self.restart_if_game_is_over(redraw, show_alert)

    def secondary_click(self, screen_x, screen_y, apothem, redraw, show_alert):
        # toggle flag on right click
        (x, y) = self.screen_coordinates_to_game_position(
            screen_x,
            screen_y,
            apothem)

        if not self.is_position_valid(x, y): # error handling
            return

        if not self[x, y].can_toggle_flag():
            return

        if not self[x, y].has_flag(): # place a flag
            if self.flag_limit_reached():
                show_alert(
                    "Minesweeper",
                    "You've reached the flag limit of {}.\n"
                        # mine count is always equal to flag limit
                        .format(self.mine_count)
                  + "This means that at least one of your "
                  + "flags is incorrectly placed.\n"
                  + "Removing any incorrect flags will "
                  + "allow you to win the game.")
                return
            self[x, y].set_flag()
        else:
            self[x, y].unset_flag()

        self.restart_if_game_is_over(redraw, show_alert)

    def game_position_to_screen_coordinates(self, x, y, apothem):
        # apothem is the distance from center to the
        # middle of an edge of a regular hexagon
        #
        #                ^
        #              /   \
        #           /         \
        #        /               \
        #     /                     \
        #  /                           \
        #  |                           |
        #  |                           |
        #  |<- apothem ->x<- apothem ->|
        #  |                           |
        #  |                           |
        #  \                           /
        #     \                     /
        #        \               /
        #           \         /
        #              \   /
        #                v
        #
        row_count = self.cell_count_in_row(y)
        max_row_count = self.highest_row_cell_count()

        # add one apothem to x for every y step
        # away from the center (in either direction)
        # for first cell at x = 0 in addition to subsequent cells
        screen_x = apothem * (max_row_count - row_count)
        # move over to correct cell
        screen_x += 2 * apothem * x
        # add another apothem to move from left tile edge to tile center
        screen_x += apothem

        # distance_tile_center_to_vertex is also the hypothenuse
        #  .__ <- vertex of hexagon
        #  |  --__
        #  |      --__ distance_tile_center_to_vertex
        #  |          --__
        #  |              --__   ^ to other hex vertex
        #  +---------------------. < hex center
        #  ^      apothem
        # side
        # middle
        # of hex
        distance_tile_center_to_vertex = 2 * apothem / math.sqrt(3)
        vertical_tile_distance = 1.5 * distance_tile_center_to_vertex
        screen_y = y * vertical_tile_distance + distance_tile_center_to_vertex
        # approximate, could be 1 off
        # in either direction
        screen_y = int(screen_y)

        return (screen_x, screen_y)

    # This simply reverses the calculations in
    # HexGrid.game_position_to_screen_coordinates
    def screen_coordinates_to_game_position(self, screen_x, screen_y, apothem):
        distance_tile_center_to_vertex = 2 * apothem / math.sqrt(3)
        vertical_tile_distance = 1.5 * distance_tile_center_to_vertex # as above
        y = round(
            (screen_y - distance_tile_center_to_vertex) / vertical_tile_distance
        )

        row_count = self.cell_count_in_row(y)
        max_row_count = self.highest_row_cell_count()

        x = screen_x - apothem # move from tile center to left tile edge
        x -= apothem * (max_row_count - row_count)
        x = round(x / apothem / 2)
        return (x, y)

    # static function called by UI on initialisation and on window resize
    # returns the tuple (apothem, hshift)
    def apothem_and_hshift_for_size(width, height, border, size):
        # 2 * size - 1 is the number of horizontal
        # hexagon cells in the largest (center) row.
        # As apothem is half the horizontal width
        # of a hexagon, it needs to be multiplied
        # by 2 on the denominator.
        # Width - 2 * border is the real window width,
        # which is divided by the number of apothems.
        horizontal_apothem = (width - 2 * border) / (2 * (2 * size - 1))

        # there are also 2 * size - 1 rows in the hexgrid,
        # as seen at the top of this file
        num_rows = 2 * size - 1

        # Let d be half the distance from a hex center to its topmost vertex.
        # Vertically stacked hexagons (alternating left and right)
        # each contribute 3 * d to the total height.
        # One d must be added for the final hexagon's bottommost vertex.
        # Height - 2 * border is the real window height,
        # which is then divided by the number of ds.
        # Finally, this number is multiplied by 2
        # as the circumradius (distance from a hex center
        # to a vertex) is equal to 2 * d.
        dist_centre_to_vertex = ((height - 2 * border) / (3 * num_rows + 1)) * 2
        # Trigonometry can then be used to calculate the corresponding
        # apothem by multiplying the circumradius by sqrt(3) / 2
        vertical_apothem = dist_centre_to_vertex * math.sqrt(3) / 2
        # The final apothem is now the lower of
        # the horizontal and vertical apothems.
        # If the vertical apothem is the lower one,
        # the window is "flat" (i.e. wider than it is tall).
        # In this case, a horizontal shift is required
        # to ensure the hexagon remains centered.
        # This horizontal shift (hshift) is equal to
        #  width - border - half of the total board width
        # Horizontal tile width = 2 * apothem
        # This is multiplied by the total number of horizontal
        # cells divided by 2 to get half of the total board width.
        # The resulting hshift is then returned in
        # a tuple to be used by the UI code.
        apothem = min(horizontal_apothem, vertical_apothem)
        if vertical_apothem == apothem:
            return (
                apothem,
                # extra space on the horizonal
                floor((width - apothem * 2 * (2 * size - 1)) / 2 - border)
            )
        return (apothem, 0)
