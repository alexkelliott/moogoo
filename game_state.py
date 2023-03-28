import pygame
import random
import socket
import os

from screens.connect_screen import Connect_Screen
from screens.lobby_screen import Lobby_Screen
from screens.game_screen import Game_Screen
from screens.screen import Screen
from board import Board
from renderer import Renderer
from player import Player
from enums import Fruit, State, Wait, Suit, Screen_Type

nameChoices: list[str] = ["Ava Cadavra", "Misty Waters", "Daddy Bigbucks", "Giuseppi Mezzoalto", "Dusty Hogg", "Phoebe Twiddle", "Luthor L. Bigbucks", "Lottie Cash", "Detective Dan D. Mann", "Pritchard Locksley", "Futo Maki", "Ephram Earl", "Lily Gates", "Cannonball Coleman", "Sue Pirmova", "Lincoln Broadsheet", "Crawdad Clem", "Bayou Boo", "Maximillian Moore", "Bucki Brock", "Berkeley Clodd", "Gramma Hattie", "Pepper Pete", "Dr. Mauricio Keys", "Olde Salty", "Lloyd", "Harlan King", "Daschell Swank", "Kris Thristle"]


class Game_State():

	def __init__(self) -> None:
		# init state
		self.wait_time: int = Wait.TURN_POPUP.value
		self.board: Board = None

	def gen_board(self, passed_in_players) -> None:
		# init players
		# fill places with computer players first
		names: list[str] = random.sample(nameChoices, 2)
		players: list[Player] = [
			None,
			Player(names[0], Fruit.WATERMELON),
			Player(names[1], Fruit.PINEAPPLE)
		]
		
		for i in range(len(passed_in_players)):
			players[i] = passed_in_players[i]

		# init board
		self.board = Board(players, self)


class Server_Game_State(Game_State):

	def __init__(self) -> None:
		 super().__init__()
		 self.state: State = State.TURN_POPUP


class Client_Game_State(Game_State):

	def __init__(self) -> None:
		super().__init__()
		
		# read user settings file
		self.user_settings: dict[str, [str | int]] = {"player_name": None, "ip": None, "port" : None}
		
		self.current_screen: Screen = Connect_Screen(self)
		self.state: State = State.CONNECT

		self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.player_turn_num: int = -1
		self.team_mates: list[Player] = [] # used for lobby screen, includes ALL players

		# init renderer
		self.renderer: Renderer = Renderer()

		# init mixer
		self.music_on: bool = False
		self.volume: float = 0.75 # [0, 1]
		pygame.mixer.init()
		pygame.mixer.music.load(os.path.join('assets', 'audio', 'soundtrack.mp3'))
		pygame.mixer.music.set_volume(self.volume)
		pygame.mixer.music.play()
		pygame.mixer.music.pause()

		# init mouse states
		self.pointer: bool = False
		self.mouse_coords: dict[str, int] = {'x':  -1, 'y': -1}
		self.mouse_click: bool = False # mouse down then up
		self.mouse_down: bool = False
		self.hovered_bet: Suit = None
		self.hovered_card: Card = None

		# settings
		self.settings_open: bool = False # only used in multiplayer
		self.return_state: State = None # state to return to after visiting settings 

		self.error = None

	def switch_screen(self, new_screen):
		match new_screen:
		    case Screen_Type.CONNECT:
		         self.current_screen = Connect_Screen(self)
		    case Screen_Type.LOBBY:
		         self.current_screen = Lobby_Screen(self)
		    case Screen_Type.GAME:
		         self.current_screen = Game_Screen(self)


	def reset_sock(self):
		if self.sock:
			self.sock.close()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)