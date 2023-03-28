import enum
from enum import auto

class Fruit(enum.Enum):
	COCONUT:    str = 'c'
	WATERMELON: str = 'w'
	PINEAPPLE:  str = 'p'


class Suit(enum.Enum):
	ORANGE: str = 'o'
	BLUE:   str = 'b'
	GREEN:  str = 'g'
	PURPLE: str = 'p'
	RED:    str = 'r'
	SILVER: str = 's'


class State(enum.Enum):
	TURN_POPUP          = auto()
	PRE_BET             = auto() # Only entered for NPCs
	BET                 = auto()
	PRE_CARD_SELECTION  = auto() # Only entered for NPCs
	CARD_SELECTION      = auto()
	POST_CARD_SELECTION = auto()
	ROUND_ENDED         = auto()
	GAME_OVER_SCREEN    = auto()
	SETTINGS            = auto()
	CONNECT             = auto()
	LOBBY               = auto()


class Wait(enum.Enum):
	# 60 = 1 second
	TURN_POPUP:          int = 60
	PRE_BET:             int = 45
	PRE_CARD_SELECTION:  int = 45
	POST_CARD_SELECTION: int = 45
	ROUND_ENDED:         int = 150


class Screen_Type(enum.Enum):
	CONNECT = auto()
	LOBBY   = auto()
	GAME    = auto()


class Error(enum.Enum):
	SERVER_STARTED   = auto()
	LOBBY_FULL       = auto()
	CONN_REFUSED     = auto()
	UNKNOWN_RESPONSE = auto()
