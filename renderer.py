import pygame
import os
from suit import Suit
from fruit import Fruit

# positional constants
DEALER_LEFT = 10
DEALER_TOP = 60
SCORE_BAY_TOP = 275
BET_BOX_TOP = 150
BET_OFFSET = 2
CARD_BAY_TOP = 240
PLAYER_HAND_TOP = 355
PLAYER_HAND_LEFT = 165
COLUMN_LEFT = 125
COLUMN_SPACING = 100

WHITE = (255, 255, 255)

class Renderer():
	def __init__(self, surface):
		self.surface = surface
		self.font1 = pygame.font.Font(os.path.join('fonts', '8bitOperatorPlus-Regular.ttf'), 28)

	def render(self, board):
		# background
		background = pygame.image.load(os.path.join('images', 'greenbackdrop.png'))
		self.surface.blit(background, (0,0))

		# dealer
		dealer = pygame.image.load(os.path.join('images', 'dealer.png'))
		self.surface.blit(dealer, (DEALER_LEFT, DEALER_TOP))

		# monkeys
		x_cord = COLUMN_LEFT
		for suit in Suit:
		    monkey = pygame.image.load(os.path.join('images', "monkeys", suit.value+".png"))
		    self.surface.blit(monkey, (x_cord, DEALER_TOP))
		    x_cord += COLUMN_SPACING

		# bet boxes
		x_cord = COLUMN_LEFT
		for suit in Suit:
		    for coords in [(x_cord, BET_BOX_TOP), (x_cord + 42, BET_BOX_TOP), (x_cord, BET_BOX_TOP + 42), (x_cord + 42, BET_BOX_TOP + 42)]:
		        bet_box = pygame.image.load(os.path.join('images', "bet_box.png"))
		        self.surface.blit(bet_box, coords)
		    x_cord += COLUMN_SPACING

		# bets
		x_cord = COLUMN_LEFT
		for suit in Suit:
			coords = [(x_cord + BET_OFFSET, BET_BOX_TOP + BET_OFFSET), (x_cord + 42 + BET_OFFSET, BET_BOX_TOP + BET_OFFSET), (x_cord + BET_OFFSET, BET_BOX_TOP + 42 + BET_OFFSET), (x_cord + 42 + BET_OFFSET, BET_BOX_TOP + 42 + BET_OFFSET)]

			for i in range(len(board.bets[suit])):
				filename = board.bets[suit][i].value + "fruit.png"
				fruit = pygame.image.load(os.path.join('images', filename))
				self.surface.blit(fruit, coords[i])

			x_cord += COLUMN_SPACING

		# card bays
		x_cord = COLUMN_LEFT
		for suit in Suit:
		    card_bay = pygame.image.load(os.path.join('images', "card_bay.png"))
		    self.surface.blit(card_bay, (x_cord, CARD_BAY_TOP))
		    x_cord += COLUMN_SPACING

		# top cards
		x_cord = COLUMN_LEFT
		for card in board.top_card.values():
			if card:
				card_img = pygame.image.load(os.path.join('images', "cards", card.filename))
				self.surface.blit(card_img, (x_cord, CARD_BAY_TOP))
			x_cord += COLUMN_SPACING

		# score bay
		score_bay = pygame.image.load(os.path.join('images', "score_bay.png"))
		self.surface.blit(score_bay, (DEALER_LEFT, SCORE_BAY_TOP))

		# score text
		txt1 = self.font1.render("Score", True, WHITE)
		self.surface.blit(txt1, (DEALER_LEFT + 10, SCORE_BAY_TOP))

		y_cord = SCORE_BAY_TOP + 35
		for fruit in Fruit:
			fruit_img = pygame.image.load(os.path.join('images', fruit.value+"fruit.png"))
			self.surface.blit(fruit_img, (DEALER_LEFT + 5, y_cord))

			for player in board.players:
				if player.fruit == fruit:
					score = self.font1.render(str(player.score), True, WHITE)
					self.surface.blit(score, (DEALER_LEFT + 55, y_cord + 2))

			y_cord += 45

		# player hand
		player_hand = pygame.image.load(os.path.join('images', "player_hand.png"))
		self.surface.blit(player_hand, (PLAYER_HAND_LEFT, PLAYER_HAND_TOP))

		# player's cards
		x_cord = PLAYER_HAND_LEFT + 10
		for card in board.players[0].hand:
			player_card = pygame.image.load(os.path.join('images', "cards", card.filename))
			self.surface.blit(player_card, (x_cord, PLAYER_HAND_TOP + 5))
			x_cord += COLUMN_SPACING

		pygame.display.flip()
