class Card():
	def __init__(self, suit, rank, value):
		super(Card, self).__init__()
		self.suit = suit
		self.rank = rank
		self.value = value
		
		
	# filename may change through the game with '?' cards
	def get_filename(self):
		return str(self.suit.value) + str(self.rank) + ".png" 


	def __repr__(self):
		return "Card: <" + str(self.suit) + ", " +  str(self.rank) + ", " + str(self.value) + ">\n"
		