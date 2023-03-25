from card import Card
from enums import Fruit


class Player():
	def __init__(self, name, fruit, is_human=False) -> None:
		super(Player, self).__init__()
		self.name: str = name
		self.fruit: Fruit = fruit
		self.hand: list[Card] = []
		self.score: int = 0
		self.is_human: bool = is_human


	def __repr__(self) -> str:
		return "Player: <" + self.name + ", " + str(self.fruit) + ">"