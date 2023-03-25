import enum


class Fruit(enum.Enum):
	COCONUT: str = 'c'
	WATERMELON: str = 'w'
	PINEAPPLE: str = 'p'

class Suit(enum.Enum):
	ORANGE: str = 'o'
	BLUE: str = 'b'
	GREEN: str = 'g'
	PURPLE: str = 'p'
	RED: str = 'r'
	SILVER: str = 's'

class State(enum.Enum):
	TURN_POPUP: int = 0
	PRE_BET: int = 1 # Only entered for NPCs
	BET: int = 2
	PRE_CARD_SELECTION: int = 3 # Only entered for NPCs
	CARD_SELECTION: int = 4
	POST_CARD_SELECTION: int = 5
	ROUND_ENDED: int = 6
	GAME_OVER_SCREEN: int = 7
	SETTINGS: int = 8,
	CONNECT: int = 9,
	LOBBY: int = 10

class Wait(enum.Enum):
	# 60 = 1 second
	TURN_POPUP: int = 60
	PRE_BET: int = 45
	PRE_CARD_SELECTION: int = 45
	POST_CARD_SELECTION: int = 45
	ROUND_ENDED: int = 150