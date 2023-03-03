# Sorting algorithims and pygame practice
import pygame
import random
import time

from player import Player
from enums import Fruit
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

        return board, renderer


if __name__ == "__main__":
    board, renderer = init()
    
    while not board.game_complete():
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            break

        board.reset()
        board.deal_cards()
        renderer.render(board)
        wait(500)

        while not board.round_complete():
            renderer.top_text = "Place a bet"
            renderer.render(board)
            renderer.player_turn_popup(board.players[board.turn])
            wait(500)
            renderer.render(board) # erase turn popup

            wait(100)
            board.handle_bet_selection(renderer)
            if board.three_bets():
                renderer.top_text = "Play a card"
            renderer.render(board)

            # only wait for card selection if its a computer's turn
            if board.turn:
                wait(350)

            # card selection if enough bets are on the table
            if board.three_bets():
                board.handle_card_selection(renderer)
                renderer.render(board)
                wait(400)

            next_player = board.next_turn()

    renderer.top_text = "Game over"
    renderer.render(board)
    wait(1000)
    renderer.game_over_screen(board.final_scores())

    while True:
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            break

    pygame.quit()
        
