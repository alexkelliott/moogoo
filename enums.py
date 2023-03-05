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
	ROUND_ENDED = 5
	GAME_OVER_SCREEN = 6

class Wait(enum.Enum):
	TURN_POPUP = 100
	PRE_BET = 100
	PRE_CARD_SELECTION = 100