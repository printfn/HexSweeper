import math

from hexgrid import HexGrid

class HexGridUIUtilities:
    """
    Static class that contains Tkinter-specific
    utilities for drawing hexagons and hexgrids.
    Used by both GameUI and ChooseDifficultyUI.
    """
    def draw_hexagon(ui, screen_pos, game_pos, fill):
        """
        Draw a single coloured hexagon.
        ui: any class that has the following members:
            - apothem: number
            - canvas: Tkinter Canvas
            - hshift: number (horizontal shift of the board)
            - border: number (invisible border on all sides of the board)
            - hex_grid: HexGrid
        screen_pos: tuple of x and y coordinates that describe
             the center of the hexagon that will be drawn.
        fill: string describing the fill colour
              of the hexagon, e.g. 'lightblue'
        """
        (sx, sy) = screen_pos
        a = ui.apothem # distance from hex center to
                    # the middle of one of its sides.
        ui.canvas.create_polygon(
            -a + sx, a / math.sqrt(3) + sy,     # lower left vertex
            -a + sx, -a / math.sqrt(3) + sy,    # upper left vertex
            0 + sx, -2 * a / math.sqrt(3) + sy, # topmost vertex
            a + sx, -a / math.sqrt(3) + sy,     # upper right vertex
            a + sx, a / math.sqrt(3) + sy,      # lower right vertex
            0 + sx, 2 * a / math.sqrt(3) + sy,  # bottommost vertex
            fill = fill, outline = '') # empty string == transparent outline

        # draw outline separately to prevent antialiasing issues
        # when window width/height are not divisible by tile size/apothem
        # all hexagons need left, top left and top right outlines
        ui.canvas.create_line(
            -a + sx, a / math.sqrt(3) + sy,  # lower left vertex
            -a + sx, -a / math.sqrt(3) + sy) # upper left vertex
        ui.canvas.create_line(
            -a + sx, -a / math.sqrt(3) + sy,    # upper left vertex
            0 + sx, -2 * a / math.sqrt(3) + sy) # topmost vertex
        ui.canvas.create_line(
            0 + sx, -2 * a / math.sqrt(3) + sy, # topmost vertex
            a + sx, -a / math.sqrt(3) + sy)     # upper right vertex

        (fx, fy) = game_pos
        # only hexagons on the far right (x == cell_count - 1)
        # need a right-hand-side outline
        if fx == ui.hex_grid.cell_count_in_row(fy) - 1:
            ui.canvas.create_line(
                a + sx, -a / math.sqrt(3) + sy, # upper right vertex
                a + sx, a / math.sqrt(3) + sy)  # lower right vertex

        # only hexagons on the bottom row (y == row_count - 1)
        # and hexagons on the far right, but on or below the center
        # row (x == cell_count - 1 and y >= size - 1)
        # need a bottom-right outline
        if fy == ui.hex_grid.row_count() - 1 \
            or (fx == ui.hex_grid.cell_count_in_row(fy) - 1 \
                and fy >= ui.hex_grid.size - 1):
            ui.canvas.create_line(
                a + sx, a / math.sqrt(3) + sy,     # lower right vertex
                0 + sx, 2 * a / math.sqrt(3) + sy) # bottommost vertex

        # only hexagons on the bottom row (y == row_count - 1)
        # and hexagons on the far left and on or below the center row
        # (x == 0 and y >= size - 1) need a bottom-left outline
        if fy == ui.hex_grid.row_count() - 1 \
            or (fx == 0 and fy >= ui.hex_grid.size - 1):
            ui.canvas.create_line(
                0 + sx, 2 * a / math.sqrt(3) + sy, # bottommost vertex
                -a + sx, a / math.sqrt(3) + sy)    # lower left vertex

        # this manual outline-handling code ensures no line is drawn twice,
        # prevents weird & OS-specific Tkinter antialiasing and rounding bugs

    def draw_field(ui):
        """
        Draw a complete hexagonal grid.
        ui: as for HexGridUIUtilities.draw_hexagon.
            This class has all members required for drawing a hexgrid,
            so no additional parameters are required
        """
        # start by clearing any previously drawn hexgrid, which would
        # otherwise contribute to a deccrease in performance
        ui.canvas.delete('all')

        # in case the window was resized, ui.apothem and ui.hshift
        # are invalidated each time the hexgrid is drawn.
        # this calculation is quite fast, so this is not a performance issue.
        (ui.apothem, ui.hshift) = HexGrid.apothem_and_hshift_for_size(
            ui.canvas.winfo_width(),
            ui.canvas.winfo_height(),
            ui.border,
            ui.hex_grid.size)

        # now draw every hexagonal tile individually
        for pos in ui.hex_grid.all_valid_coords():
            # field x, field y (in the grid coordinate system)
            (fx, fy) = pos
            # now converted to screen x, screen y
            # (in the screen coordinate system)
            (sx, sy) = ui.hex_grid.game_position_to_screen_coordinates(
                fx,
                fy,
                ui.apothem)
            # correct for borders and centering in
            # the canvas as calculated above
            sx += ui.border + ui.hshift
            sy += ui.border
            # the HexGrid class implements Python's array subscripting operator
            # for (x, y) tuples.
            tile = ui.hex_grid[pos]
            # the nested brackets for sx and sy are
            # necessary to wrap them in a tuple,
            # empty colour string is transparent (outline)
            HexGridUIUtilities.draw_hexagon(
                ui,
                (sx, sy),
                (fx, fy),
                tile.color())
            # tile.text() returns None if the tile should not contain any text,
            # which evaluates to False in a boolean expression
            if tile.text():
                # fill is the text colour; the background
                # colour is transparent by default
                ui.canvas.create_text(sx, sy, text=tile.text(), fill="black")
