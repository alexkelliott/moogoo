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

	PLAYER_TURN_POPUP = 0
	PRE_BET = 1 # Only entered for NPCs
	BET = 2
	PRE_CARD_SELECTION = 3
	CARD_SELECTION = 4
	GAME_OVER_SCREEN = 5