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


# return's true if the round is complete
def round_complete(board):
    return len([c for c in board.top_card.values() if c]) == 6
    



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

        # board.handle_turn(players[1])

        # board.handle_turn(players[2])

        return board, renderer


if __name__ == "__main__":
    board, renderer = init()
    
    while True:
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            break

        renderer.render(board)

        while not round_complete(board):
            
            board.handle_bet_selection()
            renderer.render(board)

            time.sleep(0.5)

            board.handle_card_selection()
            renderer.render(board)

            board.next_turn()
            time.sleep(1.5)

        print("ROUND COMPLETE", board.top_card)

        renderer.render(board)

        while True:
            pass

    pygame.quit()
        
