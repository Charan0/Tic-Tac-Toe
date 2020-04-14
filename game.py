import pygame
import math
from collections import Counter
from copy import deepcopy
import numpy as np
from tkinter import *
from tkinter import messagebox
import tkinter.font as tk_font
import time

pygame.init()
pygame.mixer.music.load('Background.mp3')
USER, AI = None, None
transposition_table = {}
PLAYER_FIRST = None
size = 3
PIECES_TO_WIN = 3
BOARD = [[0 for _ in range(size)] for _ in range(size)]
SEARCH_KEY = 3


class TicTacToe:
    def __init__(self, master):
        # Variables used to handle the user inputs

        self.master = master
        self.player_first = BooleanVar(value=False)
        self.size = IntVar(value=3)
        self.pieces_to_win = IntVar(value=3)
        self.symbol_choice = StringVar()
        self.options = [
            'Minimax Search',
            'Alpha-Beta Pruning',
            'Depth-limited Minimax(Heuristic)',
            'Depth-limited Alpha-Beta(Heuristic)',
            'Experimental minimax variant'
        ]
        self.search_type = StringVar()
        self.search_type.set(self.options[3])

        # Font types
        self.title_font = tk_font.Font(family="Helvetica", size=35)
        self.customFont = tk_font.Font(family="Courier", size=15)
        self.custom_labelFont = tk_font.Font(family="Courier", size=15, weight='bold')

        # Title of the GUI Window
        self.title = Label(master, text='Tic-Tac-Toe Settings',
                           font=self.title_font, justify=CENTER, width=20).pack()
        # RadioButtonGroup For User Symbol Choice
        self.choice_label = Label(master, text='Choose your symbol:', font=self.custom_labelFont).pack()
        self.cross = Radiobutton(master, text='Choose X', variable=self.symbol_choice,
                                 value='X', command=self.selected, font=self.customFont).pack()
        self.circle = Radiobutton(master, text='Choose O', variable=self.symbol_choice,
                                  value='O', command=self.selected, font=self.customFont).pack()

        # GUI Widgets to handle who has the first move, board size and number of connecting pieces to win
        self.first_move = Checkbutton(master, text='Make first move', font=self.customFont,
                                      variable=self.player_first, command=self.initial_move).pack()
        self.box_size_label = Label(master, text='Size of the grid :', font=self.custom_labelFont).pack()
        self.box_size = Entry(master, textvariable=self.size).pack()
        self.pieces_label = Label(master, text='Number of pieces to win :', font=self.custom_labelFont).pack()
        self.pieces_length = Entry(master, textvariable=self.pieces_to_win).pack()
        self.pieces_label = Label(master, text='Choose search type', font=self.custom_labelFont).pack()
        self.search_select = OptionMenu(master, self.search_type, *self.options).pack()
        self.start = Button(master, text='Start', command=self.set_inputs,
                            bg='green', fg='white', font=self.custom_labelFont).pack()
        # End of GUI Widgets

    def selected(self):
        global USER, AI
        if self.symbol_choice.get() == 'X':
            USER = 'X'
            AI = 'O'
        else:
            USER = 'O'
            AI = 'X'

    def initial_move(self):
        global PLAYER_FIRST
        if self.player_first.get():
            PLAYER_FIRST = True
        else:
            PLAYER_FIRST = False

    def set_inputs(self):
        global size, PIECES_TO_WIN, BOARD, SEARCH_KEY
        size = self.size.get()
        PIECES_TO_WIN = self.pieces_to_win.get()
        BOARD = [[0 for _ in range(size)] for _ in range(size)]
        # print(self.search_type.get())
        if self.search_type.get() == self.options[0]:
            SEARCH_KEY = 0
        elif self.search_type.get() == self.options[1]:
            SEARCH_KEY = 1
        elif self.search_type.get() == self.options[2]:
            SEARCH_KEY = 2
        elif self.search_type.get() == self.options[3]:
            SEARCH_KEY = 3
        else:
            SEARCH_KEY = 4

        self.master.destroy()


root = Tk()


# root.geometry('600x600')
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()
        exit(1)


def text_objects(text, color):
    textSurface = poppins_font.render(text, True, color)
    return textSurface, textSurface.get_rect()


def message_to_screen(msg, color):
    textSurf, textRect = text_objects(msg, color)
    textRect.center = (512, 384)
    SCREEN.blit(textSurf, textRect)


root.protocol("WM_DELETE_WINDOW", on_closing)
inputs = TicTacToe(root)
root.mainloop()

WIDTH, HEIGHT = 600, 600
WHITE = (255, 255, 255)
BLUE = (70, 130, 130)
pygame.display.set_caption('Tic Tac Toe By Charan')

SCREEN = pygame.display.set_mode((1024, 768))

TILES = {}
# The dictionary 'box' has the index to (row, col) in it i.e, 1 = (0, 0) ; 2 = (1, 0) etc
GRID_SIZE = math.ceil(WIDTH / size)
CIRCLE = pygame.image.load('Circle-200.png')
CROSS = pygame.image.load('Cross-200.png')
HEART_AI = pygame.image.load('Heart-AI.png')
HEART_USER = pygame.image.load('Heart-USER.png')

if GRID_SIZE > 200 or GRID_SIZE < 200:
    CIRCLE = pygame.transform.scale(CIRCLE, (GRID_SIZE, GRID_SIZE))
    CROSS = pygame.transform.scale(CROSS, (GRID_SIZE, GRID_SIZE))

# running = True

game_over_font = pygame.font.SysFont('calibri', 100)
poppins_font = pygame.font.Font('Poppins.ttf', 32)


# BOARD FILES BEGIN

def to_tuple(state):
    new_state = [tuple(row) for row in state]
    return tuple(new_state)


def screen_to_board():
    box = {}
    count = 0
    for row in range(size):
        for col in range(size):
            box[count + 1] = (row, col)
            count += 1
    return box


box = screen_to_board()
occupied = [False for _ in range(len(box) + 1)]


def inv_state(state):
    inverse = [[state[j][i] for j in range(size)] for i in range(size)]
    return inverse


def get_count(state, value):
    count = 0
    for row in state:
        count += Counter(row)[value]
    return count


def player(state):
    crosses = get_count(state, 'X')
    noughts = get_count(state, 'O')
    if crosses > noughts:
        return 'O'
    elif noughts > crosses:
        return 'X'
    if PLAYER_FIRST and crosses == noughts:
        return USER
    return AI


def actions(state):
    locations = []
    for row in range(size):
        for col in range(size):
            if state[row][col] == 0:
                locations.append([row, col])
    return locations


def ordered_actions(state, max=False):
    locations = []
    for row in range(size):
        for col in range(size):
            if state[row][col] == 0:
                locations.append([row, col])
    if not max:
        locations = sorted(locations, key=lambda a: eval(result(state, a)))
    elif max:
        locations = sorted(locations, key=lambda a: eval(result(state, a)), reverse=True)
    return locations


def get_middle(state, value):
    return state[len(state) // 2][len(state) // 2] == value


def result(state, action):
    row, col = action
    new_state = deepcopy(state)
    new_state[row][col] = player(state)
    return new_state


def get_diagonals(state):
    if len(state) == 3:
        return [(state[0][0], state[1][1], state[2][2]),
                (state[0][2], state[1][1], state[2][0])]

    matrix = np.array(state)
    flipped_matrix = np.fliplr(matrix)
    diagonals = []
    key = len(state) - PIECES_TO_WIN
    for k in range(-key, key + 1):
        diagonals.append(tuple(np.diag(matrix, k).tolist()))
        diagonals.append(tuple(np.diag(flipped_matrix, k).tolist()))
    return diagonals


def all_adjacent(row, val, count=PIECES_TO_WIN):
    for index in range(len(row)):
        if Counter(row[index:index + count])[val] >= count:
            return True
    return False


def won(state):
    if len(state) == 3:
        inverse = inv_state(state)
        diagonals = [[state[i][i] for i in range(size)], [state[size - 1 - i][i] for i in range(size - 1, -1, -1)]]

        if Counter(diagonals[0])['X'] == PIECES_TO_WIN or Counter(diagonals[1])['X'] == PIECES_TO_WIN:
            return 'X'
        elif Counter(diagonals[0])['O'] == PIECES_TO_WIN or Counter(diagonals[1])['O'] == PIECES_TO_WIN:
            return 'O'
        for row, col in zip(state, inverse):
            count_row = Counter(row)
            count_col = Counter(col)
            if count_row['X'] == PIECES_TO_WIN or count_col['X'] == PIECES_TO_WIN:
                return 'X'
            elif count_row['O'] == PIECES_TO_WIN or count_col['O'] == PIECES_TO_WIN:
                return 'O'

        if not get_count(state, 0):
            return 'Draw'

        return 'IN PROGRESS'
    elif len(state) > 3:
        inverse = inv_state(state)
        diagonals = get_diagonals(state)
        for diagonal in diagonals:
            if all_adjacent(diagonal, 'X'):
                return 'X'
            elif all_adjacent(diagonal, 'O'):
                return 'O'
        for row, col in zip(state, inverse):
            if all_adjacent(row, 'X') or all_adjacent(col, 'X'):
                return 'X'
            elif all_adjacent(row, 'O') or all_adjacent(col, 'O'):
                return 'O'
        if not get_count(state, 0):
            return 'Draw'

        return 'IN PROGRESS'


def terminal_test(state):
    if not actions(state):
        return True
    if won(state) != 'IN PROGRESS':
        return True
    return False


def utility(state):
    if won(state) == AI:
        return 10
    elif won(state) == USER:
        return -10
    return 0


def display_board():
    for row in BOARD:
        print(row)


def eval(state):
    if len(state) == 3:
        fitness = 0
        inverse = inv_state(state)
        for row, col in zip(state, inverse):
            if Counter(row)[AI] == 1 or Counter(col)[AI] == 1:
                fitness += 0.75
                break
            elif Counter(row)[USER] == 1 or Counter(col)[USER] == 1:
                fitness += -0.75
                break
        diagonals = get_diagonals(state)

        # print(diagonals[0], diagonals[1])
        if Counter(diagonals[0])[USER] >= 2 or Counter(diagonals[1])[USER] >= 2:
            fitness += -2.0
        elif Counter(diagonals[0])[AI] >= 2 or Counter(diagonals[1])[AI] >= 2:
            fitness += 2.0

        if get_middle(state, 0):
            fitness -= 0.75
        elif get_middle(state, USER):
            fitness += -2.5
        elif get_middle(state, AI):
            fitness += 2.5
        return fitness
    else:
        fitness = 0
        inverse = inv_state(state)
        diagonals = get_diagonals(state)

        if get_middle(state, AI):
            fitness += 0.85
        elif get_middle(state, USER):
            fitness += -0.85
        elif get_middle(state, 0):
            fitness += 0.5

        for row, col in zip(state, inverse):
            if all_adjacent(row, USER, PIECES_TO_WIN // 2 + 1) or all_adjacent(col, USER, PIECES_TO_WIN // 2 + 1):
                fitness += -4.0
            elif all_adjacent(row, AI, PIECES_TO_WIN // 2 + 1) or all_adjacent(col, AI, PIECES_TO_WIN // 2 + 1):
                fitness += 4.0
            if Counter(row)[USER] > Counter(row)[AI] or Counter(col)[USER] > Counter(col)[AI]:
                fitness += -2.0
            elif Counter(row)[AI] > Counter(row)[USER] or Counter(col)[AI] > Counter(col)[USER]:
                fitness += 2.0
        for diagonal in diagonals:
            if all_adjacent(diagonal, USER, PIECES_TO_WIN - 2):
                fitness += -4.5
            elif all_adjacent(diagonal, AI, PIECES_TO_WIN - 2):
                fitness += 4.5
            if Counter(diagonal)[USER] >= Counter(diagonal)[AI]:
                fitness += -2.5
            elif Counter(diagonal)[AI] >= Counter(diagonal)[USER]:
                fitness += 2.5
            if Counter(diagonal)['0'] > Counter(diagonal)[AI]:
                fitness += -1.5
            elif Counter(diagonal)['0'] < Counter(diagonal)[AI]:
                fitness += 1.5
        return fitness


class Move:
    def __init__(self, state, flag):
        self.state = state
        if 3 <= len(state) <= 7:
            self.depth_limit = len(state) // 2 + 1
        elif 8 <= len(state) <= 12:
            self.depth_limit = 2
        self.__search_by_heuristic = False
        if flag == 0:
            self.__search_by_heuristic = False
            self.next_move = self.minimax_decision(state)
        elif flag == 1:
            self.__search_by_heuristic = False
            self.next_move = self.alpha_beta_search(state)
        elif flag == 2:
            self.__search_by_heuristic = True
            self.next_move = self.heuristic_minimax(state)
        elif flag == 3:
            self.__search_by_heuristic = True
            self.next_move = self.heuristic_alpha_beta(state)
        elif flag == 4:
            self.__search_by_heuristic = True
            self.next_move = self.optimized_search(state)

    def max_value(self, state, alpha, beta, is_alpha_beta=False, depth=0):
        if terminal_test(state):
            return utility(state)

        if self.__cutoff_test(depth):
            return eval(state)

        v = -float('inf')
        for action in actions(state):
            v = max(v, self.min_value(result(state, action), alpha, beta, is_alpha_beta, depth + 1))
            if is_alpha_beta:
                if v >= beta:
                    return v
            alpha = max(alpha, v)
        return v

    def min_value(self, state, alpha, beta, is_alpha_beta=False, depth=0):
        if terminal_test(state):
            return utility(state)

        if self.__cutoff_test(depth):
            return eval(state)

        v = float('inf')
        for action in actions(state):
            v = min(v, self.max_value(result(state, action), alpha, beta, is_alpha_beta, depth + 1))
            if is_alpha_beta:
                if v <= alpha:
                    return v
            beta = min(beta, v)
        return v

    def minimax_decision(self, state):
        if won(state) == 'IN PROGRESS':
            return max(actions(state), key=lambda a: self.min_value(result(state, a), -np.inf, np.inf, False))

    def alpha_beta_search(self, state):
        best_score = -float('inf')
        beta = float('inf')
        best_action = None
        for a in actions(state):
            v = self.min_value(result(state, a), best_score, beta, True)
            if v > best_score:
                best_score = v
                best_action = a
        return best_action

    def __cutoff_test(self, depth):
        if depth >= self.depth_limit and self.__search_by_heuristic:
            return True
        return False

    def heuristic_minimax(self, state):
        best_score = -float('inf')
        beta = float('inf')
        best_action = None
        for a in actions(state):
            v = self.min_value(result(state, a), best_score, beta, False, 1)
            if v > best_score:
                best_score = v
                best_action = a
        return best_action

    def heuristic_alpha_beta(self, state):
        best_score = -float('inf')
        beta = float('inf')
        best_action = None
        for a in actions(state):
            v = self.min_value(result(state, a), best_score, beta, True, 1)
            if v > best_score:
                best_score = v
                best_action = a
        return best_action

    def optimized_search(self, state):
        """Search game to determine best action; use alpha-beta pruning.
        This version cuts off search and uses an evaluation function."""

        # Functions used by alpha_beta
        def max_value(state, alpha, beta, depth):
            if to_tuple(state) in transposition_table:
                return transposition_table[to_tuple(state)]

            if terminal_test(state):
                transposition_table[to_tuple(state)] = utility(state)
                return utility(state)

            if self.__cutoff_test(depth):
                transposition_table[to_tuple(state)] = eval(state)
                return eval(state)

            v = -float('inf')
            for a in actions(state):
                v = max(v, min_value(result(state, a), alpha, beta, depth + 1))
                if v >= beta:
                    transposition_table[to_tuple(state)] = v
                    return v
                alpha = max(alpha, v)
            transposition_table[to_tuple(state)] = v
            return v

        def min_value(state, alpha, beta, depth):
            if to_tuple(state) in transposition_table:
                return transposition_table[to_tuple(state)]

            if terminal_test(state):
                transposition_table[to_tuple(state)] = utility(state)
                return utility(state)

            if self.__cutoff_test(depth):
                transposition_table[to_tuple(state)] = eval(state)
                return eval(state)

            v = float('inf')
            for a in actions(state):
                v = min(v, max_value(result(state, a), alpha, beta, depth + 1))
                if v <= alpha:
                    transposition_table[to_tuple(state)] = v
                    return v
                beta = min(beta, v)
            transposition_table[to_tuple(state)] = v
            return v

        # Body of alpha_beta_cutoff_search starts here:
        # The default test cuts off at depth d or at a terminal state

        best_score = -float('inf')
        beta = float('inf')
        best_action = None
        for a in actions(state):
            v = max_value(result(state, a), best_score, beta, 0)
            if v > best_score:
                best_score = v
                best_action = a

        return best_action


# BOARD FILES END

def render_canvas(number_of_grids):
    gridsizeX, gridsizeY = math.ceil(WIDTH / number_of_grids), math.ceil(HEIGHT / number_of_grids)
    index = 0
    for col in range(128, HEIGHT + 84, gridsizeX):
        for row in range(212, WIDTH + 212, gridsizeY):
            TILES[index + 1] = pygame.draw.rect(SCREEN, WHITE, (row, col, gridsizeX, gridsizeY), 2)
            index += 1
    title = game_over_font.render('Tic Tac Toe', True, BLUE)
    SCREEN.blit(title, (310, 35))
    return


render_canvas(size)


def render(location):
    if player(BOARD) == 'X':
        SCREEN.blit(CROSS, location)
    else:
        SCREEN.blit(CIRCLE, location)


def get_collide_point(location):
    for index in range(len(TILES)):
        if TILES[index + 1].collidepoint(location):
            return index + 1


def is_valid(position):
    return not occupied[position]


def render_user_move(location):
    tile = get_collide_point(location=location)
    if is_valid(tile):
        row, col = box[tile]
        render(TILES[tile].topleft)
        BOARD[row][col] = player(BOARD)
        occupied[tile] = True
        return True
    elif not is_valid(tile):
        return False


def render_ai_move():
    global SEARCH_KEY
    move = Move(BOARD, SEARCH_KEY)
    # print(SEARCH_KEY)

    if move.next_move is None:
        return False

    row, col = move.next_move
    rev_box = {v: k for k, v in box.items()}
    tile = rev_box[(row, col)]
    # print('Row and Column = ', row, col, ' Tile = ', tile)
    # print(TILES)
    if is_valid(tile):
        render(TILES[tile].topleft)
        BOARD[row][col] = AI
        # print(rev_box[(row, col)])
        occupied[tile] = True
        return True


if not PLAYER_FIRST:
    render_ai_move()


def game_over():
    red = (151, 8, 5)
    if won(BOARD) == AI:
        return True, 'AI'
        # time.sleep(3)
        # SCREEN.fill(BLUE)
        # pygame.display.update()
        # SCREEN.blit(HEART_AI, (500, 250))
        # message_to_screen('AI WON THE GAME', red)
        # pygame.display.update()
    elif won(BOARD) == USER:
        return True, 'User'
        # time.sleep(3)
        # SCREEN.fill(BLUE)
        # pygame.display.update()
        # SCREEN.fill(BLUE)
        # SCREEN.blit(HEART_USER, (500, 250))
        # message_to_screen('Congrats, YOU WON', red)
        # pygame.display.update()
    elif won(BOARD) == 'Draw':
        return True, 'Draw'
        # time.sleep(3)
        # SCREEN.fill(BLUE)
        # pygame.display.update()
        # message_to_screen('Ended in a draw !', WHITE)
        # pygame.display.update()
    return False, 'IN Progress'


def game(location):
    if render_user_move(location) is False:
        # print('Illegal Move')
        exit(-5)
    else:
        render_user_move(location)
        render_ai_move()


def main():
    pygame.mixer.music.play(-1)
    statement = 'IN PROGRESS'
    running = True
    gameOver = False
    while running:

        while gameOver:
            SCREEN.fill(BLUE)
            if statement == 'AI':
                SCREEN.blit(HEART_AI, (500, 300))
                message_to_screen('Game Over, The AI WINS', (151, 8, 5))
            elif statement == 'User':
                SCREEN.blit(HEART_USER, (500, 300))
                message_to_screen('Game Over, Congrats you win', (151, 8, 5))
            elif statement == 'Draw':
                message_to_screen('Game Over, Ended in a Draw', (151, 8, 5))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    gameOver = False
                    exit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                exit()
            if event.type == pygame.MOUSEBUTTONUP:
                location = event.pos
                game(location)

        gameOver, statement = game_over()
        if gameOver:
            pygame.mixer.music.stop()
            pygame.display.update()
            time.sleep(3)
        pygame.display.update()


main()
