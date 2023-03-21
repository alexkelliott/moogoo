import pickle
import threading
import net

from screens.screen import Screen
from screens.game_screen import Game_Screen
from constants import *


class Lobby_Screen(Screen):

	def __init__(self, game_state):
		super().__init__()

		# # tell server the chosen name and get back the turn number
		net.send_data(game_state.sock, game_state.user_settings["player_name"].encode())
		turn_num = int(net.rec_data(game_state.sock))
		game_state.player_turn_num = turn_num

		# # start thread to listen for server LOBBY updates
		self.lobby_listen_thread = threading.Thread(target=self.listen_for_lobby_update, args=(game_state.sock, game_state,), daemon=True)
		self.lobby_listen_thread.start()


	def __repr__(self):
		return "Lobby_Screen"


	def listen_for_lobby_update(self, sock, game_state):
		while True:
			data = net.rec_data(sock)

			try:
				if data.decode() == "STARTING":
					break
			except:
				pass

			clients = pickle.loads(data)
			game_state.team_mates = [c.player for c in clients]


	def update(self, game_state):
		# if thread is dead, game has started, change screens
		if not self.lobby_listen_thread.is_alive():
			game_state.current_screen = Game_Screen(game_state)
			self.lobby_listen_thread.join() # <- not sure if necessary

		# test for start game button press
		if game_state.player_turn_num == 0:
			if self.mouse_in(game_state.mouse_coords, LOBBY_CONNECT_BUTTON_LEFT, LOBBY_CONNECT_BUTTON_WIDTH, LOBBY_CONNECT_BUTTON_TOP, LOBBY_CONNECT_BUTTON_HEIGHT):
				game_state.pointer = True
				if game_state.mouse_click:
					# send start game message to server
					net.send_data(game_state.sock, "START_GAME".encode())