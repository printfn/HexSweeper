"""
This module contains the GameUI class, which represents the main
HexSweeper window and its various UI elements.
"""

from tkinter import Tk, Canvas, Menu, Event, Widget
from tkinter import messagebox
from typing import List, Any

from hexsweeper.hexgrid import HexGrid
from hexsweeper.choose_difficulty_ui import ChooseDifficultyUI
from hexsweeper.difficulty import Difficulty
from hexsweeper.hexgrid_ui_utilities import HexGridUIUtilities

class GameUI:
    """
    This class is in charge of the main Minesweeper window.
    It owns a HexGrid instance that manages game state,
    it initialises Tkinter and it forwards mouse
    events to the HexGrid instance.
    """
    def __init__(self, difficulty: Difficulty = Difficulty.EASY) -> None:
        self.window = Tk() # create application window
        self.window.title('HexSweeper')
        # default width & height
        self.window.geometry(f'{800}x{615}')
        self.canvas = Canvas(self.window, bg='white')
        # fill entire window with canvas
        # "fill='both'" allows the canvas to stretch
        # in both x and y direction
        self.canvas.pack(expand=1, fill='both')

        # initialized with irrelevant values before
        # it is properly initialised in the start_new_game
        # method, which calls .restart_game() with correct size
        # and mine count
        self.hex_grid = HexGrid(2, 1)

        # these instance variables are initialised properly in
        # HexGridUIUtilities.draw_field
        self.apothem: float = 0
        self.hshift: float = 0
        self.start_new_game(difficulty)

        self.ui_elements: List[Widget] = [self.canvas]

        self.canvas.bind('<Button-1>', self.on_click)
        # both <Button-2> and <Button-3> need to be bound for OS X and
        # Linux support (due to Tkinter compatibility issues)
        self.canvas.bind('<Button-2>', self.on_secondary_click)
        self.canvas.bind('<Button-3>', self.on_secondary_click)
        self.window.bind('<Configure>', self.on_window_resize)

        self.init_menubar()

        self.window.mainloop()

    def init_menubar(self) -> None:
        """
        Creates the menubar. Called once on startup. The rendering
        of the menubar is operating-system dependent (Windows
        renders it inside the app window, OS X renders it in
        the OS menubar).
        """
        menubar = Menu(self.window)

        game_menu = Menu(menubar, tearoff=0)
        game_menu.add_command(
            label='New (Easy)',
            command=lambda: self.start_new_game(Difficulty.EASY))
        game_menu.add_command(
            label='New (Intermediate)',
            command=lambda: self.start_new_game(
                Difficulty.INTERMEDIATE))
        game_menu.add_command(
            label='New (Advanced)',
            command=lambda: self.start_new_game(Difficulty.ADVANCED))
        game_menu.add_command(
            label='New (Custom)',
            command=lambda: self.start_new_game(Difficulty.CUSTOM))
        menubar.add_cascade(label='Game', menu=game_menu)

        # finally add the menubar to the root window
        self.window.config(menu=menubar)

        self.ui_elements += [menubar, game_menu]

    def start_new_game(self, difficulty: Difficulty) -> None:
        """ Start a new game with the selected difficulty """
        if difficulty == Difficulty.EASY:
            self.hex_grid.restart_game(5, 8)
            self.draw_field()
        elif difficulty == Difficulty.INTERMEDIATE:
            self.hex_grid.restart_game(10, 45)
            self.draw_field()
        elif difficulty == Difficulty.ADVANCED:
            self.hex_grid.restart_game(13, 80)
            self.draw_field()
        else: # custom difficulty
            # This call takes care of restarting the game
            # with selected board size and mine count,
            # and also redraws the Game UI after difficulty
            # has been set.
            ChooseDifficultyUI(self)

    @staticmethod
    def border() -> float:
        """ Return fixed border size (on all sides) """
        return 20

    def draw_field(self) -> None:
        """ Redraw the game on the Canvas element """
        HexGridUIUtilities.draw_field(self, self.border())

    @staticmethod
    def show_alert(title: str, msg: str) -> None:
        """ Show a standard alert with a title and a message """
        messagebox.showinfo(title, msg)

    def on_click(self, event: Any) -> None:
        """ Primary click event handler """
        self.hex_grid.primary_click(
            (event.x - self.border() - self.hshift,
             event.y - self.border()),
            self.apothem,
            self.draw_field,
            self.show_alert)

    def on_secondary_click(self, event: Any) -> None:
        """ Secondary click event handler """
        self.hex_grid.secondary_click(
            (event.x - self.border() - self.hshift,
             event.y - self.border()),
            self.apothem,
            self.draw_field,
            self.show_alert)

    def on_window_resize(self, _: Event) -> None:
        """ Handler for window resize. Redraws the board. """
        # recalculates apothem and hshift values automatically
        # for the new window size
        self.draw_field()
