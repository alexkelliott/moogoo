import pickle
import threading
from socket import socket

import net
from constants import *
from game_state import Server_Game_State
from board import Board
from enums import Fruit, State, Wait
from player import Player


class Client():
	
	def __init__(self, sock, player):
		self.player: Player = player
		self.sock: socket = sock

	def __getstate__(self):
		state = self.__dict__.copy()
		del state["sock"]
		return state

class Lobby():

	def __init__(self, server_sock):
		self.server_sock: socket = server_sock
		self.clients: List[Client] = []
		self.started: bool = False
		self.game_state: Server_Game_State = None

		self.list_for_new_clients_thread: threading.Thread = threading.Thread(target=self.listen_for_new_clients, args=(), daemon=True)
		self.list_for_new_clients_thread.start()


	def listen_for_start_msg(self, sock):
		while not self.started:
			try:
				msg: str = net.rec_data(sock).decode()
				if msg == "START_GAME":
					self.start_game()
					break
			except Exception as e:
				print(e)
				break


	def start_game(self):
		self.game_state = Server_Game_State()
		self.game_state.gen_board([c.player for c in self.clients])
		self.game_state.wait_time = Wait.TURN_POPUP.value
		self.started = True
		for client in self.clients:
			net.send_data(client.sock, "STARTING".encode())
		self.list_for_new_clients_thread.join()


	def listen_for_new_clients(self):
		while len(self.clients) < 3 and not self.started:
			try:
				conn, addr = self.server_sock.accept()
			except Exception as e:
				print(e)
				break

			if self.started:
				net.send_data(conn, "STARTED".encode())
				break
			else:
				net.send_data(conn, "CONNECTED".encode())

			name: str = net.rec_data(conn).decode()

			turn_num: int = len(self.clients) # {0, 1, 2}
			net.send_data(conn, str(turn_num).encode())

			fruit: Fruit = [f for f in Fruit][turn_num]
			new_player: Player = Player(name, fruit, is_human=True)
			self.clients.append(Client(conn, new_player))

			for client in self.clients:
				players: Players = [c.player for c in self.clients]
				net.send_data(client.sock, pickle.dumps(players))
			
			if turn_num == 0:
				self.lsm_thread = threading.Thread(target=self.listen_for_start_msg, args=(conn,), daemon=True)
				self.lsm_thread.start()


	def listen_for_client_update(self):
		sock: socket = self.clients[self.game_state.board.turn].sock
		raw_board: bytes = net.rec_data(sock)
		received_board: Board = pickle.loads(raw_board)
		received_board.game_state = None # clear the backward reference
		self.game_state.board = received_board


	def update_clients(self):
		for client in self.clients:
			net.send_data(client.sock, pickle.dumps(self.game_state))


	def update_game(self):
		print(self.game_state.state, '\t', self.game_state.wait_time, '\t', self.game_state.board.players[self.game_state.board.turn].name)

		og_board_state: State = self.game_state.state

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

		# PRE_BET => BET
		elif self.game_state.state == State.PRE_BET and self.game_state.wait_time == 0:
			self.game_state.state = State.BET

		# BET => PRE_CARD_SELECTION, CARD_SELECTION, TURN_POPUP
		elif self.game_state.state == State.BET:
			if self.game_state.board.players[self.game_state.board.turn].is_human:

				# wait for the player to play
				self.listen_for_client_update()

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
				self.listen_for_client_update()

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
			self.update_clients()

		if self.game_state.wait_time > 0:
			self.game_state.wait_time -= 1