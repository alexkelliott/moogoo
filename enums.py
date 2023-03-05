import enum


class Fruit(enum.Enum):
	COCONUT = 'c'
	WATERMELON = 'w'
	PINEAPPLE = 'p'

class Suit(enum.Enum):
	ORANGE = 'o'
	BLUE = 'b'
	GREEN = 'g'
	PURPLE = 'p'
	RED = 'r'
	SILVER = 's'

class State(enum.Enum):
	TURN_POPUP = 0
	PRE_BET = 1 # Only entered for NPCs
	BET = 2
	PRE_CARD_SELECTION = 3 # Only entered for NPCs
	CARD_SELECTION = 4
	POST_CARD_SELECTION = 5
	ROUND_ENDED = 6
	GAME_OVER_SCREEN = 7

class Wait(enum.Enum):
	# 60 = 1 second
	TURN_POPUP = 60
	PRE_BET = 45
	PRE_CARD_SELECTION = 45
	POST_CARD_SELECTION = 45
	ROUND_ENDED = 150