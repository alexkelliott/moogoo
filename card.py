from enums import Suit


class Card():
	def __init__(self, suit, rank, value):
		super(Card, self).__init__()
		self.suit: Suit = suit
		self.rank: str = rank
		self.value: int = value
		self.is_q: bool = rank == "q"


	def __repr__(self):
		return "Card: <" + str(self.suit) + ", " +  str(self.rank) + ", " + str(self.value) + ">\n"
		