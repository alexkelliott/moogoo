import socket
import net
from enums import State, Screen_Type, Error

from screens.screen import Screen
from constants import *


class Connect_Screen(Screen):

	def __init__(self, game_state) -> None:
		super().__init__()


	def __repr__(self) -> str:
		return "Connect_Screen"		


	def update(self, game_state) -> None:
		if self.mouse_in(game_state.mouse_coords, LOBBY_CONNECT_BUTTON["left"], LOBBY_CONNECT_BUTTON["width"], LOBBY_CONNECT_BUTTON["top"], LOBBY_CONNECT_BUTTON["height"]):
			game_state.pointer = True

			if game_state.mouse_click:
				# try to connect to server...
				try:
					game_state.sock.connect((game_state.user_settings["ip"], game_state.user_settings["port"]))
				except:
					game_state.error = Error.CONN_REFUSED
					game_state.reset_sock()
					return

				# listen for server respond
				msg: str = net.rec_data(game_state.sock).decode()
				if msg == "STARTED":
					print("game is already in progress")
					game_state.error = Error.SERVER_STARTED

				elif msg == "CONNECTED":
					game_state.state = State.LOBBY
					game_state.switch_screen(Screen_Type.LOBBY)

				else:
					game_state.error = Error.UNKNOWN_RESPONSE
					print("unknown command recieved from server:", msg)