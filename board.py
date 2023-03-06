import random
import pygame
import time
import card
from constants import *
from enums import Suit, State, Wait


class Board():
	def __init__(self, players):
		self.deck = []
		for suit in Suit:
			for value in range(8):
				rank = 'q' if value == 0 else str(value)
				self.deck.append(card.Card(suit, rank, value))

		self.bets = {}
		for suit in Suit:
			self.bets[suit] = []

		self.top_card = {}
		for suit in Suit:
			self.top_card[suit] = None

		self.players = players
		self.turn = 2 # {0, 1, 2}. game starts on player 2 for some reason		
		self.removed_suits = []
		self.killed_suit = None # suit of monkey currently being removed

		self.state = State.TURN_POPUP
		self.wait_time = Wait.TURN_POPUP.value

		self.hovered_bet = None
		self.hovered_card = None
		self.pointer = False
		self.mouse_coords = {'x':  -1, 'y': -1}
		self.mouse_click = False
		self.return_state = None # state to return to after visiting settings menu
		self.music_on = False

		# intialize the boundary boxes for selecting bets
		self.bet_boundaries = {}
		x_cord = COLUMN_LEFT
		for suit in Suit:
			self.bet_boundaries[suit] = {
				"left"  : x_cord,
				"right" : x_cord + BET_BOX_WIDTH,
				"top"   : BET_BOX_TOP,
				"bottom": BET_BOX_TOP + BET_BOX_WIDTH,
			}
			x_cord += COLUMN_SPACING

		# intialize the boundary boxes for selecting cards
		self.card_boundaries = {}
		x_cord = PLAYER_FIRST_CARD_LEFT
		for i in range(5): # 5 cards
			self.card_boundaries[i] = {
				"left"  : x_cord,
				"right" : x_cord + CARD_SIZE[0],
				"top"   : PLAYER_FIRST_CARD_TOP,
				"bottom": PLAYER_FIRST_CARD_TOP + CARD_SIZE[1],
			}
			x_cord += COLUMN_SPACING

		self.reset()
	

	def lowest_suit(self):
		top_card_list = [c for c in self.top_card.values() if c]
		if len(top_card_list) > 0:
			top_card_list.sort(key=lambda x: x.value)
			return top_card_list[0].suit
		return None


	def reset(self):
		# figure out which suit is to be removed
		lowest_suit = self.lowest_suit()
		if lowest_suit:
			self.removed_suits.append(lowest_suit)

		# place cards that were top cards back in the deck
		for suit in Suit:
			if self.top_card[suit]:
				self.deck.append(self.top_card[suit])
			self.top_card[suit] = None

		# remove removed-suit cards from the deck
		self.deck = [c for c in self.deck if c.suit not in self.removed_suits]

		# remove removed-suit cards from players' hands
		for player in self.players:
			player.hand = [c for c in player.hand if c.suit not in self.removed_suits]

		# fill now-empty card slots in players' hands
		for player in self.players:
			cards = random.sample(self.deck, 5 - len(player.hand))
			player.hand.extend(cards)
			self.deck = [c for c in self.deck if c not in player.hand] # remove these cards from dealer deck

		# remove the bets under the removed suit for player score
		for suit in self.removed_suits:
			for bet in self.bets[suit]:
				for player in self.players:
					if bet == player.fruit:
						player.score -= 1
			self.bets[suit] = []


	# returns True/False whether or not there are at least three bets on the board
	def three_bets(self):
		return sum([len(self.bets[suit]) for suit in Suit]) > 3


	# return's lowest monkey if the round is complete
	def round_complete(self):
		top_card_list = [c for c in self.top_card.values() if c]
		full_cards = (len(top_card_list) == 6 - len(self.removed_suits))

		if full_cards:
			top_card_list.sort(key=lambda x: x.value)
			if top_card_list[0].value != top_card_list[1].value: # no tie
				return True

		return False


	def game_complete(self):
		return len(self.removed_suits) == 3


	def final_scores(self):
		sorted_players = self.players
		sorted_players.sort(key=lambda x: x.score, reverse=True)
		return sorted_players


	# grab a single card after a card is played
	def get_card(self, player):
		if len(self.deck) == 0:
			return

		choice = random.choice(self.deck)
		if choice:
			self.deck.remove(choice)
			player.hand.append(choice)


	def next_turn(self):
		self.turn = (self.turn + 1) % 3
		return self.players[self.turn]


	def bet_boxes_full(self):
		return all([len(self.bets[suit]) == 4 for suit in Suit if suit not in self.removed_suits])

	def get_hovered_bet(self):
		for suit in Suit:
			if suit not in self.removed_suits and len(self.bets[suit]) < 4:
				bound = self.bet_boundaries[suit]
				if bound["left"] <= self.mouse_coords['x'] <= bound["right"] and bound["top"] <= self.mouse_coords['y'] <= bound["bottom"]:
					return suit

		return None


	def handle_bet_selection(self):

		player = self.players[self.turn]
		choice = None

		if player.is_human: # Human player's turn
			new_hovered = self.get_hovered_bet()
			if new_hovered != self.hovered_bet:
				self.hovered_bet = new_hovered

			if self.mouse_click and self.hovered_bet:
				choice = self.hovered_bet
				self.hovered_bet = None


		else: # computer's turn
			# Place a bet at random
			available = [suit for suit in self.bets if suit not in self.removed_suits and len(self.bets[suit]) < 4] # find spots with < 4 bets
			choice = random.choice(available)

		if choice:
			self.bets[choice].append(player.fruit)
			player.score += 1
		
		return choice


	def get_hovered_card(self):
		hand = self.players[self.turn].hand

		for i in range(len(hand)):
			if hand[i]:
				bound = self.card_boundaries[i]
				if bound["left"] <= self.mouse_coords['x'] <= bound["right"] and bound["top"] <= self.mouse_coords['y'] <= bound["bottom"]:
					return hand[i]

		return None


	def handle_card_selection(self):
		player = self.players[self.turn]
		choice = None

		if player.is_human:

			self.hovered_card = self.get_hovered_card()

			if self.mouse_click and self.hovered_card:
				choice = self.hovered_card
				self.hovered_card = None
							
		else: # computer's turn
			choice = random.choice(player.hand)

		if choice:
			# return previous top card to the deck
			if self.top_card[choice.suit]:
				# make it a "?" again if it was before
				if self.top_card[choice.suit].is_q:
					self.top_card[choice.suit].rank = "q"
					self.top_card[choice.suit].value = 0

				self.deck.append(self.top_card[choice.suit])

			# if the card is '?' assign it a value
			if choice.rank == 'q':
				new_val = random.randint(1,7)
				choice.rank = str(new_val)
				choice.value = new_val

			self.top_card[choice.suit] = choice
			player.hand.remove(choice)
			self.get_card(player)

		return choice


	def __repr__(self):
		return ""

			