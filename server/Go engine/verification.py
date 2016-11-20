import copy
import random
import time

random.seed(time.time())

#To do: ko rule

#Coordinates of a point on board
class Coordinate(object):
    def __init__ (self,row,column):
        self.row = row
        self.col = column


class MoveSuccess (object):
    def __init__(self):
        self.puts_self_in_danger = False
        self.takes_out_enemies = False

        self.num_enemies_taken_out = 0

    def self_in_danger(self):
        self.puts_self_in_danger = True

    def enemies_taken_out (self,num):
        self.takes_out_enemies = True
        self.num_enemies_taken_out = num
    
        
class Connection(object):
    def __init__ (self,board_ref):
        #Each element is a Coordinate object
        self.board = board_ref
        self.connection = []
        self.liberties = []

    def add_connection(self,point):
        self.connection += [point]

    #Get number of blocked liberties for a connection
    def get_blocked_liberties(self):
        self.blocked_liberties = 0
        
        if self.liberties == []:
            return 0
        
        for coord in self.liberties:
            if self.board.board[coord.row][coord.col] != ' ':
                self.blocked_liberties += 1

        return self.blocked_liberties

    #Returns true is all liberties have been blocked off by enemy stones, else false
    def all_liberties_taken (self):

        if self.get_blocked_liberties() == self.num_liberties:
            return True

        return False

    #Gets all liberties for a single stone or string
    def identify_liberties(self):
        
        self.num_liberties = 0
        self.blocked_liberties = 0
        
        for coord in self.connection:
            own_colour = self.board.board[coord.row][coord.col]

            for i in range (-1,2,1):
                for j in range(-1,2,1):
                    if i == 0 and j == 0:
                        continue

                    if coord.row + i < 0 or coord.row + i >= self.board.board_size:
                        continue

                    if coord.col + j < 0 or coord.col + j >= self.board.board_size:
                        continue

                    if i in (1,-1) and j in (1,-1):
                        continue

                    #This will be a part of the connection
                    if self.board.board[coord.row+i][coord.col+j] == own_colour:
                        continue

                    #This hasn't already been chosen
                    if len(self.board.board[coord.row+i][coord.col+j]) == 1:
                        self.num_liberties += 1
                        if self.board.board[coord.row+i][coord.col+j] != own_colour:
                            self.blocked_liberties += 1
                            
                        self.liberties += [Coordinate(coord.row+i,coord.col+j)]
                        self.board.board[coord.row+i][coord.col+j] += "X"

        for i in self.liberties:
            self.board.board[i.row][i.col] = self.board.board[i.row][i.col][0]
                
class Board(object):
    #The two possible stones in go
    black = "B"
    white = "W"

    #Go is usually played on a 19x19 board, so this is set as the default size
    def __init__ (self,board_size = 19):

        
        if board_size <= 2:
            board_size = 19

        #Boolean used to check if a board has been set up
        self.board_initialised = False    
        self.board_size = board_size

        
        self.board = []
        #All the different strings in a game
        self.connections = []
        self.banned_moves = []
        self.white_possible_moves = []
        self.black_possible_moves = []

  
    def empty_lists (self):
        self.board = []
        self.connections = []

        #Used to implement Ko rule
        self.banned_moves = []
        self.black_prisoners = 0
        self.white_prisoners = 0

        self.white_possible_moves = ["pass"]
        self.black_possible_moves = ["pass"]
        
    def init_board (self, copy_board =  None):
        """Returns true if a board was successfully initialised, otherwise returns false"""
        self.black_prisoners = 0
        self.white_prisoners = 0

        if self.board_initialised:
            self.clear_board()
            
        #Allow user to copy a board into current board
        if copy_board != None:
            if len(copy_board) == self.board_size:
                for row in copy_board:
                    if len(row) != self.board_size:
                        return False
                    
                    for column in row:
                        if column not in (' ',self.black,self.white):
                            return False  
                self.board = copy.deepcopy(copy_board)


        else:
            self.board = [ [' ' for row in range(self.board_size)] for column in range(self.board_size) ]

        if copy_board == None:
            self.white_possible_moves = [[Coordinate(row,col),MoveSuccess()] for row in range(self.board_size) for col in range(self.board_size)]
            self.black_possible_moves = [[Coordinate(row,col),MoveSuccess()] for row in range(self.board_size) for col in range(self.board_size)]

        else:
            self.update_possible_moves()

        self.board_initialised = True
        return True

    def random_board (self, num_pieces = 5):
        self.init_board()

        restart = False

        for i in range(num_pieces):
            colour = random.choice([self.black,self.white])

            moves = self.get_possible_moves(colour)

            #No possible move available, so we need to restart
            if moves == ["resign"]:
                #I want to avoid recursion, so have function completely terminate when calling it again
                restart = True
                break


            random_move = random.choice(moves)

            self.place_stone(random_move[0].row,random_move[0].col,colour,random_move[1],True)

        if restart:
            self.random_board(num_pieces)

    def get_possible_moves (self,colour):

        if colour == self.white:
            if len(self.white_possible_moves) == 1:
                return ["resign"]

            return self.white_possible_moves


        elif colour == self.black:
            if len(self.black_possible_moves) == 1:
                return ["resign"]
            return self.black_possible_moves


    def clear_board(self):
        self.clear_lists()
        self.board_initialised = False

    #Gets socre based on number of prisoners and number of stones on the board
    def score (self,colour):
        num_occupied = 0
        prisoners = 0

        if colour == self.white:
           connection = self.white_connections
           prisoners = self.black_prisoners

        elif colour == self.black:
           connection = self.black_connections
           prisoners = self.white_prisoners

        for i in connection:
            num_occupied += len(i.connection)

        return num_occupied + prisoners



    def place_stone (self,row,col,stone,move_result = None, should_update_possible_moves = False):
        #If move_result is not none then it's a real move
        #This method ensures that captured stones are to be removed


        if stone.upper() not in (self.black,self.white):
            return False

        if row >= self.board_size or col >= self.board_size:
            return False

        self.board[row][col] = stone

        self.update_connections()
        enforce_ko = False

        if move_result != None:
            self.banned_moves = []
            if move_result.puts_self_in_danger and move_result.takes_out_enemies:
                #Ko rule
                if move_result.num_enemies_taken_out == 1:

                    #Check if piece is singular and not connected to other stones, otherwise Ko rule is invalid
                    other_connections = False

                    for i in range(-1,2,1):
                        for j in range(-1,2,1):
                            if i == j:
                                continue

                            if i in (-1,1) and j in (-1,1):
                                continue

                            if row + i >= self.board_size or row + i <0:
                                continue

                            if col + i >= self.board_size or col + i < 0:
                                continue

                            if self.board[row+i][col+j] == stone:
                                other_connections = True
                                break

                    
                    if not other_connections:
                        #Ban going to same place for one move
                        enforce_ko = True

            if move_result.takes_out_enemies:
                print("Removing enemy")

                if stone == self.white:
                    enemy_connection = self.black_connections

                elif stone == self.black:
                    enemy_connection = self.white_connections

                self.remove_trapped_stones(enemy_connection,enforce_ko)
                self.update_connections()

        if should_update_possible_moves:
            self.update_possible_moves()

    def update_possible_moves (self):

        self.white_possible_moves = ["pass"]
        self.black_possible_moves = ["pass"]
        
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] == ' ':
                    move_result_w = self.is_move_legal(row,col,self.white)
                    move_result_b = self.is_move_legal(row,col,self.black)
                    
                    if move_result_w != False:
                        self.white_possible_moves += [[Coordinate(row,col),move_result_w]]

                    if move_result_b != False:
                        self.black_possible_moves += [[Coordinate(row,col),move_result_b]] 
                
        
    def update_connections (self):
        
        #Once a coordinate has been added to a connection, we don't need to check it again
        self.black_connections = []
        self.white_connections = []
        
        #This'll be in order. All the points still to be checked for connections
        coords_to_check = [Coordinate(i,j) for i in range(self.board_size) for j in range(self.board_size)]

        while coords_to_check != []:
            if self.board [coords_to_check[0].row][coords_to_check[0].col] == ' ':
                del coords_to_check[0]
                continue
            
            possible_connections = [coords_to_check[0]]
            colour = self.board[coords_to_check[0].row][coords_to_check[0].col]

            #If a position is currently being checked for connections, an "X" is added to it so we know it's being checked for future reference
            #Saves for unncessary looping for checking if a coordinate is already part of a connection later on
            self.board [coords_to_check[0].row][coords_to_check[0].col] += "X"
            
            self.__find_connections(coords_to_check[0],possible_connections)

        
            connection_point = Connection(self)
            for i in possible_connections:
                connection_point.add_connection(i)
                #Get rid of the 'X' that was placed
                self.board[i.row][i.col] = self.board[i.row][i.col][0]

                #I was going to do a binary search, but max number of coordinates will be 361, so linear search is as good a search as any
                for j in range(len(coords_to_check)):
                    if coords_to_check[j].row == i.row and coords_to_check[j].col == i.col:
                        del coords_to_check[j]
                        break
                    
            connection_point.identify_liberties()
            if colour == self.white:
                self.white_connections += [connection_point]

            elif colour == self.black:
                self.black_connections += [connection_point]
                
    def refresh_connections (self,connections):
        for i in connections:
            i.get_blocked_liberties()
        

    def __find_connections (self,coord,possible_connections):

        stone_colour = self.board[coord.row][coord.col][0]

        #Get all points surrounding current stone
        for i in range(-1,2,1):
            for j in range(-1,2,1):

                #It's own location
                if i == 0 and j == 0:
                    continue

                if coord.row + i < 0 or coord.row + i >= self.board_size:
                    continue

                if coord.col + j < 0 or coord.col + j >= self.board_size:
                    continue
                        
                #Diagonal
                if i in (1,-1) and j in (1,-1):
                    continue

                #Check if same colour and hasn't already been done, as it won't have additional X, so will only be equal to 'B' or 'W' exactly
                if self.board[coord.row+i][coord.col+j] == stone_colour:
    
                    self.board[coord.row+i][coord.col+j] += "X"
                    
                    possible_connections += [Coordinate(coord.row+i,coord.col+j)]

                    #Get all connections next to the current coordinate that haven't yet been checked
                    self.__find_connections(possible_connections[-1],possible_connections)

    #Used to remove trapped stones
    def remove_trapped_stones(self,connection, ko_rule = False):
        i = 0
        length = len(connection)
        count = 0
        while count < length :
            if connection[i].all_liberties_taken():
                for coord in connection[i].connection:
                    if self.board[coord.row][coord.col] == self.white:
                        self.white_prisoners += 1

                    elif self.board[coord.row][coord.col] == self.black:
                        self.black_prisoners += 1

                    self.board[coord.row][coord.col] = ' '
                    if ko_rule:
                        self.banned_moves += [coord]


                del connection[i]

            else:
                i += 1

            count += 1

    
    def is_move_legal (self,row,col,colour):

        for i in self.banned_moves:
            if i.row == row and i.col == col:
                return False

        if self.board[row][col] != ' ':
            return False

        self.place_stone (row,col,colour)

        own_connections = []
        enemy_connections = []

        if colour == self.white:
            own_connections = self.white_connections
            enemy_connections = self.black_connections

        elif colour == self.black:
            own_connections = self.black_connections
            enemy_connections = self.white_connections

        own_stones_in_danger = False
        move_removes_enemies = False
        enemies_taken_out = 0

        for i in own_connections:
            if i.all_liberties_taken():
                own_stones_in_danger = True
                break

        for i in enemy_connections:
            if i.all_liberties_taken():
                move_removes_enemies = True
                enemies_taken_out += len(i.connection)
                
        #Here I need to check if the move made is connected to a string
        #If it isn't, then I need to implement the ko rule

        #Reset everything
        self.board[row][col] = ' '
        self.update_connections()

        if own_stones_in_danger and not move_removes_enemies:
            return False

        move_result = MoveSuccess()

        if own_stones_in_danger and move_removes_enemies:
            move_result.self_in_danger()
            move_result.enemies_taken_out(enemies_taken_out)

        if not own_stones_in_danger and move_removes_enemies:
            move_result.enemies_taken_out(enemies_taken_out)

        return move_result

#What I need to do next:
#Add scoring and territory
#Keep track of prisoners
#In the game loop give an AI the ability to quit by returning "pass"

#Generate legal random go positions to verify an AI

