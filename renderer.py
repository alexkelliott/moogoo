import pygame
import os
from enums import Fruit, Suit

# positional constants
DEALER_LEFT = 10
DEALER_TOP = 60
SCORE_BAY_FRUIT_TOP = 322
BET_BOX_TOP = 150
BET_OFFSET = 2
BET_BOX_WIDTH = 80
CARD_BAY_TOP = 240
CARD_SIZE = (80, 106)
PLAYER_FIRST_CARD_TOP = 360
PLAYER_FIRST_CARD_LEFT = 175
COLUMN_LEFT = 125
COLUMN_SPACING = 100

WHITE = (255, 255, 255)
DARK_GREEN = (0, 104, 76)

class Renderer():
	def __init__(self, surface):
		self.surface = surface
		self.font1 = pygame.font.Font(os.path.join('assets', 'fonts', '8bitOperatorPlus-Regular.ttf'), 28)
		self.hovered_bet = None # consider moving this to board
		self.hovered_card = None # consider moving this to board
		self.top_text = ""

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


	def render(self, board):
		# mouse
		if self.hovered_bet or self.hovered_card:
			pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
		else:
			pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

		# background
		background = pygame.image.load(os.path.join('assets', 'images', 'background.png'))
		self.surface.blit(background, (0,0))

		# top text
		text1 = self.font1.render(self.top_text, True, WHITE)
		text_rect = text1.get_rect(center=(self.surface.get_width() / 2, 30))
		self.surface.blit(text1, text_rect)

		# dealer
		dealer = pygame.image.load(os.path.join('assets', 'images', 'dealer.png'))
		self.surface.blit(dealer, (DEALER_LEFT, DEALER_TOP))

		# monkeys
		x_cord = COLUMN_LEFT
		for suit in Suit:
			if suit not in board.removed_suits:
				monkey = pygame.image.load(os.path.join('assets', 'images', "monkeys", suit.value+".png"))
				self.surface.blit(monkey, (x_cord, DEALER_TOP))
			x_cord += COLUMN_SPACING

		# bet box hover
		x_cord = COLUMN_LEFT
		for suit in Suit:
			if suit not in board.removed_suits:
				if suit == self.hovered_bet:
					for coords in [(x_cord, BET_BOX_TOP), (x_cord + 42, BET_BOX_TOP), (x_cord, BET_BOX_TOP + 42), (x_cord + 42, BET_BOX_TOP + 42)]:
						bet_box = pygame.image.load(os.path.join('assets', 'images', "bet_box_hover.png"))
						self.surface.blit(bet_box, coords)
			x_cord += COLUMN_SPACING

		# bets
		x_cord = COLUMN_LEFT
		for suit in Suit:
			if suit not in board.removed_suits:
				coords = [(x_cord + BET_OFFSET, BET_BOX_TOP + BET_OFFSET), (x_cord + 42 + BET_OFFSET, BET_BOX_TOP + BET_OFFSET), (x_cord + BET_OFFSET, BET_BOX_TOP + 42 + BET_OFFSET), (x_cord + 42 + BET_OFFSET, BET_BOX_TOP + 42 + BET_OFFSET)]

				for i in range(len(board.bets[suit])):
					filename = board.bets[suit][i].value + ".png"
					fruit = pygame.image.load(os.path.join('assets', 'images', 'fruits', filename))
					self.surface.blit(fruit, coords[i])
			x_cord += COLUMN_SPACING

		# top cards
		x_cord = COLUMN_LEFT
		for card in board.top_card.values():
			if card and card.suit not in board.removed_suits:
				card_img = pygame.image.load(os.path.join('assets', 'images', "cards", card.get_filename()))
				self.surface.blit(card_img, (x_cord, CARD_BAY_TOP))
			x_cord += COLUMN_SPACING

		# "score" text
		txt1 = self.font1.render("Score", True, WHITE)
		self.surface.blit(txt1, (DEALER_LEFT + 10, SCORE_BAY_FRUIT_TOP - 45))

		# score fruit + number
		y_cord = SCORE_BAY_FRUIT_TOP
		for fruit in Fruit:
			fruit_img = pygame.image.load(os.path.join('assets', 'images', 'fruits', fruit.value+".png"))
			self.surface.blit(fruit_img, (DEALER_LEFT + 2, y_cord + 2))

			for player in board.players:
				if player.fruit == fruit:
					score = self.font1.render(str(player.score), True, WHITE)

					# top text
					text_rect = score.get_rect(center=(DEALER_LEFT + 70, y_cord + 18))
					self.surface.blit(score, text_rect)

			y_cord += 40

		# player's cards
		if board.three_bets():
			x_cord = PLAYER_FIRST_CARD_LEFT

			for card in board.players[0].hand:
				player_card = pygame.image.load(os.path.join('assets', 'images', "cards", card.get_filename()))
				self.surface.blit(player_card, (x_cord, PLAYER_FIRST_CARD_TOP))

				if card == self.hovered_card:
					card_hover = pygame.image.load(os.path.join('assets', 'images', "card_hover.png"))
					self.surface.blit(card_hover, (x_cord, PLAYER_FIRST_CARD_TOP))

				x_cord += COLUMN_SPACING

		pygame.display.flip()


	def player_turn_popup(self, player):
		string = "     " + player.name + "'s turn" # space at front to keep box centered when fruit image is added

		# text
		text1 = self.font1.render(string, True, WHITE)
		text_rect = text1.get_rect(center=(self.surface.get_width() / 2, self.surface.get_height() / 2))

		# fruit image
		filename = player.fruit.value + ".png"
		fruit_img = pygame.image.load(os.path.join('assets', 'images', 'fruits', filename))
		
		# draw elements on screen
		background = pygame.draw.rect(self.surface, DARK_GREEN, pygame.Rect(text_rect.x-10, text_rect.y-5, text_rect.w+20, text_rect.h+10))
		self.surface.blit(fruit_img, (text_rect.x+5, text_rect.y))
		self.surface.blit(text1, text_rect)
		pygame.display.flip()


	def game_over_screen(self, players):
		# Dark green background
		background = pygame.draw.rect(self.surface, DARK_GREEN, pygame.Rect(75, 170, 570, 140))

		# Text
		words = [" wins", " is second", " is third"]
		y_offset = [-40, 0, 40]
		for i in range(len(players)):
			string = players[i].name + words[i] + " with " + str(players[i].score)
			text1 = self.font1.render(string, True, WHITE)
			text_rect = text1.get_rect(center=(self.surface.get_width() / 2, (self.surface.get_height() / 2) + y_offset[i]))
			self.surface.blit(text1, text_rect)

		pygame.display.flip()


