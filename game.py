# Sorting algorithims and pygame practice
import pygame
import random
import time

from player import Player
from enums import Fruit, State
from board import Board
from renderer import Renderer


pygame.init()
pygame.display.set_caption('Moogoo Monkey')

screen_height = 480
screen_width = 720
surface = pygame.display.set_mode((screen_width, screen_height))

nameChoices = ["Ava Cadavra", "Misty Waters", "Daddy Bigbucks", "Giuseppi Mezzoalto", "Dusty Hogg", "Phoebe Twiddle", "Luthor L. Bigbucks", "Lottie Cash", "Detective Dan D. Mann", "Pritchard Locksley", "Futo Maki", "Ephram Earl", "Lily Gates", "Cannonball Coleman", "Sue Pirmova", "Lincoln Broadsheet", "Crawdad Clem", "Bayou Boo", "Maximillian Moore", "Bucki Brock", "Berkeley Clodd", "Gramma Hattie", "Pepper Pete", "Dr. Mauricio Keys", "Olde Salty", "Lloyd", "Harlan King", "Daschell Swank", "Kris Thristle"]
    

def wait(time):
    while time > 0:
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            pygame.quit()

        pygame.time.wait(1)
        time -= 1


def init():
    # init renderer
        renderer = Renderer(surface)

        # init players
        names = random.sample(nameChoices, 2)
        players = []
        players.append(Player("Alex", Fruit.COCONUT, is_human=True))
        players.append(Player(names[0], Fruit.WATERMELON))
        players.append(Player(names[1], Fruit.PINEAPPLE))
        
        board = Board(players)
        # init board

        return board, renderer


def poll_input(board):
    for ev in pygame.event.get():
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            board.mouse_click = True
        else:
            board.mouse_click = False

        if ev.type == pygame.QUIT:
            pygame.quit()

    mouse = pygame.mouse.get_pos()
    board.mouse_coords = {'x': mouse[0], 'y': mouse[1]}


def update_game(board):

    # PLAYER_TURN_POPUP => PRE_BET, BET
    if board.state == State.PLAYER_TURN_POPUP and board.wait_time == 0:
        if board.players[board.turn].is_human:
            if board.bet_boxes_full():
                board.state = State.CARD_SELECTION
            else:
                board.state = State.BET
        else: # npc
            if board.bet_boxes_full():
                board.state = State.PRE_CARD_SELECTION
            else:
                board.state = State.PRE_BET
            board.wait_time = 100

    # PRE_BET => BET
    elif board.state == State.PRE_BET and board.wait_time == 0:
        board.state = State.BET

    # BET
    elif board.state == State.BET:
        if board.handle_bet_selection():
            if board.three_bets():
                if board.players[board.turn].is_human:
                    board.state = State.CARD_SELECTION
                else:
                    board.state = State.PRE_CARD_SELECTION
                    board.wait_time = 100
            else:
                board.next_turn()
                board.state = State.PLAYER_TURN_POPUP
                board.wait_time = 150

    # # Bet => PRE_CARD_SELECTION 
    elif board.state == State.PRE_CARD_SELECTION and board.wait_time == 0:
        board.state = State.CARD_SELECTION

    # CARD_SELECTION 
    elif board.state == State.CARD_SELECTION:
        if board.handle_card_selection():

            if board.round_complete():
                if board.game_complete():
                    board.state = State.GAME_OVER_SCREEN
                    return

                board.reset()

            else:
                board.next_turn()
            
            board.state = State.PLAYER_TURN_POPUP
            board.wait_time = 150

    if board.wait_time > 0:
        board.wait_time -= 1


if __name__ == "__main__":
    board, renderer = init()

    while True:
        poll_input(board)
        update_game(board)
        renderer.render(board)


# TODO:
# Asset manager (in the renderer)
# Add wait time enums
# add end round state (wait after final card in round is placed)
# Fix your time step article https://gafferongames.com/post/fix_your_timestep/
# Decouple board.py into a gamestate.py
# - move state machine logic to gamestate

B3b00v#2354