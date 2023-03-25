import socket
import net
from enums import State

from screens.screen import Screen
from screens.lobby_screen import Lobby_Screen
from constants import *


class Connect_Screen(Screen):

	def __init__(self) -> None:
		super().__init__()


	def __repr__(self) -> str:
		return "Connect_Screen"		


	def update(self, game_state) -> None:
		if self.mouse_in(game_state.mouse_coords, LOBBY_CONNECT_BUTTON["left"], LOBBY_CONNECT_BUTTON["width"], LOBBY_CONNECT_BUTTON["top"], LOBBY_CONNECT_BUTTON["height"]):
			game_state.pointer = True

			if game_state.mouse_click:
				# try to connect to server...
				game_state.sock.connect((game_state.user_settings["ip"], game_state.user_settings["port"]))

				# listen for server respond
				msg: str = net.rec_data(game_state.sock).decode()
				if msg == "STARTED":
					print("game is already in progress")

				elif msg == "CONNECTED":
					game_state.state = State.LOBBY
					game_state.current_screen = Lobby_Screen(game_state)

				else:
					print("unknown command recieved from server:", msg)