import pygame
import os
from constants import *
from enums import Fruit, Suit, State


class Renderer():
	def __init__(self, surface):
		self.surface = surface

		self.assets = {'fonts' : {}, 'images': {'monkeys': {}, 'fruits': {}, 'cards': {}}}
		self.assets['fonts']['font1'] = pygame.font.Font(os.path.join('assets', 'fonts', '8bitOperatorPlus-Regular.ttf'), 28)
		self.assets['images']['background'] = pygame.image.load(os.path.join('assets', 'images', 'background.png'))
		self.assets['images']['dealer'] = pygame.image.load(os.path.join('assets', 'images', 'dealer.png'))
		for suit in Suit:
			self.assets['images']['monkeys'][suit.value] = pygame.image.load(os.path.join('assets', 'images', 'monkeys', suit.value+'.png'))
		self.assets['images']['bet_box_hover'] = pygame.image.load(os.path.join('assets', 'images', 'bet_box_hover.png'))
		for fruit in Fruit:
			self.assets['images']['fruits'][fruit.value] = pygame.image.load(os.path.join('assets', 'images', 'fruits', fruit.value + '.png'))
		for suit in Suit:
			for value in range(8):
				rank = 'q' if value == 0 else str(value)
				self.assets['images']['cards'][suit.value + rank] = pygame.image.load(os.path.join('assets', 'images', 'cards', suit.value + rank + '.png')) 
		self.assets['images']['card_hover'] = pygame.image.load(os.path.join('assets', 'images', 'card_hover.png'))


	def render(self, board):
		self.draw_board(board)
		if board.state == State.TURN_POPUP:
			self.turn_popup(board.players[board.turn])
		elif board.state == State.GAME_OVER_SCREEN:
			self.game_over_screen(board.final_scores())
		pygame.display.flip()


	def draw_board(self, board):
		# mouse
		if board.hovered_bet or board.hovered_card:
			pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
		else:
			pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

		# background
		self.surface.blit(self.assets['images']['background'], (0,0))

		# top text
		top_text = ""
		if board.state in [State.TURN_POPUP, State.PRE_BET, State.BET]:
			top_text = "Place a bet"
		elif board.state in [State.PRE_CARD_SELECTION, State.CARD_SELECTION]:
			top_text = "Play a card"
		elif board.state == State.GAME_OVER_SCREEN:
			top_text = "Game over"

		text1 = self.assets['fonts']['font1'].render(top_text, True, WHITE)
		text_rect = text1.get_rect(center=(self.surface.get_width() / 2, 30))
		self.surface.blit(text1, text_rect)

		# dealer
		self.surface.blit(self.assets['images']['dealer'], (DEALER_LEFT, DEALER_TOP))

		# monkeys
		x_cord = COLUMN_LEFT
		for suit in Suit:
			if suit not in board.removed_suits:
				self.surface.blit(self.assets['images']['monkeys'][suit.value], (x_cord, DEALER_TOP))
			x_cord += COLUMN_SPACING

		# bet box hover
		x_cord = COLUMN_LEFT
		for suit in Suit:
			if suit not in board.removed_suits:
				if suit == board.hovered_bet:
					for coords in [(x_cord, BET_BOX_TOP), (x_cord + 42, BET_BOX_TOP), (x_cord, BET_BOX_TOP + 42), (x_cord + 42, BET_BOX_TOP + 42)]:
						self.surface.blit(self.assets['images']['bet_box_hover'], coords)
			x_cord += COLUMN_SPACING

		# bets
		x_cord = COLUMN_LEFT
		for suit in Suit:
			if suit not in board.removed_suits:
				coords = [(x_cord + BET_OFFSET, BET_BOX_TOP + BET_OFFSET), (x_cord + 42 + BET_OFFSET, BET_BOX_TOP + BET_OFFSET), (x_cord + BET_OFFSET, BET_BOX_TOP + 42 + BET_OFFSET), (x_cord + 42 + BET_OFFSET, BET_BOX_TOP + 42 + BET_OFFSET)]

				for i in range(len(board.bets[suit])):
					self.surface.blit(self.assets['images']['fruits'][board.bets[suit][i].value], coords[i])
			x_cord += COLUMN_SPACING

		# top cards
		x_cord = COLUMN_LEFT
		for card in board.top_card.values():
			if card and card.suit not in board.removed_suits:
				self.surface.blit(self.assets['images']['cards'][card.suit.value + card.rank], (x_cord, CARD_BAY_TOP))
			x_cord += COLUMN_SPACING

		# "score" text
		txt1 = self.assets['fonts']['font1'].render("Score", True, WHITE)
		self.surface.blit(txt1, (DEALER_LEFT + 10, SCORE_BAY_FRUIT_TOP - 45))

		# score fruit + number
		y_cord = SCORE_BAY_FRUIT_TOP
		for fruit in Fruit:
			self.surface.blit(self.assets['images']['fruits'][fruit.value], (DEALER_LEFT + 2, y_cord + 2))
			for player in board.players:
				if player.fruit == fruit:
					score = self.assets['fonts']['font1'].render(str(player.score), True, WHITE)

					# top text
					text_rect = score.get_rect(center=(DEALER_LEFT + 70, y_cord + 18))
					self.surface.blit(score, text_rect)

			y_cord += 40

		# player's cards
		if board.three_bets():
			x_cord = PLAYER_FIRST_CARD_LEFT

			for card in board.players[0].hand:
				self.surface.blit(self.assets['images']['cards'][card.suit.value + card.rank], (x_cord, PLAYER_FIRST_CARD_TOP))

				if card == board.hovered_card:
					self.surface.blit(self.assets['images']['card_hover'], (x_cord, PLAYER_FIRST_CARD_TOP))

				x_cord += COLUMN_SPACING


	def turn_popup(self, player):
		string = "     " + player.name + "'s turn" # space at front to keep box centered when fruit image is added

		# text
		text1 = self.assets['fonts']['font1'].render(string, True, WHITE)
		text_rect = text1.get_rect(center=(self.surface.get_width() / 2, self.surface.get_height() / 2))
		
		# draw elements on screen
		background = pygame.draw.rect(self.surface, DARK_GREEN, pygame.Rect(text_rect.x-10, text_rect.y-5, text_rect.w+20, text_rect.h+10))
		self.surface.blit(self.assets['images']['fruits'][player.fruit.value], (text_rect.x+5, text_rect.y))
		self.surface.blit(text1, text_rect)


	def game_over_screen(self, players):
		# Dark green background
		background = pygame.draw.rect(self.surface, DARK_GREEN, pygame.Rect(75, 170, 570, 140))

		# Text
		words = [" wins", " is second", " is third"]
		y_offset = [-40, 0, 40]
		for i in range(len(players)):
			string = players[i].name + words[i] + " with " + str(players[i].score)
			text1 = self.assets['fonts']['font1'].render(string, True, WHITE)
			text_rect = text1.get_rect(center=(self.surface.get_width() / 2, (self.surface.get_height() / 2) + y_offset[i]))
			self.surface.blit(text1, text_rect)