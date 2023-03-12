import pygame
import random
import os

from board import Board
from renderer import Renderer
from player import Player
from enums import Fruit, State, Wait


nameChoices = ["Ava Cadavra", "Misty Waters", "Daddy Bigbucks", "Giuseppi Mezzoalto", "Dusty Hogg", "Phoebe Twiddle", "Luthor L. Bigbucks", "Lottie Cash", "Detective Dan D. Mann", "Pritchard Locksley", "Futo Maki", "Ephram Earl", "Lily Gates", "Cannonball Coleman", "Sue Pirmova", "Lincoln Broadsheet", "Crawdad Clem", "Bayou Boo", "Maximillian Moore", "Bucki Brock", "Berkeley Clodd", "Gramma Hattie", "Pepper Pete", "Dr. Mauricio Keys", "Olde Salty", "Lloyd", "Harlan King", "Daschell Swank", "Kris Thristle"]

class Game_State():

	def __init__(self, server=False, name=None, player_turn_num=None):
		# init players
		names = random.sample(nameChoices, 2)
		players = []
		if not name:
			name = "Placeholdername"
		players.append(Player(name, Fruit.COCONUT, is_human=True))
		players.append(Player(names[0], Fruit.WATERMELON))
		players.append(Player(names[1], Fruit.PINEAPPLE))
		
		# init board
		self.board = Board(players, self)

		# init state
		self.state = State.TURN_POPUP
		self.wait_time = Wait.TURN_POPUP.value

		if not server:
			self.player_turn_num = player_turn_num

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

# TODO:
#	-implement __getstate__ for pickle
#	-change return state to settings open for single player