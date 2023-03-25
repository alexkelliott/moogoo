import pygame


class Screen():

	def __init__(self) -> None:
		pass


	def poll_input(self, game_state) -> None:
		game_state.mouse_click = False
		game_state.pointer = False

		for ev in pygame.event.get():
			if ev.type == pygame.QUIT:
				pygame.quit()

			if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
				game_state.mouse_click = True
				game_state.mouse_down = False

			if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
				game_state.mouse_down = True

		mouse: list[int] = pygame.mouse.get_pos()
		game_state.mouse_coords = {'x': mouse[0], 'y': mouse[1]}


	def mouse_in(self, mouse_coords, left, width, top, height) -> bool:
		return left <= mouse_coords['x'] <= left + width and top <= mouse_coords['y'] <= top + height