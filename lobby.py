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
		# init state
		# self.state = State.TURN_POPUP
		# self.wait_time = Wait.TURN_POPUP.value

		conn, addr = sock.accept()
		self.client_socket = conn
		print("client connected!")

		name = conn.recv(1024)
		print("name:", name.decode())

		turn_num = 0 # {0, 1, 2}

		self.client_socket.send(bytes(f"{turn_num}", 'utf-8'))
		
		self.game_state = Game_State(server=True, name=name.decode())
		self.game_state.wait_time = Wait.TURN_POPUP.value

		self.started = False

		print("Created lobby")


	def update_clients(self):
		# for conn in self.client_sockets:
		# 	conn.send(pickle.dumps(self.game_state))
		# self.client_socket.send(pickle.dumps(self.game_state))

		HEADERSIZE = 10

		print("new state #2!", self.game_state.board.turn)

		msg = pickle.dumps(self.game_state)
		msg = bytes(f"{len(msg):<{HEADERSIZE}}", 'utf-8')+msg
		self.client_socket.send(msg)
		print("Sent game state")



	def listen_for_update(self):
		HEADERSIZE = 10

		print("listening for player update...")

		while True:
			full_msg = b''
			new_msg = True

			while True:
				msg = self.client_socket.recv(16)
				if new_msg:
					msglen = int(msg[:HEADERSIZE])
					new_msg = False

				full_msg += msg

				if len(full_msg)-HEADERSIZE == msglen:
					break

			raw_board = full_msg[HEADERSIZE:]
			received_board = pickle.loads(raw_board)
			received_board.game_state = None # clear the backward reference
			self.game_state.board = received_board
			print("received player update")
			break



	def update_game(self):

		print(self.game_state.state, '\t', self.game_state.wait_time, '\t', self.game_state.board.players[self.game_state.board.turn].name)

		og_board_state = self.game_state.state

		# TURN_POPUP => PRE_BET, BET
		if self.game_state.state == State.TURN_POPUP and self.game_state.wait_time == 0:
			if self.game_state.board.players[self.game_state.board.turn].is_human:
				if self.game_state.board.bet_boxes_full():
					self.game_state.state = State.CARD_SELECTION
				else:
					self.game_state.state = State.BET
			else: # npc
				if self.game_state.board.bet_boxes_full():
					self.game_state.state = State.PRE_CARD_SELECTION
					self.game_state.wait_time = Wait.PRE_CARD_SELECTION.value
				else:
					self.game_state.state = State.PRE_BET
					self.game_state.wait_time = Wait.PRE_BET.value

			# self.update_clients()

		# PRE_BET => BET
		elif self.game_state.state == State.PRE_BET and self.game_state.wait_time == 0:
			self.game_state.state = State.BET
			# self.update_clients()

		# BET => PRE_CARD_SELECTION, CARD_SELECTION, TURN_POPUP
		elif self.game_state.state == State.BET:
			if self.game_state.board.players[self.game_state.board.turn].is_human:

				# wait for the player to play
				self.listen_for_update()

				if self.game_state.board.three_bets():
					self.game_state.state = State.CARD_SELECTION
				else:
					self.game_state.board.next_turn()

					self.game_state.state = State.TURN_POPUP
					self.game_state.wait_time = Wait.TURN_POPUP.value
				pass
			else:
				if self.game_state.board.handle_bet_selection():
					if self.game_state.board.three_bets():
						self.game_state.state = State.PRE_CARD_SELECTION
						self.game_state.wait_time = Wait.TURN_POPUP.value
					else:
						self.game_state.board.next_turn()
						self.game_state.state = State.TURN_POPUP
						self.game_state.wait_time = Wait.TURN_POPUP.value

		# PRE_CARD_SELECTION => CARD_SELECTION 
		elif self.game_state.state == State.PRE_CARD_SELECTION and self.game_state.wait_time == 0:
			self.game_state.state = State.CARD_SELECTION

		# CARD_SELECTION => POST_CARD_SELECTION
		elif self.game_state.state == State.CARD_SELECTION:
			if self.game_state.board.players[self.game_state.board.turn].is_human:

				# wait for the player to play
				self.listen_for_update()
				
				self.game_state.state = State.POST_CARD_SELECTION
				self.game_state.wait_time = Wait.POST_CARD_SELECTION.value

			else:
				if self.game_state.board.handle_card_selection():
					self.game_state.state = State.POST_CARD_SELECTION
					self.game_state.wait_time = Wait.POST_CARD_SELECTION.value

		# POST_CARD_SELECTION => TURN_POPUP, ROUND_ENDED, GAME_OVER_SCREEN
		elif self.game_state.state == State.POST_CARD_SELECTION and self.game_state.wait_time == 0:
			if self.game_state.board.round_complete():
				self.game_state.state = State.ROUND_ENDED
				self.game_state.wait_time = Wait.ROUND_ENDED.value

			else:
				self.game_state.board.next_turn()
				self.game_state.state = State.TURN_POPUP
				self.game_state.wait_time = Wait.TURN_POPUP.value

		# ROUND_ENDED => TURN_POPUP, GAME_OVER_SCREEN
		elif self.game_state.state == State.ROUND_ENDED and self.game_state.wait_time == 0:
			self.game_state.board.reset()

			if self.game_state.board.game_complete():
				self.game_state.state = State.GAME_OVER_SCREEN
			else:
				self.game_state.state = State.TURN_POPUP
				self.game_state.wait_time = Wait.TURN_POPUP.value


		if og_board_state != self.game_state.state:
			print("new state #1!", self.game_state.board.turn)
			self.update_clients()
			print("new state #3!", self.game_state.board.turn)



		if self.game_state.wait_time > 0:
			self.game_state.wait_time -= 1


	# def __repr__(self):
	# 	return str(self.id) + " with " + str(len(self.client_sockets)) + " clients"