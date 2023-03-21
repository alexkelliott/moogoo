import net
import pickle
import threading

from screens.screen import Screen
from constants import *
from enums import State


class Game_Screen(Screen):

	def __init__(self, game_state):
		super().__init__()

		# start thread to listen for server board updates
		self.server_listen_thread = threading.Thread(target=self.listen_for_server_update, args=(game_state,), daemon=True)
		self.server_listen_thread.start()


	def __repr__(self):
		return "Game_Screen"


	def listen_for_server_update(self, game_state):
		while True:
			raw_gamestate = net.rec_data(game_state.sock)
			new_gamestate = pickle.loads(raw_gamestate)
			new_gamestate.board.game_state = game_state

			game_state.board = new_gamestate.board
			game_state.state = new_gamestate.state
			game_state.wait_time = new_gamestate.wait_time
			game_state.renderer.debug_message = new_gamestate.state


	def send_server_board(self, board, sock):
		net.send_data(sock, pickle.dumps(board))


	def update(self, game_state):
		# wait for the server to send over the board
		if not game_state.board:
			return

		# assume that nothing is hovered by default
		game_state.pointer = False
		board = game_state.board

		# it is this player's turn
		if board.turn == game_state.player_turn_num and not game_state.settings_open:
			if game_state.state == State.BET:
				if board.handle_bet_selection():
					self.send_server_board(game_state.board, game_state.sock)

			elif game_state.state == State.CARD_SELECTION:
				if board.handle_card_selection():
					self.send_server_board(game_state.board, game_state.sock)

		# # Test if settings button is clicked
		if self.mouse_in(game_state.mouse_coords, SETTINGS_BUTTON_LEFT, SETTINGS_BUTTON_WIDTH, SETTINGS_BUTTON_TOP, SETTINGS_BUTTON_WIDTH):
			game_state.pointer = True
			if game_state.mouse_click:
				game_state.settings_open = not game_state.settings_open

		if game_state.settings_open:
			# Test if music button in settings is clicked
			if self.mouse_in(game_state.mouse_coords, MUSIC_BUTTON_LEFT, MUSIC_BUTTON_WIDTH, MUSIC_BUTTON_TOP, MUSIC_BUTTON_WIDTH):
				game_state.pointer = True
				if game_state.mouse_click:
					if game_state.music_on:
						pygame.mixer.music.pause()
					else:
						pygame.mixer.music.unpause()

					game_state.music_on = not game_state.music_on

			# volume slider
			elif self.mouse_in(game_state.mouse_coords, VOL_SLIDER_LEFT, VOL_SLIDER_WIDTH, VOL_SLIDER_TOP-10, 25):
				game_state.pointer = True
				if game_state.mouse_down:
					game_state.volume = (game_state.mouse_coords['x']-5 - VOL_SLIDER_LEFT) / VOL_SLIDER_WIDTH
					pygame.mixer.music.set_volume(game_state.volume)

			# # Test if done button in settings is clicked
			elif self.mouse_in(game_state.mouse_coords, EXIT_SETTINGS_BUTTON_LEFT, EXIT_SETTINGS_BUTTON_WIDTH, EXIT_SETTINGS_BUTTON_TOP, EXIT_SETTINGS_BUTTON_HEIGHT):
				game_state.pointer = True
				if game_state.mouse_click:
					game_state.settings_open = False

		# # decrement wait time
		if game_state.wait_time > 0:
			game_state.wait_time -= 1