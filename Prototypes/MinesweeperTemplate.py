"""
TODO: Prologue comment placeholder
    Due to grading criteria we probably need to split this into two files
    To avoid merge conflicts with existing branches, I'm waiting until
    later to do this -Kiara
"""

import pygame as pg
import pygame_textinput as textinput
import random


# Minesweeper prototype
class Minesweeper:
    def __init__(self, width, height, num_mines):
        """Take a width, height, and mine number to create a Minesweeper game."""
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.board = [[0 for _ in range(width)] for _ in range(height)]
        self.revealed = [[False for _ in range(width)] for _ in range(height)]
        self.flags = [[False for _ in range(width)] for _ in range(height)]
        self.game_over = False
        self.mines_placed = False  # Flag to track if mines have been placed

    def place_mines(self, safe_x=None, safe_y=None):
        """Place mines, ensuring the first square is safe."""
        mines = 0
        while mines < self.num_mines:
            # Random position, make sure valid placement
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            if self.board[y][x] != -1 and not (x == safe_x and y == safe_y):
                self.board[y][x] = -1
                mines += 1

    def calculate_square(self, x, y):
        """Calculate the number of adjacent mines for a given square."""
        if self.board[y][x] == -1: # Mines don't need calculation
            return
        adj = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                # If not out of bounds
                if 0 <= x + i < self.width and 0 <= y + j < self.height:
                    # If adjacent mine then ++
                    if self.board[y + j][x + i] == -1:
                        adj += 1
        self.board[y][x] = adj

    def calculate_squares(self):
        """Calculate the number of adjacent mines for all squares."""
        for y in range(self.height):
            for x in range(self.width):
                self.calculate_square(x, y)

    def reveal_square(self, x, y):
        """Reveal a square on the board. If 0 square, reveal adjacent squares."""
        if self.revealed[y][x] or self.flags[y][x] or self.game_over:
            return

        # Place mines after first click, ensuring the first square is safe
        if not self.mines_placed:
            self.place_mines(safe_x=x, safe_y=y)
            self.calculate_squares()
            self.mines_placed = True

        self.revealed[y][x] = True

        # Mine then lose
        if self.board[y][x] == -1:
            self.game_over = True
            return

        # If the square is empty (0), reveal adjacent squares
        if self.board[y][x] == 0:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if 0 <= x + i < self.width and 0 <= y + j < self.height:
                        self.reveal_square(x + i, y + j)

    def toggle_flag(self, x, y):
        """Toggle a flag on a square if flaggable."""
        if self.revealed[y][x] or self.game_over:
            return

        self.flags[y][x] = not self.flags[y][x]

    def is_game_over(self):
        """True if loss, false otherwise."""
        return self.game_over

    def is_game_won(self):
        """True if all non-mine squares are revealed, false otherwise."""
        return all(self.revealed[y][x] or self.board[y][x] == -1 for y in range(self.height) for x in range(self.width))

    def get_display_board(self):
        """Returns the current state of the board for display purposes."""
        display_board = [[] for _ in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                if self.revealed[y][x]:
                    display_board[y].append(self.board[y][x])
                elif self.flags[y][x]:
                    display_board[y].append("F")
                else:
                    display_board[y].append("?")
        return display_board


class Game:
    def __init__(self):
        """Initialize the game."""
        self.minesweeper = None
        self.quit = False
        pg.init()

    def start_game(self, width: int, height: int, num_mines: int):
        """Start a new minesweeper board with given width, height, and num_mines."""
        self.minesweeper = Minesweeper(width, height, num_mines)

    def exit_game(self):
        """Perform any game cleanup here (if needed), then quit()."""
        pg.quit()

    def play_minesweeper():
        """Static method to play Minesweeper."""
        game = Game()
        game.run()

    def run(self):
        """Main game loop. Title screen followed by game."""
        screen = pg.display.set_mode((400, 400))
        clock = pg.time.Clock()
        font = pg.font.SysFont(None, 24)

        # Init text boxes
        width_input = textinput.TextInputVisualizer(manager=textinput.TextInputManager(validator=lambda x: x.isdigit() or x == ''))
        height_input = textinput.TextInputVisualizer(manager=textinput.TextInputManager(validator=lambda x: x.isdigit() or x == ''))
        # Cap mines at 20 as per requirements
        mines_input = textinput.TextInputVisualizer(manager=textinput.TextInputManager(validator=lambda x: (x.isdigit() and int(x) <= 20) or x == ''))
        selection = 0

        # Title screen loop
        while not self.minesweeper and not self.quit:
            screen.fill((255, 255, 255))
            pg.display.set_caption("Minesweeper -- Title Screen")

            # Render text
            width_text = font.render("Width (10-30): ", True, (0, 0, 0))
            height_text = font.render("Height (10-30): ", True, (0, 0, 0))
            mines_text = font.render("Mines (10-20): ", True, (0, 0, 0))
            screen.blit(width_text, (100, 100))
            screen.blit(height_text, (100, 140))
            screen.blit(mines_text, (100, 180))

            events = pg.event.get()

            # Only update one text input at a time, but display all three
            if selection == 0:
                width_input.cursor_visible = True
                width_input.update(events)
            elif selection == 1:
                height_input.cursor_visible = True
                height_input.update(events)
            elif selection == 2:
                mines_input.cursor_visible = True
                mines_input.update(events)
            screen.blit(width_input.surface, (250, 100))
            screen.blit(height_input.surface, (250, 140))
            screen.blit(mines_input.surface, (250, 180))

            # Handle key presses
            for event in events:
                if event.type == pg.QUIT:
                    self.quit = True
                    break
                if event.type == pg.KEYDOWN and event.key == pg.K_TAB:
                    # Set all cursors invisible, cycle selection
                    width_input.cursor_visible = False
                    height_input.cursor_visible = False
                    mines_input.cursor_visible = False
                    selection = (selection + 1) % 3
                if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    # Start game if all fields filled and mines 10-20
                    if width_input.value and height_input.value and (mines_input.value and 10 <= int(mines_input.value) <= 20):
                        width = int(width_input.value)
                        height = int(height_input.value)
                        num_mines = int(mines_input.value)
                        self.start_game(width, height, num_mines)

            pg.display.update()
            clock.tick(60)

        while not self.quit:  # Main game loop
            pg.display.set_caption("Minesweeper -- Game")
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    # Safe exit
                    self.quit = True
                    break
                elif event.type == pg.MOUSEBUTTONDOWN and self.minesweeper: # Click
                    # Get grid position
                    x, y = event.pos
                    grid_x = x // (400 // self.minesweeper.width)
                    grid_y = y // (400 // self.minesweeper.height)
                    if event.button == 1: # Left click reveal
                        self.minesweeper.reveal_square(grid_x, grid_y)
                    elif event.button == 3: # Right click flag
                        self.minesweeper.toggle_flag(grid_x, grid_y)

            # Draw the grid
            # TODO: Make game window scalable?
            screen.fill((255, 255, 255))
            board = self.minesweeper.get_display_board()
            for y in range(self.minesweeper.height):
                for x in range(self.minesweeper.width):
                    value = board[y][x]
                    if value == -1:
                        color = (255, 0, 0)
                    elif value == 0:
                        color = (200, 200, 200)
                    else:
                        color = (100, 100, 100)
                    pg.draw.rect(screen, color, (x * (400 // self.minesweeper.width), y * (400 // self.minesweeper.height), 400 // self.minesweeper.width, 400 // self.minesweeper.height))
                    pg.draw.rect(screen, (100, 0, 0), (x * (400 // self.minesweeper.width), y * (400 // self.minesweeper.height), 400 // self.minesweeper.width, 400 // self.minesweeper.height), 1)
                    if self.minesweeper.revealed[y][x]: # Draw number if revealed
                        text = font.render(str(value), True, (0, 0, 0))
                        screen.blit(text, (x * (400 // self.minesweeper.width) + 10, y * (400 // self.minesweeper.height) + 10))
                    elif self.minesweeper.flags[y][x]: # Draw flag if flagged
                        text = font.render("F", True, (0, 0, 0))
                        screen.blit(text, (x * (400 // self.minesweeper.width) + 10, y * (400 // self.minesweeper.height) + 10))

            # Game end
            # TODO: Transparent end screens? Or at least display final board first
            if self.minesweeper.is_game_over(): # Loss
                screen.fill((255, 255, 255))
                text = font.render("Game Over", True, (0, 0, 0))
                screen.blit(text, (150, 200))
                pg.display.flip()
                pg.time.wait(2000)
                break
            elif self.minesweeper.is_game_won(): # Win
                screen.fill((255, 255, 255))
                text = font.render("You Win!", True, (0, 0, 0))
                screen.blit(text, (150, 200))
                pg.display.flip()
                pg.time.wait(2000)
                break

            pg.display.flip()
            clock.tick(60)
        self.exit_game()


Game.play_minesweeper()