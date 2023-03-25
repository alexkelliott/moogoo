import time
import threading
import socket
import pickle
from pygame.time import Clock

from lobby import Lobby, Client
from card import Card


IP: str = "127.0.0.1"
PORT: int = 13000
fps: int = 60
lobbies: list[Lobby] = []


if __name__ == "__main__":
	
	server_sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_sock.bind((IP, PORT))
	server_sock.listen(2)
	
	clock: Clock = Clock()

	lobby = Lobby(server_sock)

	while True:
		if lobby.started:
			lobby.update_game()

		#busy wait
		clock.tick(fps)
	