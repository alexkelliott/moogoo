from suit import Suit
from fruit import Fruit
import card

class Player():
	def __init__(self, name, fruit, is_human=False):
		super(Player, self).__init__()
		self.name = name
		self.fruit = fruit
		self.hand = []
		self.score = 0
		self.is_human = is_human

		# new_card = card.Card(Suit.ORANGE, "3", 3)
		# print(new_card)


	def __repr__(self):
		return "Player: <" + self.name + ", " + str(self.fruit) + ">"
		