class Card():
	def __init__(self, suit, rank, value):
		super(Card, self).__init__()
		self.suit = suit
		self.rank = rank
		self.value = value
		self.filename = self.suit.value + self.rank + ".png" 


	def __repr__(self):
		return "Card: <" + str(self.suit) + ", " +  str(self.rank) + ", " + str(self.value) + ">\n"
		