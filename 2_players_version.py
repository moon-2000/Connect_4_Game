# importing the required packages
import pygame as pg
import sys
import math
import numpy as np

# initializa pygame modules
pg.init()

# GAME CONSTANTS
GAME_NAME = 'Connect 4 Game'
# --- our screen size --- 
SQUARE_SIZE = 100
ROW_COUNT = 6
COLUMN_COUNT = 7
# --- width and height of board ---
width = COLUMN_COUNT * SQUARE_SIZE
height = (ROW_COUNT+1) * SQUARE_SIZE
size = (width, height)
CIRCLE_RADIUS = int(SQUARE_SIZE/2 - 5)
screen = pg.display.set_mode(size)

# --- colors -------
BLUE =  "#142d4c" 
BLACK = "#9fd3c7"
RED = "#a2a8d3"
YELLOW = "#f95959"





#-------SCREEN WINDOW---------
def initiate_window():
        #adding a color to the screen background
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pg.draw.rect(screen, BLUE, (c*SQUARE_SIZE, r*SQUARE_SIZE+SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            pg.draw.circle(screen, BLACK, (int(c*SQUARE_SIZE+SQUARE_SIZE/2), int(r*SQUARE_SIZE+SQUARE_SIZE+SQUARE_SIZE/2)), CIRCLE_RADIUS)
    # naming the game 
    pg.display.set_caption(GAME_NAME)
    pg.display.update()
    

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

def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):      
            if board[r][c] == 1:
                pg.draw.circle(screen, RED, (int(c*SQUARE_SIZE+SQUARE_SIZE/2), height-int(r*SQUARE_SIZE+SQUARE_SIZE/2)), CIRCLE_RADIUS)
            elif board[r][c] == 2: 
                pg.draw.circle(screen, YELLOW, (int(c*SQUARE_SIZE+SQUARE_SIZE/2), height-int(r*SQUARE_SIZE+SQUARE_SIZE/2)), CIRCLE_RADIUS)
    pg.display.update()

# is_full function checks whether the internal board is full or not 
def is_full(board):
    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT):
            return not (board[r][c] == 0)

game_over = False
turn = 0
def restart(board):
    initiate_window()
    for i in range(ROW_COUNT):
        for j in range(COLUMN_COUNT):
            board[i][j] = 0
    global game_over 
    game_over = False
    global turn
    turn = 0
    pg.display.update()
    
    
board = create_board()
myfont = pg.font.SysFont("monospace", 77)


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
            if turn == 0:
                pg.draw.circle(screen, RED, (posx, int(SQUARE_SIZE/2)), CIRCLE_RADIUS)
            else: 
                pg.draw.circle(screen, YELLOW, (posx, int(SQUARE_SIZE/2)), CIRCLE_RADIUS)
        pg.display.update()

        if event.type == pg.MOUSEBUTTONDOWN:
            pg.draw.rect(screen, BLACK, (0,0, width, SQUARE_SIZE))
            posx = event.pos[0]
            col = int(math.floor(posx/SQUARE_SIZE))

            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                if turn == 0:
                    drop_piece(board, row, col, 1)
                    if winning_move(board, 1):
                        label = myfont.render("Player 1 wins!!", 1, RED)
                        screen.blit(label, (40,10))
                        game_over = True 
                else:
                    drop_piece(board, row, col, 2)
                    if winning_move(board, 2):
                        label = myfont.render("Player 2 wins!!", 1, YELLOW)
                        screen.blit(label, (40,10))
                        game_over = True    
                print_board(board)
                draw_board(board)

            turn += 1
            turn = turn % 2
            
        if (event.type == pg.KEYDOWN and event.key == pg.K_r):
            restart(board)
            
        print(game_over)
        if game_over or is_full(board):
            pg.time.wait(3000)
            restart(board)
            
        