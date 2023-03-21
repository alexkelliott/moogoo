import time
import threading
import socket
import pickle
import pygame

from lobby import Lobby, Client
from card import Card


IP = "127.0.0.1"
PORT = 13000
fps = 60
lobbies = []


if __name__ == "__main__":
	
	server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_sock.bind((IP, PORT))
	server_sock.listen(2)
	
	clock = pygame.time.Clock()

	lobby = Lobby(server_sock)

	while True:
		if lobby.started:
			lobby.update_game()

		#busy wait
		clock.tick(fps)
	