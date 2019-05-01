"""
This module contains only the HexGridUIUtilities class, which provides
static utility methods for the UI code.
"""

import math

class HexGridUIUtilities:
    """
    Static class that contains Tkinter-specific
    utilities for drawing hexagons and hexgrids.
    Used by both GameUI and ChooseDifficultyUI.
    """
    @staticmethod
    def draw_hexagon(ui_instance, screen_pos, game_pos, fill):
        """
        Draw a single coloured hexagon.
        ui_instance: any class that has the following members:
            - apothem: number
            - canvas: Tkinter Canvas
            - hshift: number (horizontal shift of the board)
            - hex_grid: HexGrid
        screen_pos: tuple of x and y coordinates that describe
             the center of the hexagon that will be drawn.
        fill: string describing the fill colour
              of the hexagon, e.g. 'lightblue'
        """
        (size_x, size_y) = screen_pos
        apot = ui_instance.apothem # distance from hex center to
                    # the middle of one of its sides.
        ui_instance.canvas.create_polygon(
            # lower left vertex
            -apot + size_x, apot / math.sqrt(3) + size_y,
            # upper left vertex
            -apot + size_x, -apot / math.sqrt(3) + size_y,
            # topmost vertex
            0 + size_x, -2 * apot / math.sqrt(3) + size_y,
            # upper right vertex
            apot + size_x, -apot / math.sqrt(3) + size_y,
            # lower right vertex
            apot + size_x, apot / math.sqrt(3) + size_y,
            # bottommost vertex
            0 + size_x, 2 * apot / math.sqrt(3) + size_y,
            # empty string means transparent outline
            fill=fill, outline='')

        # Draw outline separately to prevent antialiasing issues
        # when window width/height are not divisible by tile
        # size/apothem respectively.
        # All hexagons need left, top left and top right outlines
        ui_instance.canvas.create_line(
            # lower left vertex
            -apot + size_x, apot / math.sqrt(3) + size_y,
            # upper left vertex
            -apot + size_x, -apot / math.sqrt(3) + size_y)
        ui_instance.canvas.create_line(
            # upper left vertex
            -apot + size_x, -apot / math.sqrt(3) + size_y,
            # topmost vertex
            0 + size_x, -2 * apot / math.sqrt(3) + size_y)
        ui_instance.canvas.create_line(
            # topmost vertex
            0 + size_x, -2 * apot / math.sqrt(3) + size_y,
            # upper right vertex
            apot + size_x, -apot / math.sqrt(3) + size_y)

        (field_x, field_y) = game_pos

        grid_size = ui_instance.hex_grid.size
        row_count = ui_instance.hex_grid.row_count()
        row_cell_count = ui_instance.hex_grid.cell_count_in_row(
            field_y)

        # only hexagons on the far right (x == row_cell_count - 1)
        # need a right-hand-side outline
        if field_x == row_cell_count - 1:
            ui_instance.canvas.create_line(
                # upper right vertex
                apot + size_x, -apot / math.sqrt(3) + size_y,
                # lower right vertex
                apot + size_x, apot / math.sqrt(3) + size_y)

        # only hexagons on the bottom row (y == row_count - 1)
        # and hexagons on the far right, but on or below the center
        # row (x == row_cell_count - 1 and y >= grid_size - 1)
        # need a bottom-right outline
        if field_y == row_count - 1 \
            or (field_x == row_cell_count - 1 \
                and field_y >= grid_size - 1):
            ui_instance.canvas.create_line(
                # lower right vertex
                apot + size_x, apot / math.sqrt(3) + size_y,
                # bottommost vertex
                0 + size_x, 2 * apot / math.sqrt(3) + size_y)

        # only hexagons on the bottom row (y == row_count - 1)
        # and hexagons on the far left and on or below the center row
        # (x == 0 and y >= size - 1) need a bottom-left outline
        if field_y == row_count - 1 \
            or (field_x == 0 and field_y >= grid_size - 1):
            ui_instance.canvas.create_line(
                # bottommost vertex
                0 + size_x, 2 * apot / math.sqrt(3) + size_y,
                # lower left vertex
                -apot + size_x, apot / math.sqrt(3) + size_y)

        # This manual outline-handling code ensures no line is
        # drawn twice, which prevents OS-specific Tkinter antialiasing
        # and rounding bugs.

    @staticmethod
    def draw_field(ui_instance, border):
        """
        Draw a complete hexagonal grid.
        ui_instance: as for HexGridUIUtilities.draw_hexagon.
            This class has all members required for drawing a hexgrid,
            so no additional parameters are required
        """
        # start by clearing any previously drawn hexgrid, which would
        # otherwise contribute to a decrease in performance
        ui_instance.canvas.delete('all')

        # in case the window was resized, ui_instance.apothem and
        # ui_instance.hshift are invalidated each time the hexgrid is
        # drawn. This calculation is quite fast, so this is not a
        # performance issue.
        (ui_instance.apothem, ui_instance.hshift) = \
            HexGridUIUtilities.apothem_and_hshift_for_size(
                ui_instance.canvas.winfo_width(),
                ui_instance.canvas.winfo_height(),
                border,
                ui_instance.hex_grid.size)

        font = ('Arial', HexGridUIUtilities.font_size_for_apothem(
            ui_instance.apothem))

        # now draw every hexagonal tile individually
        for pos in ui_instance.hex_grid.all_valid_coords():
            # field x, field y (in the grid coordinate screen_ystem)
            (field_x, field_y) = pos
            # now converted to screen x, screen y
            # (in the screen coordinate screen_ystem)
            (screen_x, screen_y) = ui_instance.hex_grid \
                .game_position_to_screen_coordinates(
                    field_x,
                    field_y,
                    ui_instance.apothem)
            # correct for borders and centering in
            # the canvas as calculated above
            screen_x += border + ui_instance.hshift
            screen_y += border
            # the HexGrid class implements Python's array subscripting
            # operator for (x, y) tuples.
            tile = ui_instance.hex_grid[pos]
            # the nested brackets for screen_x and screen_y are
            # necessary to wrap them in a tuple,
            # empty colour string is transparent (outline)
            HexGridUIUtilities.draw_hexagon(
                ui_instance,
                (screen_x, screen_y),
                (field_x, field_y),
                tile.color())
            # tile.text() returns None if the tile
            # should not contain any text, which evaluates
            # to False in a boolean expression
            if tile.text():
                # fill is the text colour; the background
                # colour is transparent by default
                ui_instance.canvas.create_text(
                    screen_x, screen_y, text=tile.text(), font=font, fill="black")

    @staticmethod
    def apothem_and_hshift_for_size(width, height, border, size):
        """
        Static function called by UI on initialisation and on window
        resize. Returns the tuple (apothem, hshift).
        """

        # 2 * size - 1 is the number of horizontal
        # hexagon cells in the largest (center) row.
        # As apothem is half the horizontal width
        # of a hexagon, it needs to be multiplied
        # by 2 on the denominator.
        # Width - 2 * border is the real window width,
        # which is divided by the number of apothems.
        horizontal_apothem = \
            (width - 2 * border) / (2 * (2 * size - 1))

        # there are also 2 * size - 1 rows in the hexgrid,
        # as seen at the top of this file
        num_rows = 2 * size - 1

        # Let d be half the distance from a hex center to its topmost
        # vertex. Vertically stacked hexagons (alternating left and
        # right) each contribute 3 * d to the total height.
        # One d must be added for the final hexagon's bottommost
        # vertex. Height - 2 * border is the real window height,
        # which is then divided by the number of ds.
        # Finally, this number is multiplied by 2
        # as the circumradius (distance from a hex center
        # to a vertex) is equal to 2 * d.
        dist_centre_to_vertex = (height - 2 * border) \
            / (3 * num_rows + 1) * 2
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
                math.floor(
                    (width - apothem * 2 * (2 * size - 1))
                    / 2 - border)
            )
        return (apothem, 0)

    @staticmethod
    def font_size_for_apothem(apothem):
        """
        This method computes the most appropriate font size
        for the given apothem. The result is always an integer.
        """
        if apothem < 15:
            return math.floor(apothem * 1.1)

        if apothem > 50:
            return 30

        return math.floor(apothem * 0.7)
