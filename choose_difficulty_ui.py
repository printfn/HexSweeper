"""
This module implements the UI where the user can choose a custom difficulty.
It corresponds to the window accessible under Game -> New (Custom).
"""

from tkinter import *

from hexgrid import HexGrid
from hexgrid_ui_utilities import HexGridUIUtilities

class ChooseDifficultyUI:
    def __init__(self, game_ui):
        self.game_ui = game_ui
        # programs can only have one window, but can
        # create multiple "Toplevel"s (effectively new windows)
        self.window = Toplevel()
        self.window.title('HexSweeper - Choose Difficulty')
        self.window.geometry('400x473') # size maximises space in the window
        self.window.bind('<Configure>', lambda event: self.draw_field())
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)

        # these statements allow the hexgrid (in col 1, row 3)
        # to stretch as the window is resized

        # stretch the second column horizontally:
        Grid.columnconfigure(self.window, 1, weight=1)
        # stretch the fourth row vertically:
        Grid.rowconfigure(self.window, 3, weight=1)

        Label(self.window, text='Board Size:').grid(row=0, column=0, sticky=W)
        # TkInter "Scale" objects are sliders
        self.game_size_slider = Scale(
            self.window,
            # from_ because from is a Python keyword
            from_=2,
            to=15,
            orient=HORIZONTAL,
            command=lambda event: self.update_slider_range(event)
        ) # default slider resolution/accuracy is 1
        self.game_size_slider.grid(row=0, column=1, sticky=E + W)

        Label(self.window, text='Number of mines:') \
            .grid(row=1, column=0, sticky=W)
        self.mine_count_slider = Scale(
            self.window,
            from_=1,
            to=315,
            orient=HORIZONTAL,
            command=lambda event: self.draw_field()
        )
        self.mine_count_slider.grid(row=1, column=1, sticky=E + W)

        # set default slider values to values from the previous game
        # this makes it easier for the user to make small adjustments
        # without having to remember previous game values
        self.game_size_slider.set(self.game_ui.hex_grid.size)
        self.last_size = self.game_ui.hex_grid.size
        self.mine_count_slider.config(
            to=HexGrid.highest_possible_mine_count_for_size(
                self.game_ui.hex_grid.size
            )
        )
        self.mine_count_slider.set(self.game_ui.hex_grid.mine_count)

        Button(
            self.window,
            text='Select difficulty',
            command=self.select_difficulty_clicked
        ).grid(row=2, column=0, columnspan=2)

        self.canvas = Canvas(self.window, bg='white')
        self.canvas.grid(
            row=3,
            column=0,
            # span columns 0 and 1
            columnspan=2,
            # resize with the window
            sticky=E + N + W + S)

        self.border = 5
        self.draw_field()

        # put self.window in the foreground and
        # make self.game_ui.window (the root window) inaccessible
        self.window.transient(self.game_ui.window)
        self.window.grab_set()
        self.game_ui.window.wait_window(self.window)

    def update_slider_range(self, event):
        """
        When the board size slider is adjusted, the mine count slider
        is readjusted to maintain the same ratio of empty tiles
        to tiles with a mine. As this the ratio involved the total
        tile count instead of the board size, it looks like the slider
        value shifts along slightly (try it out to see this), but that
        is only due to the quadratic relationship between board size
        and tile count (specifically, tile count = 3s^2 - 3s + 1).
        The maximum value for the mine count slider is also adjusted
        based on HexGrid.highest_possible_mine_count_for_size().
        """
        new_size = self.game_size_slider.get()
        last_mine_count = self.mine_count_slider.get()
        if new_size == self.last_size:
            # unchanged, no need to make adjustments
            return

        # start by setting up some variables for later
        last_max_mine_count = \
            HexGrid.highest_possible_mine_count_for_size(self.last_size)
        new_max_mine_count = \
            HexGrid.highest_possible_mine_count_for_size(new_size)

        # update mine count slider upper bound
        self.mine_count_slider.config(to=new_max_mine_count)

        # Calculate new suggested mine count using proportion
        # of mines to total mine count (here max_mine_count, which
        # is basically equal to total tile count).
        # Slider.set() is used to update current slider value.
        new_suggested_mine_count = round(
            last_mine_count / last_max_mine_count * new_max_mine_count
        )
        self.mine_count_slider.set(new_suggested_mine_count)

        # set self.last_size so it can be used next time when
        # the slider is updated and this event handler is called
        self.last_size = self.game_size_slider.get()

        # the field preview also needs to be
        # redrawn after all these adjustments
        self.draw_field()

    def draw_field(self):
        size = self.game_size_slider.get()
        mine_count = self.mine_count_slider.get()
        # create a new, random HexGrid on every redraw
        # this only causes slight lag with huge field sizes,
        # so it is not a major issue
        self.hex_grid = HexGrid(size, mine_count)
        # As demonstrated in hexgrid.py (at the top),
        # (size - 1, size - 1) always refers to the centre tile.
        # Using the center tile as a guaranteed empty
        # tile looks nice and symmetrical.
        self.hex_grid.try_generate_mines(size - 1, size - 1)
        # hidden tiles (just like in an actual game) would
        # make the preview worthless, so all tiles (including
        # mines) need to be revealed
        for pos in self.hex_grid.all_valid_coords():
            self.hex_grid[pos].reveal()
        # finally draw the field, just like in the actual game (see game_ui.py)
        HexGridUIUtilities.draw_field(self)

    def select_difficulty_clicked(self):
        """
        Called when the user clicks on the "Select difficulty"
        button. Selected board size and mine count are saved
        in the game_ui.hex_grid object and the window on_close event
        handler is called, which takes care of closing the window,
        restoring focus to the actual game and redrawing the game.
        """
        size = self.game_size_slider.get()
        mine_count = self.mine_count_slider.get()
        self.game_ui.hex_grid.size = size
        self.game_ui.hex_grid.mine_count = mine_count
        self.on_window_close()

    def on_window_close(self):
        """
        Called when the user either closes the window using the
        red 'X' or when the user clicks on the "Select difficulty"
        button. Because we don't know how the user got to this
        method, we can't save the board size/mine count options
        (if required, they will have already been saved). So we
        just restart and redraw the main game and close the window.
        """
        self.game_ui.hex_grid.restart_game()
        self.game_ui.window.focus_set()
        self.game_ui.draw_field()
        self.window.destroy()
