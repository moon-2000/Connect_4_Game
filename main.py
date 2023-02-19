import pygame as pg
import sys
import math
import numpy as np
import random

# initializa pygame modules
pg.init()

class Model:
    
    PLAYER = 0
    AI = 1
    EMPTY = 0
    PLAYER_PIECE = 1
    AI_PIECE = 2
    WINDOW_LENGTH = 4
    AI_level  = 1

    def __init__(self, row_count, column_count):
        self.COLUMN_COUNT = column_count
        self.ROW_COUNT = row_count
        
        self.board = np.zeros((self.ROW_COUNT,self.COLUMN_COUNT))
    
    def print_board(self):
        print(np.flip(self.board, 0))

    def drop_piece(self, board, row, col, piece):
        board[row][col] = piece
    
    def is_valid_location(self, col):
        return self.board[self.ROW_COUNT-1][col] == 0

    def get_next_open_row(self, col):
        for r in range(self.ROW_COUNT):
            if self.board[r][col] == 0:
                return r
    
    def winning_move(self, piece):
        # Check horizontal locations for win
        for c in range(self.COLUMN_COUNT-3):
            for r in range(self.ROW_COUNT):
                if self.board[r][c] == piece and self.board[r][c+1] == piece \
                    and self.board[r][c+2] == piece and self.board[r][c+3] == piece:
                    return True
        
        # Check vertical locations for win
        for c in range(self.COLUMN_COUNT):
            for r in range(self.ROW_COUNT-3):
                if self.board[r][c] == piece and self.board[r+1][c] == piece \
                    and self.board[r+2][c] == piece and self.board[r+3][c] == piece:
                    return True
        
        # Check positively sloped diaganols
        for c in range(self.COLUMN_COUNT-3):
            for r in range(self.ROW_COUNT-3):
                if self.board[r][c] == piece and self.board[r+1][c+1] == piece \
                    and self.board[r+2][c+2] == piece and self.board[r+3][c+3] == piece:
                    return True
        
        # Check negatively sloped diaganols
        for c in range(self.COLUMN_COUNT-3):
            for r in range(3, self.ROW_COUNT):
                if self.board[r][c] == piece and self.board[r-1][c+1] == piece \
                    and self.board[r-2][c+2] == piece and self.board[r-3][c+3] == piece:
                    return True
    
    def get_valid_locations(self):
        valid_locations = []
        for col in range(self.COLUMN_COUNT):
            if self.is_valid_location(col):
                valid_locations.append(col)
        return valid_locations
    
    def evaluate_window(self, window, piece):
        score = 0
        opp_piece = self.PLAYER_PIECE
        if piece == self.PLAYER_PIECE:
            opp_piece = self.AI_PIECE

        if window.count(piece) == 4:
            score += 100
        elif window.count(piece) == 3 and window.count(self.EMPTY) == 1:
            score += 5
        elif window.count(piece) == 2 and window.count(self.EMPTY) == 2:
            score += 2

        if window.count(opp_piece) == 3 and window.count(self.EMPTY) == 1:
            score -= 4

        return score
    
    def score_position(self, board_copy, piece):
        score = 0

        ## Score center column
        center_array = [int(i) for i in list(board_copy[:, self.COLUMN_COUNT//2])]
        center_count = center_array.count(piece)
        score += center_count * 3

        ## Score Horizontal
        for r in range(self.ROW_COUNT):
            row_array = [int(i) for i in list(board_copy[r,:])]
            for c in range(self.COLUMN_COUNT-3):
                window = row_array[c:c+self.WINDOW_LENGTH]
                score += self.evaluate_window(window, piece)

        ## Score Vertical
        for c in range(self.COLUMN_COUNT):
            col_array = [int(i) for i in list(board_copy[:,c])]
            for r in range(self.ROW_COUNT-3):
                window = col_array[r:r+self.WINDOW_LENGTH]
                score += self.evaluate_window(window, piece)

        ## Score posiive sloped diagonal
        for r in range(self.ROW_COUNT-3):
            for c in range(self.COLUMN_COUNT-3):
                window = [board_copy[r+i][c+i] for i in range(self.WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece)

        for r in range(self.ROW_COUNT-3):
            for c in range(self.COLUMN_COUNT-3):
                window = [board_copy[r+3-i][c+i] for i in range(self.WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece)

        return score
    
    def is_terminal_node(self):
        return self.winning_move(self.PLAYER_PIECE) or self.winning_move(self.AI_PIECE) or len(self.get_valid_locations()) == 0
    
    def minimax(self, board_copy, depth, alpha, beta, maximizingPlayer):
        valid_locations = self.get_valid_locations()
        is_terminal = self.is_terminal_node()
        if depth == 0 or is_terminal:
            if is_terminal:
                if self.winning_move(self.AI_PIECE):
                    return (None, 100000000000000)
                elif self.winning_move(self.PLAYER_PIECE):
                    return (None, -10000000000000)
                else: # Game is over, no more valid moves
                    return (None, 0)
            else: # Depth is zero
                return (None, self.score_position(board_copy, self.AI_PIECE))
        if maximizingPlayer:
            value = -math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(col)
                b_copy = board_copy.copy()
                self.drop_piece(b_copy, row, col, self.AI_PIECE)
                new_score = self.minimax(b_copy, depth-1, alpha, beta, False)[1]
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
                row = self.get_next_open_row(col)
                b_copy = board_copy.copy()
                self.drop_piece(b_copy, row, col, self.PLAYER_PIECE)
                new_score = self.minimax(b_copy, depth-1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return column, value
    
    def pick_best_move(self, piece):
        """
        this function helps AI player to choose a random column
        """
        valid_locations = self.get_valid_locations()
        best_score = -10000
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = self.get_next_open_row(col)
            temp_board = self.board.copy()
            self.drop_piece(temp_board, row, col, piece)
            score = self.score_position(temp_board, piece)
            if score > best_score:
                best_score = score
                best_col = col
        return best_col

    def AI_rnd_or_minimax(self):
        if self.AI_level == 1:
            col, minimax_score = self.minimax(self.board, 5, -math.inf, math.inf, True)
            print("minimax mode chosen")
        else: 
            col = self.pick_best_move(self.AI_PIECE)
            print("random_move mode chosen")
        return col
    
    def print_board(self):
        print(np.flip(self.board, 0))

class View:   
    GAME_NAME = 'Connect 4 Game'
    BLUE =  "#142d4c" 
    BLACK = "#9fd3c7"
    RED = "#a2a8d3"
    YELLOW = "#f95959"
    SQUARE_SIZE = 100
    CIRCLE_RADIUS = int(SQUARE_SIZE/2 - 5)
    myfont = pg.font.SysFont("monospace", 77)
    
    def __init__(self, column_count, row_count, board, ai_piece, player_piece):
        self.COLUMN_COUNT = column_count
        self.ROW_COUNT = row_count
        self.PLAYER_PIECE = player_piece
        self.AI_PIECE = ai_piece
        self.width = self.COLUMN_COUNT * self.SQUARE_SIZE
        self.height = (self.ROW_COUNT+1) * self.SQUARE_SIZE
        self.size = (self.width, self.height)
        self.screen = pg.display.set_mode(self.size)
        self.board = board
        
    def initiate_window(self):
        #drawing the screen background
        for c in range(self.COLUMN_COUNT):
            for r in range(self.ROW_COUNT):
                pg.draw.rect(self.screen, self.BLUE, (c*self.SQUARE_SIZE, r*self.SQUARE_SIZE+ self.SQUARE_SIZE, self.SQUARE_SIZE, self.SQUARE_SIZE))
                pg.draw.circle(self.screen, self.BLACK, (int(c*self.SQUARE_SIZE + self.SQUARE_SIZE/2), int(r*self.SQUARE_SIZE + self.SQUARE_SIZE + self.SQUARE_SIZE/2)), self.CIRCLE_RADIUS)
        # naming the game 
        pg.display.set_caption(self.GAME_NAME)
        pg.display.update()

    def draw_board(self):
        for c in range(self.COLUMN_COUNT):
            for r in range(self.ROW_COUNT):      
                if self.board[r][c] == self.PLAYER_PIECE:
                    pg.draw.circle(self.screen, self.RED, (int(c*self.SQUARE_SIZE+self.SQUARE_SIZE/2), \
                        self.height-int(r*self.SQUARE_SIZE+self.SQUARE_SIZE/2)), self.CIRCLE_RADIUS)
                elif self.board[r][c] == self.AI_PIECE: 
                    pg.draw.circle(self.screen, self.YELLOW, (int(c*self.SQUARE_SIZE+self.SQUARE_SIZE/2), \
                        self.height-int(r*self.SQUARE_SIZE+self.SQUARE_SIZE/2)), self.CIRCLE_RADIUS)
        pg.display.update()

    def announce_winner(self, player):
        player += 1
        if player == 1:
            label = self.myfont.render(f"Player {player} wins!!", 1, self.RED)
        else:
            label = self.myfont.render(f"Player {player} wins!!", 2, self.YELLOW)
        
        print(f"player {player} is the winner")
        return label

class Controller:
    def __init__(self):
        self.game_over = False
        self.game_mode = 'pvp'
        self.COLUMN_COUNT = 7
        self.ROW_COUNT = 6
        self.player = 0 # player 1 plays first is (the default)
        self.model = Model(self.ROW_COUNT, self.COLUMN_COUNT)
        self.view= View(self.COLUMN_COUNT, self.ROW_COUNT, \
            self.model.board, self.model.AI_PIECE, self.model.PLAYER_PIECE)
    
    def change_mode(self):
        if self.game_mode == 'ai':
            self.game_mode = 'pvp'
            print("game mode is changed into pvp")
        else:
            self.game_mode = 'ai'
            print("game mode is changed into ai")

    def restart(self):
        for i in range(self.ROW_COUNT):
            for j in range(self.COLUMN_COUNT):
                self.model.board[i][j] = 0

        game.view.initiate_window()
        print(self.model.board)
        game.view.draw_board()
        self.game_mode = 'pvp'
        self.game_over = False
    
    def ai_level_change(self):
        if self.model.AI_level == 0:
            self.model.AI_level = 1 # minimax
        else:
            self.model.AI_level = 0 # random
            
            
    def key_handler(self, event):
        try:
            if event.key == pg.K_r:
                self.restart()
            elif event.key == pg.K_c:
                self.change_mode()
            elif event.key == pg.K_l:  
                self.ai_level_change()
        except (KeyError, ValueError):
            print('Wrong Key!')

    def swap_player(self):
        self.player += 1
        self.player = self.player % 2 


if __name__ == "__main__":

    game = Controller()
    game.view.initiate_window()

    while not game.game_over:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            
            if event.type == pg.MOUSEMOTION:
                pg.draw.rect(game.view.screen, game.view.BLACK, (0,0, game.view.width, game.view.SQUARE_SIZE))
                posx = event.pos[0]
                if game.player == 0:
                    pg.draw.circle(game.view.screen, game.view.RED, (posx, int(game.view.SQUARE_SIZE/2)), game.view.CIRCLE_RADIUS)
                else: 
                    pg.draw.circle(game.view.screen, game.view.YELLOW, (posx, int(game.view.SQUARE_SIZE/2)), game.view.CIRCLE_RADIUS)
            pg.display.update()

            if event.type == pg.MOUSEBUTTONDOWN:
                pg.draw.rect(game.view.screen, game.view.BLACK, (0,0, game.view.width, game.view.SQUARE_SIZE))
                posx = event.pos[0]
                col = int(math.floor(posx/game.view.SQUARE_SIZE))
                if game.model.is_valid_location(col):
                    row = game.model.get_next_open_row(col)
                    piece = game.player + 1
        
                    game.model.drop_piece(game.model.board, row, col, piece)
                    if game.model.winning_move(piece):
                        label = game.view.announce_winner(game.player)
                        game.view.screen.blit(label, (40,10))
                        game.game_over = True

                    game.model.print_board()
                    game.view.draw_board()
                    
                game.swap_player()
            
            elif event.type == pg.KEYDOWN:
                game.key_handler(event)

        # # Ask for Player 2 Input
        if game.player == game.model.AI and not game.game_over and game.game_mode == "ai":				
            col = game.model.AI_rnd_or_minimax()

            if game.model.is_valid_location(col):
                #pygame.time.wait(500)
                row = game.model.get_next_open_row(col)
                game.model.drop_piece(game.model.board, row, col, game.model.AI_PIECE)

                if game.model.winning_move(game.model.AI_PIECE):
                    label = game.view.announce_winner(game.player)
                    game.view.screen.blit(label, (40,10))
                    game.game_over = True

                game.model.print_board()
                game.view.draw_board()
            game.swap_player()

            if event.type == pg.KEYDOWN:
                game.key_handler(event)
    pg.time.wait(3000)