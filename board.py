import random
import time
import card
from suit import Suit

class Board():
	def __init__(self, players):
		self.deck = []
		self.bets = {}
		self.top_card = {}
		self.players = players
		self.turn = 2 # {0, 1, 2}. game starts on player 2 for some reason
		self.reset()
	

	def reset(self, removed_suits=[]):
		# reset deck
		for suit in Suit:
			if suit not in removed_suits:
				for value in range(8):
					rank = 'q' if value == 0 else str(value)
					self.deck.append(card.Card(suit, rank, value))

		# reset bets and cards
		for suit in Suit:
			if suit not in removed_suits:
				self.bets[suit] = []
				self.top_card[suit] = None


	def deal_cards(self):
		for player in self.players:
			cards = random.sample(self.deck, 5)
			player.hand = cards
			self.deck = [c for c in self.deck if c not in player.hand] # remove these cards from dealer deck

	# grab a single card after a card is played
	def get_card(self):
		if len(self.deck) == 0:
			return None

		choice = random.choice(self.deck)
		self.deck.remove(choice)
		return choice

	def next_turn(self, manual_set=None):
		if manual_set:
			self.turn = manual_set
		else:
			self.turn = (self.turn + 1) % 3 

	# if  first_round=True, then bets will be placed but no cards
	def handle_bet_selection(self):
		# first_round = sum([len(self.bets[suit]) for suit in Suit]) < 3
		
		player = self.players[self.turn]
		print(str(player) + " is placing a bet")

		if player.is_human: # Human player's turn

			# TODO: Implement player selection
			# Place a bet at random
			available = [suit for suit in self.bets if len(self.bets[suit]) < 4]
			choice = random.choice(available)
			self.bets[choice].append(player.fruit)
			player.score += 1
		
		else: #computer's turn

			# Place a bet at random
			available = [suit for suit in self.bets if len(self.bets[suit]) < 4] # find spots with < 4 bets
			choice = random.choice(available)
			self.bets[choice].append(player.fruit)
			player.score += 1

			

	def handle_card_selection(self):
		# no card selection unless enough bets are on the table
		if sum([len(self.bets[suit]) for suit in Suit]) <= 3:
			return

		player = self.players[self.turn]
		print(str(player) + " is placing a card")

		choice = random.choice(player.hand)
		self.top_card[choice.suit] = choice
		player.hand.remove(choice)

		player.hand.append(self.get_card())

	def __repr__(self):
		return ""

			