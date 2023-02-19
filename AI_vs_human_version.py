# importing the required packages
import pygame as pg
import sys
import math
import numpy as np
import random

# initializa pygame modules
pg.init()

# GAME CONSTANTS
GAME_NAME = 'Connect 4 Game'
ROW_COUNT = 6
COLUMN_COUNT = 7
PLAYER = 0
AI = 1
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2
AI_level = 1
WINDOW_LENGTH = 4
# --- width and height of board ---
SQUARE_SIZE = 100
width = COLUMN_COUNT * SQUARE_SIZE
height = (ROW_COUNT+1) * SQUARE_SIZE
size = (width, height)
CIRCLE_RADIUS = int(SQUARE_SIZE/2 - 5)
screen = pg.display.set_mode(size)
turn = random.randint(PLAYER, AI)
game_over = False
myfont = pg.font.SysFont("monospace", 75)

# --- colors -------
BLUE =  "#142d4c" 
BLACK = "#9fd3c7"
RED = "#a2a8d3"
YELLOW = "#f95959"

# -----INNER BOARD------------
def create_board():
    board = np.zeros((ROW_COUNT,COLUMN_COUNT))
    return board

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def print_board(board):
    print(np.flip(board, 0))

def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    # Check positively sloped diaganols
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    # Check negatively sloped diaganols
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score

def score_position(board, piece):
    score = 0

    ## Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    ## Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    ## Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    ## Score posiive sloped diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else: # Game is over, no more valid moves
                return (None, 0)
        else: # Depth is zero
            return (None, score_position(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else: # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

def pick_best_move(board, piece):
    """
    this function helps AI player to choose a random column
    """
    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col

    return best_col

def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):      
            if board[r][c] == PLAYER_PIECE:
                pg.draw.circle(screen, RED, (int(c*SQUARE_SIZE+SQUARE_SIZE/2), height-int(r*SQUARE_SIZE+SQUARE_SIZE/2)), CIRCLE_RADIUS)
            elif board[r][c] == AI_PIECE: 
                pg.draw.circle(screen, YELLOW, (int(c*SQUARE_SIZE+SQUARE_SIZE/2), height-int(r*SQUARE_SIZE+SQUARE_SIZE/2)), CIRCLE_RADIUS)
    pg.display.update()

def initiate_window():
        #adding a color to the screen background
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pg.draw.rect(screen, BLUE, (c*SQUARE_SIZE, r*SQUARE_SIZE+SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            pg.draw.circle(screen, BLACK, (int(c*SQUARE_SIZE+SQUARE_SIZE/2), int(r*SQUARE_SIZE+SQUARE_SIZE+SQUARE_SIZE/2)), CIRCLE_RADIUS)
    # naming the game 
    pg.display.set_caption(GAME_NAME)
    pg.display.update()

def restart(board):
    initiate_window()
    for i in range(ROW_COUNT):
        for j in range(COLUMN_COUNT):
            board[i][j] = 0
    global game_over 
    game_over = False
    global turn
    turn = random.randint(PLAYER, AI)
    pg.display.update()

def is_full(board):
    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT):
            return not (board[r][c] == 0)

def AI_rnd_or_minimax(AI_level, board):
    if AI_level == 1:
        col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)
        print("minimax mode chosen")
    else: 
        col = pick_best_move(board, AI_PIECE)
        print("random mode chosen")
    return col


board = create_board()
initiate_window()
draw_board(board) 

while not game_over:

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        if event.type == pg.MOUSEMOTION:
            pg.draw.rect(screen, BLACK, (0,0, width, SQUARE_SIZE))
            posx = event.pos[0]
            if turn == PLAYER:
                pg.draw.circle(screen, RED, (posx, int(SQUARE_SIZE/2)), CIRCLE_RADIUS)

        pg.display.update()

        if event.type == pg.MOUSEBUTTONDOWN:
            pg.draw.rect(screen, BLACK, (0,0, width, SQUARE_SIZE))
            #print(event.pos)
            
            # Ask for Player 1 Input
            if turn == PLAYER:
                posx = event.pos[0]
                col = int(math.floor(posx/SQUARE_SIZE))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_PIECE)

                    if winning_move(board, PLAYER_PIECE):
                        label = myfont.render("Player 1 wins!!", 1, RED)
                        screen.blit(label, (40,10))
                        game_over = True

                    turn += 1
                    turn = turn % 2
                    print_board(board)
                    draw_board(board)


    # # Ask for Player 2 Input
    if turn == AI and not game_over:				

        col = AI_rnd_or_minimax(AI_level, board)

        if is_valid_location(board, col):
            #pygame.time.wait(500)
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI_PIECE)

            if winning_move(board, AI_PIECE):
                label = myfont.render("Player 2 wins!!", 1, YELLOW)
                screen.blit(label, (40,10))
                game_over = True

            print_board(board)
            draw_board(board)

            turn += 1
            turn = turn % 2
        
        if (event.type == pg.KEYDOWN and event.key == pg.K_r):
            print("game over 1 ", game_over)
            restart(board)
        
        if game_over or is_full(board):
            print("game over 2 ", game_over)
            pg.time.wait(3000)
            restart(board)

