import pygame
import random
import socket
import os

from screens.connect_screen import Connect_Screen
from board import Board
from renderer import Renderer
from player import Player
from enums import Fruit, State, Wait

nameChoices = ["Ava Cadavra", "Misty Waters", "Daddy Bigbucks", "Giuseppi Mezzoalto", "Dusty Hogg", "Phoebe Twiddle", "Luthor L. Bigbucks", "Lottie Cash", "Detective Dan D. Mann", "Pritchard Locksley", "Futo Maki", "Ephram Earl", "Lily Gates", "Cannonball Coleman", "Sue Pirmova", "Lincoln Broadsheet", "Crawdad Clem", "Bayou Boo", "Maximillian Moore", "Bucki Brock", "Berkeley Clodd", "Gramma Hattie", "Pepper Pete", "Dr. Mauricio Keys", "Olde Salty", "Lloyd", "Harlan King", "Daschell Swank", "Kris Thristle"]


class Game_State():

	def __init__(self):
		# init state
		self.wait_time = Wait.TURN_POPUP.value
		self.board = None

	def gen_board(self, passed_in_players):
		# init players
		# fill places with computer players first
		names = random.sample(nameChoices, 2)
		players = [
			None,
			Player(names[0], Fruit.WATERMELON),
			Player(names[1], Fruit.PINEAPPLE)
		]
		
		for i in range(len(passed_in_players)):
			players[i] = passed_in_players[i]

		# init board
		self.board = Board(players, self)


class Server_Game_State(Game_State):

	def __init__(self):
		 super().__init__()
		 self.state = State.TURN_POPUP


class Client_Game_State(Game_State):

	def __init__(self):
		super().__init__()
		
		# read user settings file
		self.user_settings = {"player_name": None, "ip": None, "port" : None}
		
		self.current_screen = Connect_Screen()
		self.state = State.CONNECT

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.player_turn_num = -1
		self.team_mates = [] # used for lobby screen, includes ALL players

		# init renderer
		self.renderer = Renderer()

		# init mixer
		self.music_on = False
		self.volume = 0.75 # [0, 1]
		pygame.mixer.init()
		pygame.mixer.music.load(os.path.join('assets', 'audio', 'soundtrack.mp3'))
		pygame.mixer.music.set_volume(self.volume)
		pygame.mixer.music.play()
		pygame.mixer.music.pause()

		# init mouse states
		self.pointer = False
		self.mouse_coords = {'x':  -1, 'y': -1}
		self.mouse_click = False # mouse down then up
		self.mouse_down = False
		self.hovered_bet = None
		self.hovered_card = None

		# settings
		self.settings_open = False # only used in multiplayer
		self.return_state = None # state to return to after visiting settings menu