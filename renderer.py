import pygame
import os
from constants import *
from enums import Fruit, Suit, State

pygame.display.set_caption('Moogoo Monkey')
screen_height = 480
screen_width = 720

class Renderer():
	def __init__(self):
		self.surface = pygame.display.set_mode((screen_width, screen_height))

		self.assets = {'fonts' : {}, 'images': {'monkeys': {}, 'fruits': {}, 'cards': {}}}
		self.assets['fonts']['font1'] = pygame.font.Font(os.path.join('assets', 'fonts', '8bitOperatorPlus-Regular.ttf'), 28)
		self.assets['images']['background'] = pygame.image.load(os.path.join('assets', 'images', 'background.png'))
		self.assets['images']['cog'] = pygame.image.load(os.path.join('assets', 'images', 'cog.png'))
		self.assets['images']['dealer'] = pygame.image.load(os.path.join('assets', 'images', 'dealer.png'))
		for suit in Suit:
			self.assets['images']['monkeys'][suit.value] = pygame.image.load(os.path.join('assets', 'images', 'monkeys', suit.value + '.png'))
		self.assets['images']['red_x'] = pygame.image.load(os.path.join('assets', 'images', 'redx.png'))
		self.assets['images']['bet_box_hover'] = pygame.image.load(os.path.join('assets', 'images', 'bet_box_hover.png'))
		for fruit in Fruit:
			self.assets['images']['fruits'][fruit.value] = pygame.image.load(os.path.join('assets', 'images', 'fruits', fruit.value + '.png'))
		for suit in Suit:
			for value in range(8):
				rank = 'q' if value == 0 else str(value)
				self.assets['images']['cards'][suit.value + rank] = pygame.image.load(os.path.join('assets', 'images', 'cards', suit.value + rank + '.png')) 
		self.assets['images']['card_hover'] = pygame.image.load(os.path.join('assets', 'images', 'card_hover.png'))


	def render(self, game_state):
		self.draw_board(game_state)
		if game_state.state == State.TURN_POPUP:
			self.turn_popup(game_state.board.players[game_state.board.turn])
		elif game_state.state == State.GAME_OVER_SCREEN:
			self.game_over_screen(game_state.board.final_scores())
		elif game_state.state == State.SETTINGS:
			self.settings_screen(game_state)
		pygame.display.flip()


	def draw_board(self, game_state):
		board = game_state.board

		# mouse
		if game_state.hovered_bet or game_state.hovered_card or game_state.pointer:
			pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
		else:
			pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

		# background
		self.surface.blit(self.assets['images']['background'], (0,0))

		# settings button
		self.surface.blit(self.assets['images']['cog'], (SETTINGS_BUTTON_LEFT, SETTINGS_BUTTON_TOP))

		# top text
		top_text = ""
		if game_state.state in [State.TURN_POPUP, State.PRE_BET, State.BET]:
			top_text = "Place a bet"
		elif game_state.state in [State.PRE_CARD_SELECTION, State.CARD_SELECTION, State.POST_CARD_SELECTION, State.ROUND_ENDED]:
			top_text = "Play a card"
		elif game_state.state == State.GAME_OVER_SCREEN:
			top_text = "Game over"

		text1 = self.assets['fonts']['font1'].render(top_text, True, WHITE)
		text_rect = text1.get_rect(center=(self.surface.get_width() / 2, 30))
		self.surface.blit(text1, text_rect)

		# dealer
		self.surface.blit(self.assets['images']['dealer'], (DEALER_LEFT, DEALER_TOP))

		# monkeys
		x_cord = COLUMN_LEFT
		for suit in Suit:
			# monkey image
			if suit not in board.removed_suits:
				self.surface.blit(self.assets['images']['monkeys'][suit.value], (x_cord, DEALER_TOP))
			# red x over monkey if being removed
			if game_state.state == State.ROUND_ENDED and suit == board.lowest_suit():
				if game_state.wait_time % 30 >= 15: # make it blink
					self.surface.blit(self.assets['images']['red_x'], (x_cord, DEALER_TOP))

			x_cord += COLUMN_SPACING

		# bet box hover
		x_cord = COLUMN_LEFT
		for suit in Suit:
			if suit not in board.removed_suits:
				if suit == game_state.hovered_bet:
					for coords in [(x_cord, BET_BOX_TOP), (x_cord + 42, BET_BOX_TOP), (x_cord, BET_BOX_TOP + 42), (x_cord + 42, BET_BOX_TOP + 42)]:
						self.surface.blit(self.assets['images']['bet_box_hover'], coords)
			x_cord += COLUMN_SPACING

		# bets
		x_cord = COLUMN_LEFT
		for suit in Suit:
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

				if card == game_state.hovered_card:
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


	def settings_screen(self, game_state):
		pygame.draw.rect(self.surface, DARK_GREEN, pygame.Rect(100, 100, 520, 280))

		# settings text
		text1 = self.assets['fonts']['font1'].render("Settings", True, WHITE)
		text_rect = text1.get_rect(center=(self.surface.get_width() / 2, 120))
		self.surface.blit(text1, text_rect)

		# music button
		pygame.draw.rect(self.surface, WHITE, pygame.Rect(MUSIC_BUTTON_LEFT, MUSIC_BUTTON_TOP, MUSIC_BUTTON_WIDTH, MUSIC_BUTTON_WIDTH))
		if game_state.music_on:
			pygame.draw.rect(self.surface, BLACK, pygame.Rect(MUSIC_BUTTON_LEFT+2, MUSIC_BUTTON_TOP+2, MUSIC_BUTTON_WIDTH-4, MUSIC_BUTTON_WIDTH-4))

		# music text
		text2 = self.assets['fonts']['font1'].render("Music", True, WHITE)
		self.surface.blit(text2, (115, 135))

		# volume text
		text2 = self.assets['fonts']['font1'].render("Volume", True, WHITE)
		self.surface.blit(text2, (115, 175))

		# volume slider bar
		pygame.draw.rect(self.surface, WHITE, pygame.Rect(VOL_SLIDER_LEFT, VOL_SLIDER_TOP, VOL_SLIDER_WIDTH, VOL_SLIDER_HEIGHT))

		# volume slider handle
		left_pos = VOL_SLIDER_LEFT + game_state.volume * (VOL_SLIDER_WIDTH)
		pygame.draw.rect(self.surface, WHITE, pygame.Rect(left_pos, 190, 10, 25))

		# done button
		pygame.draw.rect(self.surface, WHITE, pygame.Rect(EXIT_SETTINGS_BUTTON_LEFT, EXIT_SETTINGS_BUTTON_TOP, EXIT_SETTINGS_BUTTON_WIDTH, EXIT_SETTINGS_BUTTON_HEIGHT))
		text3 = self.assets['fonts']['font1'].render("Done", True, BLACK)
		text_rect = text3.get_rect(center=(EXIT_SETTINGS_BUTTON_LEFT+EXIT_SETTINGS_BUTTON_WIDTH/2, (EXIT_SETTINGS_BUTTON_TOP+EXIT_SETTINGS_BUTTON_HEIGHT/2)))
		self.surface.blit(text3, text_rect)


