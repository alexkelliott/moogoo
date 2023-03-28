import net
import pickle
import threading
from pygame.mixer import music

from screens.screen import Screen
from constants import *
from enums import State, Screen_Type


class Game_Screen(Screen):

	def __init__(self, game_state) -> None:
		super().__init__()

		# start thread to listen for server board updates
		self.server_listen_thread: threading.Thread = threading.Thread(target=self.listen_for_server_update, args=(game_state,), daemon=True)
		self.server_listen_thread.start()


	def __repr__(self) -> str:
		return "Game_Screen"


	def listen_for_server_update(self, game_state) -> None:
		while True:
			raw_gamestate: bytes = net.rec_data(game_state.sock)
			new_gamestate: 'Game_State' = pickle.loads(raw_gamestate)
			new_gamestate.board.game_state = game_state

			game_state.board = new_gamestate.board
			game_state.state = new_gamestate.state
			game_state.wait_time = new_gamestate.wait_time
			game_state.renderer.debug_message = new_gamestate.state


	def send_server_board(self, board, sock) -> None:
		net.send_data(sock, pickle.dumps(board))


	def update(self, game_state) -> None:
		# wait for the server to send over the board
		if not game_state.board:
			return

		# it is this player's turn
		if game_state.board.turn == game_state.player_turn_num and not game_state.settings_open:
			if game_state.state == State.BET:
				if game_state.board.handle_bet_selection():
					self.send_server_board(game_state.board, game_state.sock)

			elif game_state.state == State.CARD_SELECTION:
				if game_state.board.handle_card_selection():
					self.send_server_board(game_state.board, game_state.sock)

		# # Test if settings button is clicked
		if self.mouse_in(game_state.mouse_coords, SETTINGS_BUTTON["left"], SETTINGS_BUTTON["width"], SETTINGS_BUTTON["top"], SETTINGS_BUTTON["height"]):
			game_state.pointer = True
			if game_state.mouse_click:
				game_state.settings_open = not game_state.settings_open

		if game_state.settings_open:
			# Test if music button in settings is clicked
			if self.mouse_in(game_state.mouse_coords, MUSIC_BUTTON["left"], MUSIC_BUTTON["width"], MUSIC_BUTTON["top"], MUSIC_BUTTON["height"]):
				game_state.pointer = True
				if game_state.mouse_click:
					if game_state.music_on:
						music.pause()
					else:
						music.unpause()

					game_state.music_on = not game_state.music_on

			# volume slider
			elif self.mouse_in(game_state.mouse_coords, VOL_SLIDER["left"], VOL_SLIDER["width"], VOL_SLIDER["top"]-10, 25):
				game_state.pointer = True
				if game_state.mouse_down:
					game_state.volume = (game_state.mouse_coords['x']-5 - VOL_SLIDER["left"]) / VOL_SLIDER["width"]
					music.set_volume(game_state.volume)

			# # Test if done button in settings is clicked
			elif self.mouse_in(game_state.mouse_coords, EXIT_SETTINGS_BUTTON["left"], EXIT_SETTINGS_BUTTON["width"], EXIT_SETTINGS_BUTTON["top"], EXIT_SETTINGS_BUTTON["height"]):
				game_state.pointer = True
				if game_state.mouse_click:
					game_state.settings_open = False

		# back to connect screen
		if game_state.state == State.GAME_OVER_SCREEN:
			if self.mouse_in(game_state.mouse_coords, LOBBY_CONNECT_BUTTON["left"], LOBBY_CONNECT_BUTTON["width"], LOBBY_CONNECT_BUTTON["top"], LOBBY_CONNECT_BUTTON["height"]):
				game_state.pointer = True
				if game_state.mouse_click:
					game_state.reset_sock()
					game_state.state = State.CONNECT
					game_state.switch_screen(Screen_Type.CONNECT)

		# # decrement wait time
		if game_state.wait_time > 0:
			game_state.wait_time -= 1