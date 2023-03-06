# Sorting algorithims and pygame practice
import pygame
import random
import time

from constants import *
from player import Player
from enums import Fruit, State, Wait
from board import Board
from renderer import Renderer


pygame.init()
pygame.display.set_caption('Moogoo Monkey')

screen_height = 480
screen_width = 720
fps = 60
clock = pygame.time.Clock()
surface = pygame.display.set_mode((screen_width, screen_height))

nameChoices = ["Ava Cadavra", "Misty Waters", "Daddy Bigbucks", "Giuseppi Mezzoalto", "Dusty Hogg", "Phoebe Twiddle", "Luthor L. Bigbucks", "Lottie Cash", "Detective Dan D. Mann", "Pritchard Locksley", "Futo Maki", "Ephram Earl", "Lily Gates", "Cannonball Coleman", "Sue Pirmova", "Lincoln Broadsheet", "Crawdad Clem", "Bayou Boo", "Maximillian Moore", "Bucki Brock", "Berkeley Clodd", "Gramma Hattie", "Pepper Pete", "Dr. Mauricio Keys", "Olde Salty", "Lloyd", "Harlan King", "Daschell Swank", "Kris Thristle"]


def init():
    # init renderer
    renderer = Renderer(surface)

    # init players
    names = random.sample(nameChoices, 2)
    players = []
    players.append(Player("Alex", Fruit.COCONUT, is_human=True))
    players.append(Player(names[0], Fruit.WATERMELON))
    players.append(Player(names[1], Fruit.PINEAPPLE))
    
    # init board
    board = Board(players)

    return board, renderer


def poll_input(board):
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit()

        board.mouse_click = (ev.type == pygame.MOUSEBUTTONUP and ev.button == 1)

    mouse = pygame.mouse.get_pos()
    board.mouse_coords = {'x': mouse[0], 'y': mouse[1]}


def update_game(board):
    # assume that nothing is hovered by default
    board.pointer = False

    # TURN_POPUP => PRE_BET, BET
    if board.state == State.TURN_POPUP and board.wait_time == 0:
        if board.players[board.turn].is_human:
            if board.bet_boxes_full():
                board.state = State.CARD_SELECTION
            else:
                board.state = State.BET
        else: # npc
            if board.bet_boxes_full():
                board.state = State.PRE_CARD_SELECTION
                board.wait_time = Wait.PRE_CARD_SELECTION.value
            else:
                board.state = State.PRE_BET
                board.wait_time = Wait.PRE_BET.value

    # PRE_BET => BET
    elif board.state == State.PRE_BET and board.wait_time == 0:
        board.state = State.BET

    # BET => PRE_CARD_SELECTION, CARD_SELECTION, TURN_POPUP
    elif board.state == State.BET:
        if board.handle_bet_selection():
            if board.three_bets():
                if board.players[board.turn].is_human:
                    board.state = State.CARD_SELECTION
                else:
                    board.state = State.PRE_CARD_SELECTION
                    board.wait_time = Wait.TURN_POPUP.value
            else:
                board.next_turn()
                board.state = State.TURN_POPUP
                board.wait_time = Wait.TURN_POPUP.value

    # PRE_CARD_SELECTION => CARD_SELECTION 
    elif board.state == State.PRE_CARD_SELECTION and board.wait_time == 0:
        board.state = State.CARD_SELECTION

    # CARD_SELECTION => POST_CARD_SELECTION
    elif board.state == State.CARD_SELECTION:
        if board.handle_card_selection():
            board.state = State.POST_CARD_SELECTION
            board.wait_time = Wait.POST_CARD_SELECTION.value

    # POST_CARD_SELECTION => TURN_POPUP, ROUND_ENDED, GAME_OVER_SCREEN
    elif board.state == State.POST_CARD_SELECTION and board.wait_time == 0:
        if board.round_complete():
            board.state = State.ROUND_ENDED
            board.wait_time = Wait.ROUND_ENDED.value

        else:
            board.next_turn()
            board.state = State.TURN_POPUP
            board.wait_time = Wait.TURN_POPUP.value

    # ROUND_ENDED => TURN_POPUP, GAME_OVER_SCREEN
    elif board.state == State.ROUND_ENDED and board.wait_time == 0:
        board.reset()

        if board.game_complete():
            board.state = State.GAME_OVER_SCREEN
            return

        board.state = State.TURN_POPUP
        board.wait_time = Wait.TURN_POPUP.value


    # Test if settings button is clicked
    if SETTINGS_BUTTON_LEFT <= board.mouse_coords['x'] <= SETTINGS_BUTTON_LEFT + SETTINGS_BUTTON_WIDTH and SETTINGS_BUTTON_TOP <= board.mouse_coords['y'] <= SETTINGS_BUTTON_TOP + SETTINGS_BUTTON_WIDTH:
        board.pointer = True
        if board.mouse_click and board.state != State.SETTINGS:
            board.return_state = board.state
            board.state = State.SETTINGS

    # Test if music button in settings is clicked
    if MUSIC_BUTTON_LEFT <= board.mouse_coords['x'] <= MUSIC_BUTTON_LEFT + MUSIC_BUTTON_WIDTH and MUSIC_BUTTON_TOP <= board.mouse_coords['y'] <= MUSIC_BUTTON_TOP + MUSIC_BUTTON_WIDTH:
        board.pointer = True
        if board.mouse_click:
            board.music_on = not board.music_on
            board.mouse_click = False

    # Test if done button in settings is clicked
    if EXIT_SETTINGS_BUTTON_LEFT <= board.mouse_coords['x'] <= EXIT_SETTINGS_BUTTON_LEFT + EXIT_SETTINGS_BUTTON_WIDTH and EXIT_SETTINGS_BUTTON_TOP <= board.mouse_coords['y'] <= EXIT_SETTINGS_BUTTON_TOP + EXIT_SETTINGS_BUTTON_WIDTH:
        board.pointer = True
        if board.mouse_click:
            board.state = board.return_state
            board.return_state = None
            board.mouse_click = False

    # decrement wait time if game is not paused
    if board.wait_time > 0 and board.state != State.SETTINGS:
        board.wait_time -= 1


if __name__ == "__main__":
    board, renderer = init()

    while True:
        poll_input(board)
        update_game(board)
        renderer.render(board)
        clock.tick(fps)


# TODO:
# Decouple board.py into a gamestate.py
# - move state machine logic to gamestate
