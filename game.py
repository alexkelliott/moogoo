import pygame
import threading
import pickle
import socket
import json

from constants import *
from net import *
from enums import Fruit, State, Wait
from game_state import Client_Game_State

fps = 60

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


def update_server(board, sock):
	print("sending update to server")
	print(pickle.dumps(board))
	print()

	send_data(sock, pickle.dumps(board))


def update_game(game_state, sock, turn_num):
	# assume that nothing is hovered by default
	game_state.pointer = False
	board = game_state.board

	# it is this player's turn
	if board.turn == turn_num and not game_state.settings_open:
		if game_state.state == State.BET:
			if board.handle_bet_selection():
				update_server(game_state.board, sock)

		elif game_state.state == State.CARD_SELECTION:
			if board.handle_card_selection():
				update_server(game_state.board, sock)

	# # Test if settings button is clicked
	if mouse_in(game_state.mouse_coords, SETTINGS_BUTTON_LEFT, SETTINGS_BUTTON_WIDTH, SETTINGS_BUTTON_TOP, SETTINGS_BUTTON_WIDTH):
		game_state.pointer = True
		if game_state.mouse_click:
			game_state.settings_open = not game_state.settings_open

	if game_state.settings_open:
		# Test if music button in settings is clicked
		if mouse_in(game_state.mouse_coords, MUSIC_BUTTON_LEFT, MUSIC_BUTTON_WIDTH, MUSIC_BUTTON_TOP, MUSIC_BUTTON_WIDTH):
			game_state.pointer = True
			if game_state.mouse_click:
				if game_state.music_on:
					pygame.mixer.music.pause()
				else:
					pygame.mixer.music.unpause()

				game_state.music_on = not game_state.music_on

		# volume slider
		elif mouse_in(game_state.mouse_coords, VOL_SLIDER_LEFT, VOL_SLIDER_WIDTH, VOL_SLIDER_TOP-10, 25):
			game_state.pointer = True
			if game_state.mouse_down:
				game_state.volume = (game_state.mouse_coords['x']-5 - VOL_SLIDER_LEFT) / VOL_SLIDER_WIDTH
				pygame.mixer.music.set_volume(game_state.volume)

		# # Test if done button in settings is clicked
		elif mouse_in(game_state.mouse_coords, EXIT_SETTINGS_BUTTON_LEFT, EXIT_SETTINGS_BUTTON_WIDTH, EXIT_SETTINGS_BUTTON_TOP, EXIT_SETTINGS_BUTTON_HEIGHT):
			game_state.pointer = True
			if game_state.mouse_click:
				game_state.settings_open = False

	if game_state.state == State.LOBBY:
		pass

	# # decrement wait time
	if game_state.wait_time > 0:
		game_state.wait_time -= 1


def listen_for_server_update(sock, game_state):
	while True:
		raw_gamestate = rec_data(sock)
		new_gamestate = pickle.loads(raw_gamestate)
		new_gamestate.board.game_state = game_state

		game_state.board = new_gamestate.board
		game_state.state = new_gamestate.state
		game_state.wait_time = new_gamestate.wait_time
		game_state.renderer.debug_message = new_gamestate.state


def listen_for_lobby_update(sock, game_state):
	while True:
		data = rec_data(sock)

		try:
			if data.decode() == "STARTING":
				print("server is starting!")
				break
		except:
			pass

		print("recieved", data)

		clients = pickle.loads(data)
		game_state.team_mates = [c.player for c in clients]


if __name__ == "__main__":

	# init game variables
	pygame.init()
	clock = pygame.time.Clock()
	game_state = Client_Game_State()
	game_state.state = State.CONNECT

	# read user settings
	with open("user_settings.json", "r") as us:
		settings = json.loads(us.read())
		game_state.user_settings = {
			"ip":          settings["hostname"],
			"port":        int(settings["port"]),
			"player_name": settings["player_name"]}

	# Connect loop
	# clean this up
	while True:
		poll_input(game_state)
		game_state.pointer = False
		if mouse_in(game_state.mouse_coords, LOBBY_CONNECT_BUTTON_LEFT, LOBBY_CONNECT_BUTTON_WIDTH, LOBBY_CONNECT_BUTTON_TOP, LOBBY_CONNECT_BUTTON_HEIGHT):
			game_state.pointer = True
			if game_state.mouse_click:
				game_state.state = State.LOBBY
				break

		game_state.renderer.render(game_state)
		clock.tick(fps)

	# init socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((game_state.user_settings["ip"], game_state.user_settings["port"]))

	# # tell server the chosen name and get back the turn number
	send_data(sock, game_state.user_settings["player_name"].encode())
	turn_num = int(rec_data(sock))
	game_state.player_turn_num = turn_num

	# # start thread to listen for server LOBBY updates
	lobby_listen_thread = threading.Thread(target=listen_for_lobby_update, args=(sock,game_state,), daemon=True)
	lobby_listen_thread.start()

	# Lobby loop
	# clean this up
	while lobby_listen_thread.is_alive():
		poll_input(game_state)
		game_state.pointer = False
		if game_state.player_turn_num == 0:
			if mouse_in(game_state.mouse_coords, LOBBY_CONNECT_BUTTON_LEFT, LOBBY_CONNECT_BUTTON_WIDTH, LOBBY_CONNECT_BUTTON_TOP, LOBBY_CONNECT_BUTTON_HEIGHT):
				game_state.pointer = True
				if game_state.mouse_click:
					# send start game message to server
					send_data(sock, "START_GAME".encode())
					break

		game_state.renderer.render(game_state)
		clock.tick(fps)

	lobby_listen_thread.join()


	
	# start thread to listen for server board updates
	server_listen_thread = threading.Thread(target=listen_for_server_update, args=(sock,game_state,), daemon=True)
	server_listen_thread.start()

	# wait for the server to send over the board
	while not game_state.board:
		pass

	# game loop
	while True:
		poll_input(game_state)
		update_game(game_state, sock, turn_num)
		game_state.renderer.render(game_state)
		clock.tick(fps)


# TODO:
#	-allow for user to choose their own name in game (not thru file)
#	-add graceful failure if can't connect to server
#	-change return state to settings open for single player
#	-make the lobby screen actually decent
#	-handle clients leaving
#	-allow players to chose their own fruits
#	-make new set of dimmmensions for start game button
#	-move sending and receiving functions to a seperate file
#	-update all sends to include header