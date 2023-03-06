import sys
import copy
import pygame
import numpy
import random

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
ROWS = 3
COLS = 3
SQUARE_SIZE = SCREEN_WIDTH // COLS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

AI_score = 0
human_score = 0

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tic Tac Toe')
background_surface = pygame.image.load('background.png')
background_rect = background_surface.get_rect()

class Board:
    
    def __init__(self):
        self.squares = numpy.zeros((ROWS, COLS))
        self.empty_squares = self.squares
        self.filled_squares = 0
        screen.blit(background_surface, background_rect)

    def mark_square(self, row, col, player):
        self.squares[row][col] = player
        self.filled_squares += 1

    def empty_square(self, row, col):
        return self.squares[row][col] == 0

    def get_empty_squares(self):
        self.empty_squares = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.empty_square(row, col):  # If that square is empty
                    self.empty_squares.append((row, col))

    def evaluate_win(self, draw_line):

        for col in range(COLS):
            if self.squares[0][col] == self.squares[1][col] == \
               self.squares[2][col] != 0:
                if draw_line == True:
                    pygame.draw.line(screen, RED, (col * 200 + 100, 50),
                                      (col * 200 + 100, 550), 5)
                return self.squares[0][col]

        for row in range(ROWS):
            if self.squares[row][0] == self.squares[row][1] == \
               self.squares[row][2] != 0:
                if draw_line == True:
                    pygame.draw.line(screen, RED, (50, row * 200 + 100),
                                     (550, row * 200 + 100), 5)
                return self.squares[row][0]
            
        if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] != 0:
            if draw_line == True:
                pygame.draw.line(screen, RED, (50,50), (550, 550), 5)            
            return self.squares[0][0]

        if self.squares[2][0] == self.squares[1][1] == self.squares[0][2] != 0:
            if draw_line == True:
                pygame.draw.line(screen, RED, (50, 550), (550, 50), 5)
            return self.squares[2][0]

        if self.filled_squares == 9:
            # all the squares filled up
            return 3 # 3 stands for Draw
        
        return 0  # Nobody won yet
    
class Game:

    def __init__(self):       
        self.board = Board()
        self.player = 1  # Human starts first
        self.over = False
        self.update_score(0, 1)
        self.update_score(0, 2)

    def draw_XO(self, row, col):
        if self.player == 1:  # Human is O
            pygame.draw.circle(screen, WHITE,
                               (col * 200 + 100,
                                row * 200 + 100),
                               50, 5)
        else:  # AI is X
            pygame.draw.line(screen, BLACK,
                             (col * 200 + 50,
                              row * 200 + 50),
                             (col * 200 + 150,
                              row * 200 + 150), 5)
            pygame.draw.line(screen, BLACK,
                             (col * 200 + 150,
                              row * 200 + 50),
                             (col * 200 + 50,
                              row * 200 + 150), 5)
    
    def update_score(self, score, winner):

        score_text = pygame.font.SysFont('comicsans', 30, True)
        winning_text = pygame.font.SysFont(None, 30, True)
        self.board.evaluate_win(True)

        if winner == 1:
            human_score_surface = score_text.render(f"Human: {human_score}", 1, BLACK)
            score_rect = human_score_surface.get_rect(center = (100,50))
            screen.blit(human_score_surface, score_rect)
            winning_surface = winning_text.render('You won. Hit "r" to restart.',1,RED)
            
        elif winner == 2:   
            AI_score_surface = score_text.render(f"AI: {AI_score}", 1, BLACK)
            score_rect = AI_score_surface.get_rect(center = (450,50))
            screen.blit(AI_score_surface, score_rect)
            winning_surface = winning_text.render('You lost. Hit "r" to restart.',1,RED)
        
        else:
            winning_surface = winning_text.render('It is a draw. Hit "r" to restart.',1,RED)
                                                  

        if score != 0:
            winning_rect = winning_surface.get_rect(center = (300,300))
            screen.blit(winning_surface, winning_rect)

    def make_move(self, row, col):
        # Update board status
        self.board.mark_square(row, col, self.player)
        
        # Get list of remaining empty squares
        self.board.get_empty_squares()

        # Draw on game board
        self.draw_XO(row, col)

        # Evaluate if anyone won
        result = self.board.evaluate_win(False)
        
        # switch player from 1 to 2, or vice versa
        if result == 0:  # Nobody won yet
            self.player = self.player % 2 + 1
        elif result == 1: # Human won
            global human_score
            human_score += 1
            self.update_score(human_score, 1)
            self.over = True
        elif result == 2: # AI won
            global AI_score
            AI_score += 1
            self.update_score(AI_score, 2)
            self.over = True
        else: # Draw
            self.update_score(-1, 0)
            self.over = True

    def select_square(self, board, maximising):

        case = board.evaluate_win(False)
        
        if case == 1:  # Human wins
            return 1, None
        elif case == 2:  # AI wins
            return -1, None
        elif case == 3:  # Draw
            print("Draw")
            return 0, None

        if maximising:
            maximize_value = -1
            selected_move = None
            board.get_empty_squares()
            
            for row, col in board.empty_squares:
                temp_board = copy.deepcopy(board)
                temp_board.mark_square(row, col, 1)
                value = self.select_square(temp_board, False)[0]

                if value > maximize_value:
                    maximize_value = value
                    selected_move = row, col

            return maximize_value, selected_move

        else:
            minimize_value = 1
            selected_move = None
            board.get_empty_squares()

            for row, col in board.empty_squares:
                temp_board = copy.deepcopy(board)
                temp_board.mark_square(row, col, self.player)
                value = self.select_square(temp_board, True)[0]

                if value < minimize_value:
                    minimize_value = value
                    selected_move = row, col

            return minimize_value, selected_move

def main():

    beep_sound = pygame.mixer.Sound('beep.wav')
  
    game = Game()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                clicked_position = event.pos
                selected_row = clicked_position[1] // SQUARE_SIZE
                selected_col = clicked_position[0] // SQUARE_SIZE

                # Check if the square that user clicked is empty
                if game.board.empty_square(selected_row, selected_col) == 0:
                    # Play a beep sound when player click on occupied square
                    beep_sound.play()
                else:
                    game.make_move(selected_row, selected_col)
                    if game.over:
                        pass
                    else:
                        # AI's turn. Strategy: choose a square randomly
                        # selected_square = random.choice(game.board.empty_squares)   

                        # Strategy: minimax
                        selected_square = game.select_square(game.board, False)[1]
                
                        game.make_move(selected_square[0], selected_square[1])
                        if game.over:
                            pass
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.__init__()

        pygame.display.update()

if __name__ == "__main__":
    main()
