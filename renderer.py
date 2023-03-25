import pygame
from pygame.surface import Surface
import os

from constants import *
from enums import Fruit, Suit, State

pygame.display.set_caption('Moogoo Monkey')
screen_height: int = 480
screen_width: int = 720


class Renderer():
	def __init__(self) -> None:
		self.debug: bool = False
		self.debug_message: str = ""

		self.surface: Surface = pygame.display.set_mode((screen_width, screen_height))

		self.assets: dict[str, dict[str, ...]] = {'fonts' : {}, 'images': {'monkeys': {}, 'fruits': {}, 'cards': {}}}
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


	def render(self, game_state) -> None:
		# mouse
		if game_state.hovered_bet or game_state.hovered_card or game_state.pointer:
			pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
		else:
			pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

		if game_state.state == State.CONNECT:
			# Screen showing server selection
			self.connect_screen(game_state)
		elif game_state.state == State.LOBBY:
			# Screen showing lobby
			self.lobby_screen(game_state)
		else:
			# Actual gameplay
			self.draw_board(game_state)

			if game_state.state == State.TURN_POPUP:
				self.turn_popup(game_state.board.players[game_state.board.turn])
			elif game_state.state == State.GAME_OVER_SCREEN:
				self.game_over_screen(game_state.board.final_scores())

			if game_state.settings_open:
				self.settings_screen(game_state)


		if self.debug:
			self.show_debug()

		pygame.display.flip()


	def draw_board(self, game_state) -> None:
		board: 'Board' = game_state.board

		# background
		self.surface.blit(self.assets['images']['background'], (0,0))

		# settings button
		self.surface.blit(self.assets['images']['cog'], (SETTINGS_BUTTON_LEFT, SETTINGS_BUTTON_TOP))

		# top text
		top_text: str = ""
		if game_state.state in [State.TURN_POPUP, State.PRE_BET, State.BET]:
			top_text = "Place a bet"
		elif game_state.state in [State.PRE_CARD_SELECTION, State.CARD_SELECTION, State.POST_CARD_SELECTION, State.ROUND_ENDED]:
			top_text = "Play a card"
		elif game_state.state == State.GAME_OVER_SCREEN:
			top_text = "Game over"

		text1: Surface = self.assets['fonts']['font1'].render(top_text, True, WHITE)
		text_rect = text1.get_rect(center=(self.surface.get_width() / 2, 30))
		self.surface.blit(text1, text_rect)

		# dealer
		self.surface.blit(self.assets['images']['dealer'], (DEALER_LEFT, DEALER_TOP))

		# monkeys
		x_cord: int = COLUMN_LEFT
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
		txt1: pygame.surface.Surface = self.assets['fonts']['font1'].render("Score", True, WHITE)
		self.surface.blit(txt1, (DEALER_LEFT + 10, SCORE_BAY_FRUIT_TOP - 45))

		# score fruit + number
		y_cord: int = SCORE_BAY_FRUIT_TOP
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

			for card in board.players[game_state.player_turn_num].hand:
				self.surface.blit(self.assets['images']['cards'][card.suit.value + card.rank], (x_cord, PLAYER_FIRST_CARD_TOP))

				if card == game_state.hovered_card:
					self.surface.blit(self.assets['images']['card_hover'], (x_cord, PLAYER_FIRST_CARD_TOP))

				x_cord += COLUMN_SPACING


	def turn_popup(self, player) -> None:
		string: str = "     " + player.name + "'s turn" # space at front to keep box centered when fruit image is added

		# text
		text1: Surface = self.assets['fonts']['font1'].render(string, True, WHITE)
		text_rect = text1.get_rect(center=(self.surface.get_width() / 2, self.surface.get_height() / 2))
		
		# draw elements on screen
		background = pygame.draw.rect(self.surface, DARK_GREEN, pygame.Rect(text_rect.x-10, text_rect.y-5, text_rect.w+20, text_rect.h+10))
		self.surface.blit(self.assets['images']['fruits'][player.fruit.value], (text_rect.x+5, text_rect.y))
		self.surface.blit(text1, text_rect)


	def game_over_screen(self, players) -> None:
		# Dark green background
		background = pygame.draw.rect(self.surface, DARK_GREEN, pygame.Rect(75, 170, 570, 140))

		# Text
		words: list[str] = [" wins", " is second", " is third"]
		y_offset: list[int] = [-40, 0, 40]
		for i in range(len(players)):
			string: str = players[i].name + words[i] + " with " + str(players[i].score)
			text1: Surface = self.assets['fonts']['font1'].render(string, True, WHITE)
			text_rect = text1.get_rect(center=(self.surface.get_width() / 2, (self.surface.get_height() / 2) + y_offset[i]))
			self.surface.blit(text1, text_rect)


	def lobby_screen(self, game_state) -> None:
		pygame.draw.rect(self.surface, DARK_GREEN, pygame.Rect(0, 0, screen_width, screen_height))

		text1: Surface = self.assets['fonts']['font1'].render("Connected", True, WHITE)

		text_rect: pygame.Rect = text1.get_rect(center=(self.surface.get_width() / 2, 30))
		self.surface.blit(text1, text_rect)

		if len(game_state.team_mates):
			string: str = "Waiting for " + str(game_state.team_mates[0].name) + " to start the game"
			text5 = self.assets['fonts']['font1'].render(string, True, WHITE)
			self.surface.blit(text5, (50, 75))

		string: str = "Players: " + str(len(game_state.team_mates)) + "/3"
		text2: Surface = self.assets['fonts']['font1'].render(string, True, WHITE)
		self.surface.blit(text2, (50, 135))

		y_cord: int = 200
		for player in game_state.team_mates:
			# text
			text3: Surface = self.assets['fonts']['font1'].render(player.name, True, WHITE)
			self.surface.blit(text3, (125, y_cord))
			self.surface.blit(self.assets['images']['fruits'][player.fruit.value], (75, y_cord))

			y_cord += 50

		# only show the start game button to the lobby starter
		if game_state.player_turn_num == 0:
			# start game button
			pygame.draw.rect(self.surface, WHITE, pygame.Rect(LOBBY_CONNECT_BUTTON_LEFT, LOBBY_CONNECT_BUTTON_TOP, LOBBY_CONNECT_BUTTON_WIDTH, LOBBY_CONNECT_BUTTON_HEIGHT))
			text4: Surface = self.assets['fonts']['font1'].render("Start Game", True, BLACK)
			text_rect: pygame.Rect = text4.get_rect(center=(LOBBY_CONNECT_BUTTON_LEFT+LOBBY_CONNECT_BUTTON_WIDTH/2, (LOBBY_CONNECT_BUTTON_TOP+LOBBY_CONNECT_BUTTON_HEIGHT/2)))
			self.surface.blit(text4, text_rect)


	def connect_screen(self, game_state) -> None:
		pygame.draw.rect(self.surface, DARK_GREEN, pygame.Rect(0, 0, screen_width, screen_height))

		text0: Surface = self.assets['fonts']['font1'].render("Reading data from user_settings.json...", True, WHITE)
		self.surface.blit(text0, (10, 10))

		text1: Surface = self.assets['fonts']['font1'].render("Player Name:", True, WHITE)
		self.surface.blit(text1, (30, 70))
		text2: Surface = self.assets['fonts']['font1'].render(str(game_state.user_settings["player_name"]), True, WHITE)
		self.surface.blit(text2, (300, 70))

		text3: Surface = self.assets['fonts']['font1'].render("Server Details", True, WHITE)
		self.surface.blit(text3, (10, 150))

		text3: Surface = self.assets['fonts']['font1'].render("IP/HostName:", True, WHITE)
		self.surface.blit(text3, (30, 200))
		text4: Surface = self.assets['fonts']['font1'].render(str(game_state.user_settings["ip"]), True, WHITE)
		self.surface.blit(text4, (300, 200))
		text5: Surface = self.assets['fonts']['font1'].render("IP/Port:", True, WHITE)
		self.surface.blit(text5, (30, 250))
		text6: Surface = self.assets['fonts']['font1'].render(str(game_state.user_settings["port"]), True, WHITE)
		self.surface.blit(text6, (300, 250))

		# connect button
		pygame.draw.rect(self.surface, WHITE, pygame.Rect(LOBBY_CONNECT_BUTTON_LEFT, LOBBY_CONNECT_BUTTON_TOP, LOBBY_CONNECT_BUTTON_WIDTH, LOBBY_CONNECT_BUTTON_HEIGHT))
		text3: Surface = self.assets['fonts']['font1'].render("Connect", True, BLACK)
		text_rect: pygame.Rect = text3.get_rect(center=(LOBBY_CONNECT_BUTTON_LEFT+LOBBY_CONNECT_BUTTON_WIDTH/2, (LOBBY_CONNECT_BUTTON_TOP+LOBBY_CONNECT_BUTTON_HEIGHT/2)))
		self.surface.blit(text3, text_rect)


	def settings_screen(self, game_state) -> None:

		pygame.draw.rect(self.surface, DARK_GREEN, pygame.Rect(100, 100, 520, 280))

		# settings text
		text1: Surface = self.assets['fonts']['font1'].render("Settings", True, WHITE)
		text_rect: pygame.Rect = text1.get_rect(center=(self.surface.get_width() / 2, 120))
		self.surface.blit(text1, text_rect)

		# music button
		pygame.draw.rect(self.surface, WHITE, pygame.Rect(MUSIC_BUTTON_LEFT, MUSIC_BUTTON_TOP, MUSIC_BUTTON_WIDTH, MUSIC_BUTTON_WIDTH))
		if game_state.music_on:
			pygame.draw.rect(self.surface, BLACK, pygame.Rect(MUSIC_BUTTON_LEFT+2, MUSIC_BUTTON_TOP+2, MUSIC_BUTTON_WIDTH-4, MUSIC_BUTTON_WIDTH-4))

		# music text
		text1: Surface = self.assets['fonts']['font1'].render("Music", True, WHITE)
		self.surface.blit(text1, (115, 135))

		# volume text
		text2: Surface = self.assets['fonts']['font1'].render("Volume", True, WHITE)
		self.surface.blit(text2, (115, 175))

		# volume slider bar
		pygame.draw.rect(self.surface, WHITE, pygame.Rect(VOL_SLIDER_LEFT, VOL_SLIDER_TOP, VOL_SLIDER_WIDTH, VOL_SLIDER_HEIGHT))

		# volume slider handle
		left_pos: int = VOL_SLIDER_LEFT + game_state.volume * (VOL_SLIDER_WIDTH)
		pygame.draw.rect(self.surface, WHITE, pygame.Rect(left_pos, 190, 10, 25))

		# done button
		pygame.draw.rect(self.surface, WHITE, pygame.Rect(EXIT_SETTINGS_BUTTON_LEFT, EXIT_SETTINGS_BUTTON_TOP, EXIT_SETTINGS_BUTTON_WIDTH, EXIT_SETTINGS_BUTTON_HEIGHT))
		text3: Surface = self.assets['fonts']['font1'].render("Done", True, BLACK)
		text_rect: pyagme.Rect = text3.get_rect(center=(EXIT_SETTINGS_BUTTON_LEFT+EXIT_SETTINGS_BUTTON_WIDTH/2, (EXIT_SETTINGS_BUTTON_TOP+EXIT_SETTINGS_BUTTON_HEIGHT/2)))
		self.surface.blit(text3, text_rect)


	def show_debug(self) -> None:
		text2: Surface = self.assets['fonts']['font1'].render(str(self.debug_message), True, WHITE)
		self.surface.blit(text2, (120, 440))