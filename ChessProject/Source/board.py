from ast import Pass
from operator import le
from re import L
import re
from typing import ParamSpecArgs
from square import Square
from values import *
from square import Square
from Piece import *
from move import Move
import os
import copy

class Board:

    def __init__(self):
        self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(Columns)]
        self.last_move = None
        self._create()
        self._add_piece("white")
        self._add_piece("black")

    def move(self,piece,move):
        initial = move.initial
        final = move.final

        #console board move update
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece =  piece

        #pawn promotion
        if isinstance(piece,Pawn):
            self.check_promotion(piece, final)

        #king castling
        if isinstance(piece,King):
            if self.castling(initial,final):
                diff = final.col - initial.col
                rook = piece.left_rook if (diff<0) else piece.right_rook
                self.move(rook, rook.moves[-1])

        #move
        piece.moved = True

        #clear valid moves
        piece.clear_moves()

        self.last_move = move
    
    def valid_move(self,piece,move):
        return move in piece.moves

    def check_promotion(self,piece,final):
        if final.row == 0 or final.row == 7:
            self.squares[final.row][final.col].piece = Queen(piece.colour)

    def castling(self,initial, final):
        return abs(initial.col - final.col) == 2

    def in_check(self,piece,move):
        temp_piece = copy.deepcopy(piece)
        temp_board = copy.deepcopy(self)
        temp_board.move(temp_piece,move)
        for row in range (Rows):
            for col in range(Columns):
                if temp_board.squares[row][col].has_enemy_piece(piece.colour):
                    p = temp_board.squares[row][col].piece
                    temp_board.calc_moves(p,row,col,bool = False)
                    for m in p.moves:
                        if isinstance(m.final.piece,King):
                            return True
        return False

    def calc_moves(self, piece, row, col, bool = True):

        def pawn_moves():
            #steps
            steps = 1 if piece.moved else 2

            #verical moves
            start = row + piece.dir
            end = row + (piece.dir*(1+steps))
            for move_row in range(start,end, piece.dir):
                if Square.in_range(move_row):
                    if self.squares[move_row][col].isempty():
                        #create initial and final move
                        initial = Square(row,col)
                        final = Square(move_row,col)
                        #create a new move
                        move = Move(initial,final)

                        #check potential checks
                        if bool:
                            if not self.in_check(piece,move):
                                #append new move
                                piece.add_move(move)
                        else:
                            #append new move
                            piece.add_move(move)
                    #blocked
                    else: break
                #not in range
                else: break

            #diagonal moves
            possible_move_row = row + piece.dir
            possible_move_cols = [col-1, col+1]
            for possible_move_col in possible_move_cols:
                if Square.in_range(possible_move_row,possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.colour):
                        #create initial and final move squares 
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row,possible_move_col,final_piece)
                        #create a new move
                        move = Move(initial, final)
                        #check potential checks
                        if bool:
                            if not self.in_check(piece,move):
                                #append new move
                                piece.add_move(move)
                        else:
                            #append new move
                            piece.add_move(move)

        
        def knight_moves():
            #8possible moves
            possible_moves = [
                (row-2,col+1),
                (row-1,col+2),
                (row+1,col+2),
                (row+2,col+1),
                (row+2,col-1),
                (row+1,col-2),
                (row-1,col-2),
                (row-2,col-1),
                ]

            for possible_move in possible_moves:
                possible_move_row,possible_move_col = possible_move

                if Square.in_range(possible_move_row,possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.colour):
                        #create squares of the new move
                        initial = Square(row,col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row,possible_move_col,final_piece)                 

                        # create new move
                        move = Move(initial,final)
                        #check potential checks
                        if bool:
                            if not self.in_check(piece,move):
                                #append new move
                                piece.add_move(move)
                            else: break
                        else:
                            #append new move
                            piece.add_move(move)

        def starightline_moves(incrs):
            for incr in incrs:
                row_incr, col_incr = incr
                possible_move_row = row + row_incr
                possible_move_col = col + col_incr

                while True:
                    if Square.in_range(possible_move_row,possible_move_col):
                        #create squares of the possible new move
                        initial = Square(row,col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row,possible_move_col,final_piece)
                        #create a possible new move
                        move = Move(initial, final)
                        #empty =  continue looping
                        if self.squares[possible_move_row][possible_move_col].isempty():
                            #check potential checks
                            if bool:
                                if not self.in_check(piece,move):
                                    #append new move
                                    piece.add_move(move)
                            else:
                                #append new move
                                piece.add_move(move)

                        #has enemy piece = add move+ break
                        elif self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.colour):
                            #check potential checks
                            if bool:
                                if not self.in_check(piece,move):
                                    #append new move
                                    piece.add_move(move)
                            else:
                                #append new move
                                piece.add_move(move)
                            break

                        #has team piece
                        elif self.squares[possible_move_row][possible_move_col].has_team_piece(piece.colour):
                            break
                    # not in range
                    else: break

                    #incrementing incrs
                    possible_move_row = possible_move_row + row_incr
                    possible_move_col = possible_move_col + col_incr
        def king_moves():
            adjs = [ 
                (row-1,col+0),
                (row-1,col+1),
                (row+0,col+1),
                (row+1,col+1),
                (row+1,col+0),
                (row+1,col-1),
                (row+0,col-1),
                (row-1,col-1),
            ]

            #normal moves
            for possible_move in adjs:
                possible_move_row, possible_move_col = possible_move

                if Square.in_range(possible_move_row,possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.colour):
                        #create new square
                        initial = Square(row,col)
                        final = Square(possible_move_row, possible_move_col)
                        #create new move
                        move = Move(initial,final)
                        #check potential checks
                        if bool:
                            if not self.in_check(piece,move):
                                #append new move
                                piece.add_move(move)
                            else: break
                        else:
                            #append new move
                            piece.add_move(move)

            #castling moves
            if not piece.moved:
                #queen castling
                left_rook = self.squares[row][0].piece
                if isinstance(left_rook,Rook):
                    if not left_rook.moved:
                        for c in range(1,4):
                            if self.squares[row][c].has_piece():
                                break
                            if c == 3:
                                #add left rook to king
                                piece.left_rook = left_rook

                                #rook move
                                initial = Square(row,0)
                                final = Square(row, 3)
                                moveR = Move(initial,final)

                                #king move
                                initial = Square(row,col)
                                final = Square(row, 2)
                                moveK = Move(initial,final)
                                #check potential checks
                                if bool:
                                    if not self.in_check(piece,moveR) and not self.in_check(piece,moveK):
                                        #append new move to rook
                                        left_rook.add_move(moveR)
                                        #append new move to king
                                        piece.add_move(moveK)
                                else:
                                    #append new move to rook
                                    left_rook.add_move(moveR)
                                    #append new move
                                    piece.add_move(moveK)


                #king castling
                right_rook = self.squares[row][7].piece
                if isinstance(right_rook,Rook):
                    if not right_rook.moved:
                        for c in range(5,7):
                            if self.squares[row][c].has_piece():
                                break
                            if c == 6:
                                #add left rook to king
                                piece.right_rook = right_rook

                                #rook move
                                initial = Square(row,7)
                                final = Square(row, 5)
                                moveR = Move(initial,final)
                                #king move
                                initial = Square(row,col)
                                final = Square(row, 6)
                                moveK = Move(initial,final)
                                

                                #check potential checks
                                if bool:
                                    if not self.in_check(piece,moveR) and not self.in_check(piece,moveK):
                                        #append new move to rook
                                        left_rook.add_move(moveR)
                                        #append new move to king
                                        piece.add_move(moveK)
                                else:
                                    #append new move to rook
                                    left_rook.add_move(moveR)
                                    #append new move
                                    piece.add_move(moveK)


        if isinstance(piece, Pawn): 
            pawn_moves()

        elif isinstance(piece, Knight): 
            knight_moves()

        elif isinstance(piece, Bishop): 
            starightline_moves([
                (-1, 1),  # up-right
                (-1, -1), # up-left
                (1, 1),  # down - right
                (1, -1),  # down - left
            ])
        elif isinstance(piece, Rook):    
             starightline_moves([ 
                (-1, 0), #up
                (0, 1),  #right
                (1, 0),  #down
                (0, -1), # left
             ])

        elif isinstance(piece, Queen): 
            starightline_moves([ 
                (-1,0),  #up
                (0,1),   #right
                (1,0),   #down
                (0,-1),  # left
                (-1,1),  # up-right
                (-1,-1), # up-left
                (1,1),  # down - right
                (1,-1),  # down - left
            ])
        elif isinstance(piece, King): 
            king_moves()

    def _create(self):
        for row in range(Rows):
            for col in range(Columns):
                self.squares[row][col] = Square(row,col)


    def _add_piece(self, colour):
        row_pawn, row_other = (6,7) if colour == "white" else (1,0)
        
        #pawns
        for j in range(Columns):
            self.squares[row_pawn][j] = Square(row_pawn,j,Pawn(colour))

        #rooks
        self.squares[row_other][0] = Square(row_other,0,Rook(colour))
        self.squares[row_other][7] = Square(row_other,7,Rook(colour))

        #knights
        self.squares[row_other][1] = Square(row_other,1,Knight(colour))
        self.squares[row_other][6] = Square(row_other,6,Knight(colour))
        
        # bishops
        self.squares[row_other][2] = Square(row_other,2,Bishop(colour))
        self.squares[row_other][5] = Square(row_other,5,Bishop(colour))

        #Queen
        self.squares[row_other][3] = Square(row_other,3,Queen(colour))

        #king
        self.squares[row_other][4] = Square(row_other,4,King(colour))

