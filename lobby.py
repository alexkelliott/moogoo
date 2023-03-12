import random
import pickle
import sys # temporary

from game_state import Game_State
from board import Board
from enums import Fruit, State, Wait
from player import Player

nameChoices = ["Ava Cadavra", "Misty Waters", "Daddy Bigbucks", "Giuseppi Mezzoalto", "Dusty Hogg", "Phoebe Twiddle", "Luthor L. Bigbucks", "Lottie Cash", "Detective Dan D. Mann", "Pritchard Locksley", "Futo Maki", "Ephram Earl", "Lily Gates", "Cannonball Coleman", "Sue Pirmova", "Lincoln Broadsheet", "Crawdad Clem", "Bayou Boo", "Maximillian Moore", "Bucki Brock", "Berkeley Clodd", "Gramma Hattie", "Pepper Pete", "Dr. Mauricio Keys", "Olde Salty", "Lloyd", "Harlan King", "Daschell Swank", "Kris Thristle"]

class Client():
	def __init__(self):
		pass

class Lobby():

	def __init__(self, sock):
		self.client_socket = sock
		self.game_state = Game_State(server=True)
		self.game_state.wait_time = Wait.TURN_POPUP.value
		self.started = False
		# init state
		# self.state = State.TURN_POPUP
		# self.wait_time = Wait.TURN_POPUP.value

		print("Created lobby")


	def update_clients(self):
		# for conn in self.client_sockets:
		# 	conn.send(pickle.dumps(self.game_state))
		# self.client_socket.send(pickle.dumps(self.game_state))

		HEADERSIZE = 10

		if self.client_socket:

			msg = pickle.dumps(self.game_state)
			msg = bytes(f"{len(msg):<{HEADERSIZE}}", 'utf-8')+msg
			# print("sending:", msg)
			self.client_socket.send(msg)
			print("Sent game state")

			# self.client_socket.send(pickle.dumps(self.game_state))
			# self.client_socket.sendall(b"I hope this works")
		else:
			print("failed to send")


	def listen_for_update(self):
		raw_board = self.client_sockets[0].recv(4096)
		print("server received:", raw_board)

		# rec_game_state = pickle.loads(raw_board)
		print("updated")


	def update_game(self):

		board = self.game_state.board

		print(self.game_state.state, '\t', self.game_state.wait_time, '\t', board.players[board.turn].name)

		# TURN_POPUP => PRE_BET, BET
		if self.game_state.state == State.TURN_POPUP and self.game_state.wait_time == 0:
			if board.players[board.turn].is_human:
				if board.bet_boxes_full():
					self.game_state.state = State.CARD_SELECTION
				else:
					self.game_state.state = State.BET
			else: # npc
				if board.bet_boxes_full():
					self.game_state.state = State.PRE_CARD_SELECTION
					self.game_state.wait_time = Wait.PRE_CARD_SELECTION.value
				else:
					self.game_state.state = State.PRE_BET
					self.game_state.wait_time = Wait.PRE_BET.value

			self.update_clients()

		# PRE_BET => BET
		elif self.game_state.state == State.PRE_BET and self.game_state.wait_time == 0:
			self.game_state.state = State.BET
			self.update_clients()

		# BET => PRE_CARD_SELECTION, CARD_SELECTION, TURN_POPUP
		elif self.game_state.state == State.BET:
			if board.players[board.turn].is_human:
				# wait for the player to play
				# if board.three_bets():
				# 	self.game_state.state = State.CARD_SELECTION
				# else:
				# 	board.next_turn()
				# 	self.game_state.state = State.TURN_POPUP
				# 	self.game_state.wait_time = Wait.TURN_POPUP.value
				pass
			else:
				if board.handle_bet_selection():
					if board.three_bets():
						self.game_state.state = State.PRE_CARD_SELECTION
						self.game_state.wait_time = Wait.TURN_POPUP.value
					else:
						board.next_turn()
						self.game_state.state = State.TURN_POPUP
						self.game_state.wait_time = Wait.TURN_POPUP.value

			self.update_clients()
			# self.listen_for_update()

		# PRE_CARD_SELECTION => CARD_SELECTION 
		elif self.game_state.state == State.PRE_CARD_SELECTION and self.game_state.wait_time == 0:
			self.game_state.state = State.CARD_SELECTION

		# CARD_SELECTION => POST_CARD_SELECTION
		elif self.game_state.state == State.CARD_SELECTION:
			if board.handle_card_selection():
				self.game_state.state = State.POST_CARD_SELECTION
				self.game_state.wait_time = Wait.POST_CARD_SELECTION.value

		# POST_CARD_SELECTION => TURN_POPUP, ROUND_ENDED, GAME_OVER_SCREEN
		elif self.game_state.state == State.POST_CARD_SELECTION and self.game_state.wait_time == 0:
			if board.round_complete():
				self.game_state.state = State.ROUND_ENDED
				self.game_state.wait_time = Wait.ROUND_ENDED.value

			else:
				board.next_turn()
				self.game_state.state = State.TURN_POPUP
				self.game_state.wait_time = Wait.TURN_POPUP.value

		# ROUND_ENDED => TURN_POPUP, GAME_OVER_SCREEN
		elif self.game_state.state == State.ROUND_ENDED and self.game_state.wait_time == 0:
			board.reset()

			if board.game_complete():
				self.game_state.state = State.GAME_OVER_SCREEN
				return

			self.game_state.state = State.TURN_POPUP
			self.game_state.wait_time = Wait.TURN_POPUP.value

		if self.game_state.wait_time > 0:
			self.game_state.wait_time -= 1


	def start_game(self):
		# init players
		names = random.sample(nameChoices, 2)
		players = []
		players.append(Player("Alex-Multi", Fruit.COCONUT, is_human=True))
		players.append(Player(names[0], Fruit.WATERMELON))
		players.append(Player(names[1], Fruit.PINEAPPLE))

		self.game_state.board = Board(players, None)

		self.started = True
		print("Created board", self.game_state.board.players)


	# def __repr__(self):
	# 	return str(self.id) + " with " + str(len(self.client_sockets)) + " clients"