# Sorting algorithims and pygame practice
import pygame
import os

from constants import *
from enums import Fruit, State, Wait
from game_state import Game_State

fps = 60


def poll_input(game_state):
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit()

        game_state.mouse_click = (ev.type == pygame.MOUSEBUTTONUP and ev.button == 1)

    mouse = pygame.mouse.get_pos()
    game_state.mouse_coords = {'x': mouse[0], 'y': mouse[1]}


def update_game(game_state):
    # assume that nothing is hovered by default
    game_state.pointer = False
    board = game_state.board

    # TURN_POPUP => PRE_BET, BET
    if game_state.state == State.TURN_POPUP and game_state.wait_time == 0:
        if board.players[board.turn].is_human:
            if board.bet_boxes_full():
                game_state.state = State.CARD_SELECTION
            else:
                game_state.state = State.BET
        else: # npc
            if board.bet_boxes_full():
                game_state.state = State.PRE_CARD_SELECTION
                game_state.wait_time = Wait.PRE_CARD_SELECTION.value
            else:
                game_state.state = State.PRE_BET
                game_state.wait_time = Wait.PRE_BET.value

    # PRE_BET => BET
    elif game_state.state == State.PRE_BET and game_state.wait_time == 0:
        game_state.state = State.BET

    # BET => PRE_CARD_SELECTION, CARD_SELECTION, TURN_POPUP
    elif game_state.state == State.BET:
        if board.handle_bet_selection():
            if board.three_bets():
                if board.players[board.turn].is_human:
                    game_state.state = State.CARD_SELECTION
                else:
                    game_state.state = State.PRE_CARD_SELECTION
                    game_state.wait_time = Wait.TURN_POPUP.value
            else:
                board.next_turn()
                game_state.state = State.TURN_POPUP
                game_state.wait_time = Wait.TURN_POPUP.value

    # PRE_CARD_SELECTION => CARD_SELECTION 
    elif game_state.state == State.PRE_CARD_SELECTION and game_state.wait_time == 0:
        game_state.state = State.CARD_SELECTION

    # CARD_SELECTION => POST_CARD_SELECTION
    elif game_state.state == State.CARD_SELECTION:
        if board.handle_card_selection():
            game_state.state = State.POST_CARD_SELECTION
            game_state.wait_time = Wait.POST_CARD_SELECTION.value

    # POST_CARD_SELECTION => TURN_POPUP, ROUND_ENDED, GAME_OVER_SCREEN
    elif game_state.state == State.POST_CARD_SELECTION and game_state.wait_time == 0:
        if board.round_complete():
            game_state.state = State.ROUND_ENDED
            game_state.wait_time = Wait.ROUND_ENDED.value

        else:
            board.next_turn()
            game_state.state = State.TURN_POPUP
            game_state.wait_time = Wait.TURN_POPUP.value

    # ROUND_ENDED => TURN_POPUP, GAME_OVER_SCREEN
    elif game_state.state == State.ROUND_ENDED and game_state.wait_time == 0:
        board.reset()

        if board.game_complete():
            game_state.state = State.GAME_OVER_SCREEN
            return

        game_state.state = State.TURN_POPUP
        game_state.wait_time = Wait.TURN_POPUP.value


    # Test if settings button is clicked
    if SETTINGS_BUTTON_LEFT <= game_state.mouse_coords['x'] <= SETTINGS_BUTTON_LEFT + SETTINGS_BUTTON_WIDTH and SETTINGS_BUTTON_TOP <= game_state.mouse_coords['y'] <= SETTINGS_BUTTON_TOP + SETTINGS_BUTTON_WIDTH:
        game_state.pointer = True
        if game_state.mouse_click and game_state.state != State.SETTINGS:
            game_state.return_state = game_state.state
            game_state.state = State.SETTINGS

    # Test if music button in settings is clicked
    if MUSIC_BUTTON_LEFT <= game_state.mouse_coords['x'] <= MUSIC_BUTTON_LEFT + MUSIC_BUTTON_WIDTH and MUSIC_BUTTON_TOP <= game_state.mouse_coords['y'] <= MUSIC_BUTTON_TOP + MUSIC_BUTTON_WIDTH:
        game_state.pointer = True
        if game_state.mouse_click:
            if game_state.music_on:
                game_state.music_on = False
                pygame.mixer.music.pause()
            else:
                game_state.music_on = True
                pygame.mixer.music.unpause()

            game_state.mouse_click = False

    # Test if done button in settings is clicked
    if game_state.state == State.SETTINGS:
        if EXIT_SETTINGS_BUTTON_LEFT <= game_state.mouse_coords['x'] <= EXIT_SETTINGS_BUTTON_LEFT + EXIT_SETTINGS_BUTTON_WIDTH and EXIT_SETTINGS_BUTTON_TOP <= game_state.mouse_coords['y'] <= EXIT_SETTINGS_BUTTON_TOP + EXIT_SETTINGS_BUTTON_WIDTH:
            game_state.pointer = True
            if game_state.mouse_click:
                game_state.state = game_state.return_state
                game_state.return_state = None
                game_state.mouse_click = False

    # decrement wait time if game is not paused
    if game_state.wait_time > 0 and game_state.state != State.SETTINGS:
        game_state.wait_time -= 1


if __name__ == "__main__":
    # init
    pygame.init()
    game_state = Game_State()
    clock = pygame.time.Clock()

    # game loop
    while True:
        poll_input(game_state)
        update_game(game_state)
        game_state.renderer.render(game_state)
        clock.tick(fps)
