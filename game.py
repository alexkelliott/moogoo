
import pygame
import os
import threading
import pickle
import time
import socket
from constants import *
from enums import Fruit, State, Wait
from game_state import Game_State

fps = 60
HOST = "127.0.0.1"
PORT = 13000

def poll_input(game_state):
	game_state.mouse_click = False

	for ev in pygame.event.get():
		if ev.type == pygame.QUIT:
			pygame.quit()

		if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
			game_state.mouse_click = True
			game_state.mouse_down = False

		if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
			game_state.mouse_down = True


	mouse = pygame.mouse.get_pos()
	game_state.mouse_coords = {'x': mouse[0], 'y': mouse[1]}


def mouse_in(mouse_coords, left, width, top, height):
	return left <= mouse_coords['x'] <= left + width and top <= mouse_coords['y'] <= top + height


def update_game(game_state):
	# assume that nothing is hovered by default
	game_state.pointer = False
	board = game_state.board

	# # TURN_POPUP => PRE_BET, BET
	# if game_state.state == State.TURN_POPUP and game_state.wait_time == 0:
	#     if board.players[board.turn].is_human:
	#         if board.bet_boxes_full():
	#             game_state.state = State.CARD_SELECTION
	#         else:
	#             game_state.state = State.BET
	#     else: # npc
	#         if board.bet_boxes_full():
	#             game_state.state = State.PRE_CARD_SELECTION
	#             game_state.wait_time = Wait.PRE_CARD_SELECTION.value
	#         else:
	#             game_state.state = State.PRE_BET
	#             game_state.wait_time = Wait.PRE_BET.value

	# # PRE_BET => BET
	# elif game_state.state == State.PRE_BET and game_state.wait_time == 0:
	#     game_state.state = State.BET

	# # BET => PRE_CARD_SELECTION, CARD_SELECTION, TURN_POPUP
	# elif game_state.state == State.BET:
	#     if board.handle_bet_selection():
	#         if board.three_bets():
	#             if board.players[board.turn].is_human:
	#                 game_state.state = State.CARD_SELECTION
	#             else:
	#                 game_state.state = State.PRE_CARD_SELECTION
	#                 game_state.wait_time = Wait.TURN_POPUP.value
	#         else:
	#             board.next_turn()
	#             game_state.state = State.TURN_POPUP
	#             game_state.wait_time = Wait.TURN_POPUP.value

	# # PRE_CARD_SELECTION => CARD_SELECTION 
	# elif game_state.state == State.PRE_CARD_SELECTION and game_state.wait_time == 0:
	#     game_state.state = State.CARD_SELECTION

	# # CARD_SELECTION => POST_CARD_SELECTION
	# elif game_state.state == State.CARD_SELECTION:
	#     if board.handle_card_selection():
	#         game_state.state = State.POST_CARD_SELECTION
	#         game_state.wait_time = Wait.POST_CARD_SELECTION.value

	# # POST_CARD_SELECTION => TURN_POPUP, ROUND_ENDED, GAME_OVER_SCREEN
	# elif game_state.state == State.POST_CARD_SELECTION and game_state.wait_time == 0:
	#     if board.round_complete():
	#         game_state.state = State.ROUND_ENDED
	#         game_state.wait_time = Wait.ROUND_ENDED.value

	#     else:
	#         board.next_turn()
	#         game_state.state = State.TURN_POPUP
	#         game_state.wait_time = Wait.TURN_POPUP.value

	# # ROUND_ENDED => TURN_POPUP, GAME_OVER_SCREEN
	# elif game_state.state == State.ROUND_ENDED and game_state.wait_time == 0:
	#     board.reset()

	#     if board.game_complete():
	#         game_state.state = State.GAME_OVER_SCREEN
	#         return

	#     game_state.state = State.TURN_POPUP
	#     game_state.wait_time = Wait.TURN_POPUP.value

	# # Test if settings button is clicked
	# if mouse_in(game_state.mouse_coords, SETTINGS_BUTTON_LEFT, SETTINGS_BUTTON_WIDTH, SETTINGS_BUTTON_TOP, SETTINGS_BUTTON_WIDTH):
	#     game_state.pointer = True
	#     if game_state.mouse_click and game_state.state != State.SETTINGS:
	#         game_state.return_state = game_state.state
	#         game_state.state = State.SETTINGS

	# # Test if music button in settings is clicked
	# if mouse_in(game_state.mouse_coords, MUSIC_BUTTON_LEFT, MUSIC_BUTTON_WIDTH, MUSIC_BUTTON_TOP, MUSIC_BUTTON_WIDTH):
	#     game_state.pointer = True
	#     if game_state.mouse_click:
	#         if game_state.music_on:
	#             pygame.mixer.music.pause()
	#         else:
	#             pygame.mixer.music.unpause()

	#         game_state.music_on = not game_state.music_on

	# # volume slider
	# vol_left = VOL_SLIDER_LEFT + game_state.volume * (VOL_SLIDER_WIDTH)
	# if mouse_in(game_state.mouse_coords, VOL_SLIDER_LEFT, VOL_SLIDER_WIDTH, VOL_SLIDER_TOP-10, 25):
	#     game_state.pointer = True
	#     if game_state.mouse_down:
	#         game_state.volume = (game_state.mouse_coords['x']-5 - VOL_SLIDER_LEFT) / VOL_SLIDER_WIDTH
	#         pygame.mixer.music.set_volume(game_state.volume)

	# # Test if done button in settings is clicked
	# if game_state.state == State.SETTINGS:
	#     if mouse_in(game_state.mouse_coords, EXIT_SETTINGS_BUTTON_LEFT, EXIT_SETTINGS_BUTTON_WIDTH, EXIT_SETTINGS_BUTTON_TOP, EXIT_SETTINGS_BUTTON_HEIGHT):
	#         game_state.pointer = True
	#         if game_state.mouse_click:
	#             game_state.state = game_state.return_state
	#             game_state.return_state = None

	# # decrement wait time if game is not paused
	# if game_state.wait_time > 0 and game_state.state != State.SETTINGS:
	#     game_state.wait_time -= 1


def listen_for_server_update(sock, game_state):

	HEADERSIZE = 10

	while True:
		print("listening for server message...")


		full_msg = b''
		new_msg = True
		while True:
			msg = sock.recv(16)
			if new_msg:
				# print("new msg len:",msg[:HEADERSIZE])
				msglen = int(msg[:HEADERSIZE])
				new_msg = False

			# print(f"full message length: {msglen}")

			full_msg += msg

			# print(len(full_msg))

			if len(full_msg)-HEADERSIZE == msglen:
				print("full msg recvd")
				raw_gamestate = full_msg[HEADERSIZE:]
				new_gamestate = pickle.loads(raw_gamestate)
				game_state.renderer.debug_message = new_gamestate.state
				new_msg = True
				full_msg = b""


if __name__ == "__main__":
	# init
	pygame.init()
	game_state = Game_State()
	clock = pygame.time.Clock()

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((HOST, PORT))
	sock.sendall(b"PlayernameHere")
	print(sock.recv(1024).decode())

	server_listen_thread = threading.Thread(target=listen_for_server_update, args=(sock,game_state,), daemon=True)
	server_listen_thread.start()

	# game loop

	while True:
		poll_input(game_state)
		# update_game(game_state)
		# game_state.renderer.debug_message = "TEST"
		game_state.renderer.render(game_state)
		clock.tick(fps)


# TODO:
#   -make function to detect if mouse is in a certain bound