import pygame
import random
import os

from board import Board
from renderer import Renderer
from player import Player
from enums import Fruit, State, Wait


nameChoices = ["Ava Cadavra", "Misty Waters", "Daddy Bigbucks", "Giuseppi Mezzoalto", "Dusty Hogg", "Phoebe Twiddle", "Luthor L. Bigbucks", "Lottie Cash", "Detective Dan D. Mann", "Pritchard Locksley", "Futo Maki", "Ephram Earl", "Lily Gates", "Cannonball Coleman", "Sue Pirmova", "Lincoln Broadsheet", "Crawdad Clem", "Bayou Boo", "Maximillian Moore", "Bucki Brock", "Berkeley Clodd", "Gramma Hattie", "Pepper Pete", "Dr. Mauricio Keys", "Olde Salty", "Lloyd", "Harlan King", "Daschell Swank", "Kris Thristle"]

class Game_State():

	def __init__(self):
		# init renderer
		self.renderer = Renderer()

		# init players
		names = random.sample(nameChoices, 2)
		players = []
		players.append(Player("Alex", Fruit.COCONUT, is_human=True))
		players.append(Player(names[0], Fruit.WATERMELON))
		players.append(Player(names[1], Fruit.PINEAPPLE))
		
		# init board
		self.board = Board(players, self)

		# init mixer
		pygame.mixer.init()
		pygame.mixer.music.load(os.path.join('assets', 'audio', 'soundtrack.mp3'))
		pygame.mixer.music.set_volume(0.7)
		pygame.mixer.music.play()
		pygame.mixer.music.pause()
		self.music_on = False

		# init state
		self.state = State.TURN_POPUP
		self.return_state = None # state to return to after visiting settings menu
		self.wait_time = Wait.TURN_POPUP.value

		# init mouse states
		self.pointer = False
		self.mouse_coords = {'x':  -1, 'y': -1}
		self.mouse_click = False
		self.hovered_bet = None
		self.hovered_card = None