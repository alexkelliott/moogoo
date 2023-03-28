import pickle
import threading
import net

from screens.screen import Screen
from enums import Screen_Type
from constants import *


class Lobby_Screen(Screen):

	def __init__(self, game_state) -> None:
		super().__init__()

		# tell server the chosen name and get back the turn number
		net.send_data(game_state.sock, game_state.user_settings["player_name"].encode())
		turn_num: int = int(net.rec_data(game_state.sock))
		game_state.player_turn_num = turn_num

		# start thread to listen for server LOBBY updates
		self.lobby_listen_thread: threading.Thread = threading.Thread(target=self.listen_for_lobby_update, args=(game_state.sock, game_state,), daemon=True)
		self.lobby_listen_thread.start()


	def __repr__(self) -> str:
		return "Lobby_Screen"


	def listen_for_lobby_update(self, sock, game_state) -> None:
		while True:
			data: bytes = net.rec_data(sock)

			try:
				if data.decode() == "STARTING":
					break
			except:
				pass

			team_mates: list[Player] = pickle.loads(data)
			game_state.team_mates = team_mates


	def update(self, game_state) -> None:
		# if thread is dead, game has started, change screens
		if not self.lobby_listen_thread.is_alive():
			game_state.switch_screen(Screen_Type.GAME)
			self.lobby_listen_thread.join() # <- not sure if necessary

		# test for start game button press
		if game_state.player_turn_num == 0:
			if self.mouse_in(game_state.mouse_coords, LOBBY_CONNECT_BUTTON["left"], LOBBY_CONNECT_BUTTON["width"], LOBBY_CONNECT_BUTTON["top"], LOBBY_CONNECT_BUTTON["height"]):
				game_state.pointer = True
				if game_state.mouse_click:
					# send start game message to server
					net.send_data(game_state.sock, "START_GAME".encode())