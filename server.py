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

def listen_for_clients(server_sock):
	# while True:
	conn, addr = server_sock.accept()
	if conn and addr:
		print("client connected")

		# if len(lobbies) == 0:
		#     lobbies.append(Lobby(addr))
		# lobbies[0].client_sockets.append(conn)
		# print(lobbies[0])
		# lobbies[0].start_game()
		# conn.send(pickle.dumps(lobbies[0].game_state))

	# server_sock.close() 



if __name__ == "__main__":
	
	server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_sock.bind((IP, PORT))
	server_sock.listen(2)

	#Start threads
	# server_thread = threading.Thread(target=listen_for_clients, args=(server_sock,), daemon=True)
	# server_thread.start()
	
	clock = pygame.time.Clock()
	
	

	lobby = Lobby(server_sock)
	

	try:
		while True:
			lobby.update_game()

			#busy wait
			clock.tick(fps)

	except Exception as e:

		print("Stopping...")
		print(e)

		#close all threads
		server_sock.close()
		# server_thread.join()
		
		print("All threads successfully terminated")