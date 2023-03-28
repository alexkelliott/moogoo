import pygame
from pygame.time import Clock
import json

from game_state import Game_State, Client_Game_State

fps: int = 60


if __name__ == "__main__":

	# init game variables
	pygame.init()
	clock: Clock = Clock()
	game_state: Game_State = Client_Game_State()

	# read user settings
	with open("user_settings.json", "r") as us:
		settings: dict[str, str] = json.loads(us.read())
		game_state.user_settings = {
			"ip":          settings["hostname"],
			"port":        int(settings["port"]),
			"player_name": settings["player_name"]}

	# game loop
	while True:
		game_state.current_screen.poll_input(game_state)
		game_state.current_screen.update(game_state)
		game_state.renderer.render(game_state)
		print(game_state.current_screen)
		clock.tick(fps)


# TODO:
#	-allow for user to choose their own name in game (not thru file)
#	-allow players to chose their own fruits
#	-add graceful failure if can't connect to server
#	-change return state to settings open for single player
#	-make the lobby screen actually decent
#	-handle clients leaving
#	-make new set of dimmmensions for buttons that are using dupes