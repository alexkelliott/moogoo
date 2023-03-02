import random
import pygame
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
		self.removed_suits = []

		self.reset()
	

	def reset(self):
		# reset deck
		# print("deck pre removal", self.deck)
		self.deck = []
		# print("deck after removal", self.deck)
		# print("removed_suits", self.removed_suits)
		for suit in Suit:
			if suit not in self.removed_suits:
				for value in range(8):
					rank = 'q' if value == 0 else str(value)
					# print("adding", suit, rank)
					self.deck.append(card.Card(suit, rank, value))

		# print("after deck", self.deck)


		# reset player hands
		for player in self.players:
			player.hand = []

		# reset bets and cards
		for suit in Suit:
			# if suit not in self.removed_suits:
			self.bets[suit] = []
			self.top_card[suit] = None

		# reset turn
		self.turn = 2


	# return's lowest monkey if the round is complete
	def round_complete(self):
		top_card_list = [c for c in self.top_card.values() if c]
		full_cards = (len(top_card_list) == 6 - len(self.removed_suits))

		if full_cards:
			top_card_list.sort(key=lambda x: x.value)
			no_tie = top_card_list[0].value != top_card_list[1].value

			if full_cards and no_tie:
				self.removed_suits.append(top_card_list[0].suit)
				print("Removed", top_card_list[0].suit)

				# remove the bets under the removed suit
				for bet in self.bets[top_card_list[0].suit]:
					for player in self.players:
						if bet == player.fruit:
							player.score -= 1

				return True
		return False


	def game_complete(self):
		return len(self.removed_suits) == 3


	def final_scores(self):
		sorted_players = self.players
		sorted_players.sort(key=lambda x: x.score, reverse=True)
		return sorted_players


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


	def next_turn(self):
		self.turn = (self.turn + 1) % 3
		return self.players[self.turn]


	def get_hovered_bet(self, bet_boundaries):
		mouse = pygame.mouse.get_pos()

		for suit in Suit:
			if suit not in self.removed_suits and len(self.bets[suit]) < 4:
				bound = bet_boundaries[suit]
				if bound["left"] <= mouse[0] <= bound["right"] and bound["top"] <= mouse[1] <= bound["bottom"]:
					return suit

		return None


	def handle_bet_selection(self, renderer):
		player = self.players[self.turn]
		print(str(player) + " is placing a bet")
		renderer.top_text = "Place a bet"

		choice = None

		if player.is_human: # Human player's turn
			while not choice:
				new_hovered = self.get_hovered_bet(renderer.bet_boundaries)
				if new_hovered != renderer.hovered_bet:
					renderer.hovered_bet = new_hovered
					renderer.render(self)

				for ev in pygame.event.get():
					if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
						if renderer.hovered_bet:
							choice = renderer.hovered_bet
							renderer.hovered_bet = None
							break
					if ev.type == pygame.QUIT:
						pygame.quit()

		else: # computer's turn
			# Place a bet at random
			available = [suit for suit in self.bets if suit not in self.removed_suits and len(self.bets[suit]) < 4] # find spots with < 4 bets
			choice = random.choice(available)

		self.bets[choice].append(player.fruit)
		player.score += 1
		return choice


	def get_hovered_card(self, card_boundaries):
		mouse = pygame.mouse.get_pos()
		hand = self.players[self.turn].hand

		for i in range(len(hand)):
			if hand[i]:
				bound = card_boundaries[i]
				if bound["left"] <= mouse[0] <= bound["right"] and bound["top"] <= mouse[1] <= bound["bottom"]:
					return hand[i]

		return None


	def handle_card_selection(self, renderer):
		# no card selection unless enough bets are on the table
		if sum([len(self.bets[suit]) for suit in Suit]) <= 3:
			return
		player = self.players[self.turn]
		print(str(player) + " is placing a card")

		renderer.top_text = "Play a card"

		choice = None

		if player.is_human:
			choice = None
			while not choice:
				new_hovered = self.get_hovered_card(renderer.card_boundaries)
				if new_hovered != renderer.hovered_card:
					renderer.hovered_card = new_hovered
					renderer.render(self)

				for ev in pygame.event.get():
					if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
						if renderer.hovered_card:
							choice = renderer.hovered_card
							renderer.hovered_bet = None
							break
					if ev.type == pygame.QUIT:
						pygame.quit()

		else: # computer's turn
			choice = random.choice(player.hand)
		

		# if the card is '?' assign it a value
		if choice.rank == 'q':
			new_val = random.randint(1,7)
			choice.rank = new_val
			choice.value = new_val

		self.top_card[choice.suit] = choice
		player.hand.remove(choice)
		player.hand.append(self.get_card())

		return choice


	def __repr__(self):
		return ""

			