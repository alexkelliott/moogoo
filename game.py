# Sorting algorithims and pygame practice
import pygame
import random
import time

from player import Player

from fruit import Fruit
from board import Board
from renderer import Renderer

pygame.init()
pygame.display.set_caption('Moogoo Monkey')

screen_height = 480
screen_width = 720
surface = pygame.display.set_mode((screen_width, screen_height))

nameChoices = ["Ava Cadavra", "Misty Waters", "Daddy Bigbucks", "Giuseppi Mezzoalto", "Dusty Hogg", "Phoebe Twiddle", "Luthor L. Bigbucks", "Lottie Cash", "Detective Dan D. Mann", "Pritchard Locksley", "Futo Maki", "Ephram Earl", "Lily Gates", "Cannonball Coleman", "Sue Pirmova", "Lincoln Broadsheet", "Crawdad Clem", "Bayou Boo", "Maximillian Moore", "Bucki Brock", "Berkeley Clodd", "Gramma Hattie", "Pepper Pete", "Dr. Mauricio Keys", "Olde Salty", "Lloyd", "Harlan King", "Daschell Swank", "Kris Thristle"]
    

def wait(time):
    while time > 0:
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            pygame.quit()

        pygame.time.wait(1)
        time -= 1


def init():
    # init renderer
        renderer = Renderer(surface)

        # init players
        names = random.sample(nameChoices, 2)
        players = []
        players.append(Player("Alex", Fruit.COCONUT, is_human=True))
        players.append(Player(names[0], Fruit.WATERMELON))
        players.append(Player(names[1], Fruit.PINEAPPLE))
        
        # init board
        board = Board(players)
        board.deal_cards()

        return board, renderer


if __name__ == "__main__":
    board, renderer = init()

    counter = 0
    
    while not board.game_complete():
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            break

        renderer.render(board)

        while not board.round_complete():
            renderer.player_turn_popup(board.players[board.turn])
            wait(500)
            renderer.render(board)

            wait(100)
            board.handle_bet_selection(renderer)
            renderer.render(board)

            if board.turn: # only wait if its a computer
                wait(350)

            if board.handle_card_selection(renderer):
                renderer.render(board)
                wait(400)

            next_player = board.next_turn()

        print("ROUND COMPLETE!", board.top_card)

        board.reset()
        board.deal_cards()
        renderer.render(board)


    print("GAME OVER")

    final_ranking = board.final_scores()
    for player in final_ranking:
        print(player.fruit, player.name, player.score)


    while True:
        pass

    pygame.quit()
        
