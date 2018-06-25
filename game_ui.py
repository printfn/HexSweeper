from tkinter import *
# messagebox is a submodule, so it's not imported automatically
from tkinter import messagebox

from hexgrid import HexGrid
from hexgrid_ui_utilities import HexGridUIUtilities
from choose_difficulty_ui import ChooseDifficultyUI

class GameUI:
    """
    This class is in charge of the main Minesweeper window.
    It owns a HexGrid instance that manages game state,
    it initialises Tkinter and it forwards mouse
    events to the HexGrid instance.
    """
    def __init__(self, difficulty):
        self.window = Tk() # create application window
        self.window.title('HexSweeper')
        self.window.geometry('{}x{}'.format(800, 615)) # default width & height
        self.canvas = Canvas(self.window, bg = 'white')
        # fill entire window with canvas
        # fill = 'both' allows canvas to stretch in both x and y direction
        self.canvas.pack(expand = 1, fill = 'both')

        self.border = 20

        # initialized with irrelevant values before
        # it is properly initialised in the start_new_game
        # method, which calls .restart_game() with correct size
        # and mine count
        self.hex_grid = HexGrid(2, 1)
        self.start_new_game(difficulty)

        self.canvas.bind('<Button-1>', self.on_click)
        # both <Button-2> and <Button-3> need to be bound for OS X and
        # Linux support (due to Tkinter compatibility issues)
        self.canvas.bind('<Button-2>', self.on_secondary_click)
        self.canvas.bind('<Button-3>', self.on_secondary_click)
        self.window.bind('<Configure>', self.on_window_resize)

        self.init_menubar()

        self.window.mainloop()

    def init_menubar(self):
        """
        Creates the menubar. Called once on startup. The rendering
        of the menubar is operating-system dependent (Windows
        renders it inside the app window, OS X renders it in
        the OS menubar).
        """
        self.menubar = Menu(self.window)

        self.game_menu = Menu(self.menubar, tearoff = 0)
        self.game_menu.add_command(
            label = 'New (Easy)',
            command = lambda: self.start_new_game('easy'))
        self.game_menu.add_command(
            label = 'New (Intermediate)',
            command = lambda: self.start_new_game('intermediate'))
        self.game_menu.add_command(
            label = 'New (Advanced)',
            command = lambda: self.start_new_game('advanced'))
        self.game_menu.add_command(
            label = 'New (Custom)',
            command = lambda: self.start_new_game('custom'))
        self.menubar.add_cascade(label = 'Game', menu = self.game_menu)

        # finally add the menubar to the root window
        self.window.config(menu = self.menubar)

    def start_new_game(self, difficulty):
        if difficulty == 'easy':
            self.hex_grid.restart_game(5, 8)
            self.draw_field()
        elif difficulty == 'intermediate':
            self.hex_grid.restart_game(10, 45)
            self.draw_field()
        elif difficulty == 'advanced':
            self.hex_grid.restart_game(13, 80)
            self.draw_field()
        else: # custom difficulty
            # This call takes care of restarting the game
            # with selected board size and mine count,
            # and also redraws the Game UI after difficulty
            # has been set.
            ChooseDifficultyUI(self)

    def draw_field(self):
        HexGridUIUtilities.draw_field(self)

    def on_click(self, event):
        self.hex_grid.primary_click(
            event.x - self.border - self.hshift,
            event.y - self.border,
            self.apothem,
            self.draw_field,
            messagebox.showinfo)

    def on_secondary_click(self, event):
        self.hex_grid.secondary_click(
            event.x - self.border - self.hshift,
            event.y - self.border,
            self.apothem,
            self.draw_field,
            messagebox.showinfo)

    def on_window_resize(self, event):
        # recalculates apothem and hshift values automatically
        # for the new window size
        self.draw_field()
