import pygame
from Piece import Piece
from values import *
from board import  Board
from dragger import Dragger
from square import Square

class Game:

    def __init__(self):
        self.next_player = 'white'
        self.hovered_sqr = None
        self.board = Board()
        self.dragger = Dragger()

    # Show Methods

    def show_bg(self,surface):
        for row in range(Rows):
            for col in range(Columns):
                if (row + col)%2 == 0:
                    colour = (245,240,220)
                else:
                    colour = (144,200,172)

                rect = (col*Sqrsize, row*Sqrsize, Sqrsize, Sqrsize)

                pygame.draw.rect(surface,colour,rect)

    def show_pieces(self,surface):
         for row in range(Rows):
            for col in range(Columns):
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece
                    

                    #all pieces except dragger piece
                    if piece is not self.dragger.piece:
                        piece.set_texture(size = 80)
                        img = pygame.image.load(piece.texture)
                        img_center = col*Sqrsize + Sqrsize // 2, row*Sqrsize + Sqrsize //2
                        piece.texture_rect = img.get_rect(center = img_center)
                        surface.blit(img, piece.texture_rect)

    def show_moves(self,surface):
        if self.dragger.dragging:
            piece = self.dragger.piece

            #for all valid moves
            for move in piece.moves:
                #colour
                colour = '#C86464' if (move.final.row + move.final.col) % 2 == 0 else '#684646'
                #rect
                rect =(move.final.col*Sqrsize , move.final.row*Sqrsize, Sqrsize ,Sqrsize)
                #blit
                pygame.draw.rect(surface, colour, rect)

    def show_last_move(self, surface):
        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final

            for pos in [initial,final]:

                #colour
                colour = (244,247,200) if (pos.row + pos.col)% 2 ==0 else(173,195,172)
                #rect
                rect = (pos.col*Sqrsize,pos.row*Sqrsize,Sqrsize,Sqrsize)
                #blit
                pygame.draw.rect(surface, colour, rect)

    def next_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'

    def set_hover(self,row,col):
        self.hovered_sqr = self.board.squares[row][col]

    def reset(self):
        self.__init__()