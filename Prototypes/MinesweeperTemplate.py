"""
TODO: Prologue comment placeholder
    Due to grading criteria we probably need to split this into two files
    To avoid merge conflicts with existing branches, I'm waiting until
    later to do this -Kiara
"""

import pygame as pg
import pygame_textinput as textinput
import random

# Window layout
WIN_SIZE = (440, 440)
GRID_PIXELS = 400

# Board layout (fixed 10x10)
BOARD_WIDTH = 10
BOARD_HEIGHT = 10
CELL = GRID_PIXELS // BOARD_WIDTH  # 40 px per cell

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRID_LINE = (120, 0, 0)
HIDDEN = (190, 190, 190)
REVEALED_EMPTY = (200, 200, 200)
REVEALED_NUMBER = (160, 160, 160)
MINE_RED = (255, 0, 0)
LABEL_GRAY = (90, 90, 90)


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
    def __init__(self, margin_left=40, margin_top=40):
        """Initialize the game."""
        self.minesweeper = None
        self.quit = False
        self.margin_left = margin_left
        self.margin_top = margin_top
        #Playable grid rectangle/square in window pixels (area AFTER the label margins)
        self.grid_x0 = self.margin_left #left edge of PLAYABLE board
        self.grid_y0 = self.margin_top #top edge of PLAYABLE board
        self.grid_x1 = self.grid_x0 + GRID_PIXELS #right edge of board
        self.grid_y1 = self.grid_y0 + GRID_PIXELS #bottom edge of board
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
        
    def mouse_to_grid(self, mx: int, my:int):
        """Convert mouse pixel coordinates (mx, my) to grid coordinates (gx, gy), or None if click outside of board"""
        if not (self.grid_x0 <= mx < self.grid_x1 and self.grid_y0 <= my < self.grid_y1):
            return None
        gx = (mx - self.grid_x0) // CELL
        gy = (my - self.grid_y0) // CELL
        return int(gx), int(gy)

    def run(self):
        """Main game loop. Title screen followed by game."""
        screen = pg.display.set_mode(WIN_SIZE)
        clock = pg.time.Clock()
        font = pg.font.SysFont(None, 24)

        # Cap mines at 20 as per requirements
        mines_input = textinput.TextInputVisualizer(manager=textinput.TextInputManager(validator=lambda x: (x.isdigit() and int(x) <= 20) or x == ''))

        # Title screen loop
        while not self.minesweeper and not self.quit:
            screen.fill(WHITE)
            pg.display.set_caption("Minesweeper -- Title Screen")

            # Render text
            mines_text = font.render("Mines (10-20): ", True, BLACK)
            screen.blit(mines_text, (100, 180))

            events = pg.event.get()

            # Updates mine and render mine-count input field
            mines_input.update(events)
            screen.blit(mines_input.surface, (250, 180))
            
            #Draw hint text
            hint_text = font.render("Press Enter to Start", True, (LABEL_GRAY))
            screen.blit(hint_text, (100,210))

            # Handle key presses
            for event in events:
                if event.type == pg.QUIT:
                    self.quit = True
                    break
                if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    # Start game if mine count provided and within 10-20 range
                    if (mines_input.value and 10 <= int(mines_input.value) <= 20):
                        num_mines = int(mines_input.value)
                        self.start_game(BOARD_WIDTH, BOARD_HEIGHT, num_mines)

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
                    hit = self.mouse_to_grid(*event.pos)
                    if hit is None:
                        continue  # clicked margin or outside grid
                    grid_x, grid_y = hit
                    if event.button == 1: # Left click reveal
                        self.minesweeper.reveal_square(grid_x, grid_y)
                    elif event.button == 3: # Right click flag
                        self.minesweeper.toggle_flag(grid_x, grid_y)

            # Draw the grid
            # TODO: Make game window scalable?
            screen.fill(WHITE)
            board = self.minesweeper.get_display_board()
            for y in range(self.minesweeper.height):
                for x in range(self.minesweeper.width):
                    value = board[y][x]
                    if self.minesweeper.revealed[y][x]:
                        if value == -1:
                            color = (MINE_RED)    
                        elif value == 0:
                            color = (REVEALED_EMPTY)    
                        else:
                            color = (REVEALED_NUMBER)   
                    else:
                        color = (HIDDEN)       

                    cell_rect = pg.Rect(self.grid_x0 + x * CELL, self.grid_y0 + y * CELL, CELL, CELL)
                    pg.draw.rect(screen, color, cell_rect)
                    pg.draw.rect(screen, GRID_LINE, cell_rect, 1)  # grid line

                    # draw text centered in the cell
                    if self.minesweeper.revealed[y][x]: # Draw number if revealed
                        txt = font.render(str(value if value >= 0 else 'X'), True, BLACK)
                        screen.blit(txt, txt.get_rect(center=cell_rect.center))
                    elif self.minesweeper.flags[y][x]: # Draw flag if flagged
                        txt = font.render("F", True, BLACK)
                        screen.blit(txt, txt.get_rect(center=cell_rect.center))

            # Column labels A–J (top)
            for col_index, letter in enumerate("ABCDEFGHIJ"):
                text_surface = font.render(letter, True, BLACK)
                text_rect = text_surface.get_rect(center=(
                    self.grid_x0 + col_index * CELL + CELL// 2,
                    self.grid_y0 // 2
                ))
                screen.blit(text_surface, text_rect)

            # Row labels 1–10 (left)
            for row_index in range(BOARD_HEIGHT):
                text_surface = font.render(str(row_index + 1), True, BLACK)
                text_rect = text_surface.get_rect(center=(
                    self.grid_x0 // 2,
                    self.grid_y0 + row_index * CELL + CELL // 2
                ))
                screen.blit(text_surface, text_rect)
                
            # Game end
            # TODO: Transparent end screens? Or at least display final board first
            if self.minesweeper.is_game_over(): # Loss
                screen.fill(WHITE)
                text = font.render("Game Over", True, BLACK)
                screen.blit(text, (150, 200))
                pg.display.flip()
                pg.time.wait(2000)
                break
            elif self.minesweeper.is_game_won(): # Win
                screen.fill(WHITE)
                text = font.render("You Win!", True, BLACK)
                screen.blit(text, (150, 200))
                pg.display.flip()
                pg.time.wait(2000)
                break

            pg.display.flip()
            clock.tick(60)
        self.exit_game()


Game.play_minesweeper()