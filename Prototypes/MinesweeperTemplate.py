import pygame as pg
import pygame_textinput as textinput
import random


## Minesweeper prototype
class Minesweeper:
    def __init__(self, width, height, num_mines):
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.board = [[0 for _ in range(width)] for _ in range(height)]
        self.revealed = [[False for _ in range(width)] for _ in range(height)]
        self.flags = [[False for _ in range(width)] for _ in range(height)]
        self.game_over = False
        self.placeMines() ## Need to move this to allow for safe first square
        self.calculateSquares()

    def placeMines(self): ## Need to account for first square safe
        mines = 0
        while mines < self.num_mines:
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            if self.board[y][x] != -1: ## and not first square
                self.board[y][x] = -1
                mines += 1
    
    def calculateSquare(self, x, y) :
        if (self.board[y][x] == -1) :
            return
        adj = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                ## If not out of bounds
                if 0 <= x + i < self.width and 0 <= y + j < self.height:
                    ## If adjacent mine then ++
                    if self.board[y + j][x + i] == -1:
                        adj += 1
        self.board[y][x] = adj

    def calculateSquares(self):
        for y in range(self.height):
            for x in range(self.width):
                self.calculateSquare(x, y)
    
    def revealSquare(self, x, y):
        if self.revealed[y][x] or self.flags[y][x] or self.game_over:
            return
        
        self.revealed[y][x] = True

        if self.board[y][x] == -1:
            self.game_over = True
            return
        
        if self.board[y][x] == 0:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if 0 <= x + i < self.width and 0 <= y + j < self.height:
                        self.revealSquare(x + i, y + j)

    def toggleFlag(self, x, y):
        if self.revealed[y][x] or self.game_over:
            return

        self.flags[y][x] = not self.flags[y][x]

    def isGameOver(self):
        return self.game_over

    def isGameWon(self):
        return all(self.revealed[y][x] or self.board[y][x] == -1 for y in range(self.height) for x in range(self.width))
    
    def getDisplayBoard(self):
        displayBoard = [[] for _ in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                if self.revealed[y][x]:
                    displayBoard[y].append(self.board[y][x])
                elif self.flags[y][x]:
                    displayBoard[y].append("F")
                else:
                    displayBoard[y].append("?")
        return displayBoard


class Game:
    def __init__(self):
        self.minesweeper = None
        self.quit = False
        pg.init()

    def startGame(self, width: int, height: int, num_mines: int):
        '''Start a new game with given width, height, and num_mines.'''
        self.minesweeper = Minesweeper(width, height, num_mines)
    
    def exitGame(self):
        '''Perform any game cleanup here, then quit().'''
        pg.quit()

    def run(self):
        screen = pg.display.set_mode((400, 400))
        clock = pg.time.Clock()
        font = pg.font.SysFont(None, 24)

        ## Text boxes
        width_input = textinput.TextInputVisualizer(manager=textinput.TextInputManager(validator=lambda x: x.isdigit() or x == ''))
        height_input = textinput.TextInputVisualizer(manager=textinput.TextInputManager(validator=lambda x: x.isdigit() or x == ''))
        mines_input = textinput.TextInputVisualizer(manager=textinput.TextInputManager(validator=lambda x: x.isdigit() or x == ''))
        selection = 0

        while not self.minesweeper and not self.quit: ## Title screen loop
            screen.fill((255, 255, 255))
            pg.display.set_caption("Minesweeper -- Title Screen")

            width_text = font.render("Width (10-30): ", True, (0, 0, 0))
            height_text = font.render("Height (10-30): ", True, (0, 0, 0))
            mines_text = font.render("Mines (1-99): ", True, (0, 0, 0))
            screen.blit(width_text, (100, 100))
            screen.blit(height_text, (100, 140))
            screen.blit(mines_text, (100, 180))

            events = pg.event.get()

            ## Only update one input at a time, but display all three
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

            ## Handle key presses
            for event in events:
                if event.type == pg.QUIT:
                    self.quit = True
                    break
                if event.type == pg.KEYDOWN and event.key == pg.K_TAB:
                    ## Set all cursors invisible, cycle selection
                    width_input.cursor_visible = False
                    height_input.cursor_visible = False
                    mines_input.cursor_visible = False
                    selection = (selection + 1) % 3
                if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    if (width_input.value and height_input.value and mines_input.value):
                        width = int(width_input.value)
                        height = int(height_input.value)
                        num_mines = int(mines_input.value)
                        self.startGame(width, height, num_mines)

            pg.display.update()
            clock.tick(60)

        while not self.quit: ## Main game loop
            pg.display.set_caption("Minesweeper -- Game")
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit = True
                    break
                elif event.type == pg.MOUSEBUTTONDOWN and self.minesweeper:
                    x, y = event.pos
                    grid_x = x // (400 // self.minesweeper.width)
                    grid_y = y // (400 // self.minesweeper.height)
                    if event.button == 1:
                        self.minesweeper.revealSquare(grid_x, grid_y)
                    elif event.button == 3:
                        self.minesweeper.toggleFlag(grid_x, grid_y)

            screen.fill((255, 255, 255))
            for y in range(self.minesweeper.height):
                for x in range(self.minesweeper.width):
                    value = self.minesweeper.getDisplayBoard()[y][x]
                    if value == -1:
                        color = (255, 0, 0)
                    elif value == 0:
                        color = (200, 200, 200)
                    else:
                        color = (100, 100, 100)
                    pg.draw.rect(screen, color, (x * (400 // self.minesweeper.width), y * (400 // self.minesweeper.height), 400 // self.minesweeper.width, 400 // self.minesweeper.height))
                    pg.draw.rect(screen, (100, 0, 0), (x * (400 // self.minesweeper.width), y * (400 // self.minesweeper.height), 400 // self.minesweeper.width, 400 // self.minesweeper.height), 1)
                    if self.minesweeper.revealed[y][x]:
                        text = font.render(str(value), True, (0, 0, 0))
                        screen.blit(text, (x * (400 // self.minesweeper.width) + 10, y * (400 // self.minesweeper.height) + 10))
                    elif self.minesweeper.flags[y][x]:
                        text = font.render("F", True, (0, 0, 0))
                        screen.blit(text, (x * (400 // self.minesweeper.width) + 10, y * (400 // self.minesweeper.height) + 10))
            
            if self.minesweeper.isGameOver():
                screen.fill((255, 255, 255))
                text = font.render("Game Over", True, (0, 0, 0))
                screen.blit(text, (150, 200))
                pg.display.flip()
                pg.time.wait(2000)
                break
            elif self.minesweeper.isGameWon():
                screen.fill((255, 255, 255))
                text = font.render("You Win!", True, (0, 0, 0))
                screen.blit(text, (150, 200))
                pg.display.flip()
                pg.time.wait(2000)
                break

            pg.display.flip()
            clock.tick(60)
        self.exitGame()


main = Game()
main.run()
