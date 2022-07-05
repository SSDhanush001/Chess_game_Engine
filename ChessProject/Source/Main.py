from ast import Pass
from cmath import pi
import pygame
import sys
from square import Square
from move import Move
from values import *
from game import Game

class Main:

    def __init__(self):
        pygame.init() #initialsizing pygame
        self.screen = pygame.display.set_mode((Width,Height))
        pygame.display.set_caption("Chess")
        self.game = Game()


    def mainloop(self):

        screen = self.screen
        game = self.game
        board = self.game.board
        dragger = self.game.dragger

        while True:
            #show methods
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            

            if dragger.dragging:
                dragger.update_blit(screen)

            for event in pygame.event.get(): # setting up the game screen
                
                #CLICK
                if event.type == pygame.MOUSEBUTTONDOWN:
                    dragger.update_mouse(event.pos)

                    
                    clicked_row = dragger.mouseY//Sqrsize
                    clicked_col = dragger.mouseX//Sqrsize
                    
                    #if clicked square has piece
                    if board.squares[clicked_row][clicked_col].has_piece():
                        piece = board.squares[clicked_row][clicked_col].piece
                        #if valide piecw colour
                        if piece.colour == game.next_player:
                            board.calc_moves(piece,clicked_row,clicked_col,bool = True)
                            dragger.save_initial(event.pos)
                            dragger.drag_piece(piece)
                            #show methods
                            game.show_bg(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen)


                #Mouse MOTION
                elif event.type == pygame.MOUSEMOTION:
                    motion_row = event.pos[1]//Sqrsize
                    motion_col = event.pos[0]//Sqrsize
                    
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        #show methods
                        game.show_bg(screen)
                        game.show_last_move(screen)
                        game.show_moves(screen)
                        game.show_pieces(screen)
                        
                        dragger.update_blit(screen)
                
                #release
                elif event.type == pygame.MOUSEBUTTONUP:

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)

                        released_row = dragger.mouseY//Sqrsize
                        released_col = dragger.mouseX//Sqrsize

                        #create possible move
                        initial = Square(dragger.initial_row,dragger.initial_col)
                        final = Square(released_row, released_col)
                        move = Move(initial,final)
                        
                        #valid move
                        if board.valid_move(dragger.piece,move):
                            board.move(dragger.piece,move)
                            #show methods
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_pieces(screen)

                            #next turn
                            game.next_turn()


                    dragger.undrag_piece()

                #key press
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game.reset()
                        game = self.game
                        board = self.game.board
                        dragger = self.game.dragger

                
                #exit game
                elif event.type == pygame.QUIT: # for exiting the game
                    pygame.quit()
                    sys.exit()

                
            pygame.display.update()

main = Main()
main.mainloop()
