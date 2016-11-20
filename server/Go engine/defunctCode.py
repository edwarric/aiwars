   def is_move_legal_defunct (self,row,col,colour):
        """Do not use"""
        #THIS DOESN'T WORK. A MOVE COULD POTENTIALLY JOIN UP TWO CONNECTIONS TOGETHER
        #I'm going to have to use brute force
        #If a move is legal, I want this method to return metadata on the move
        #Does it take out a piece(s). If so, how many? 
        #If a move has no liberties, then check if it takes out a piece
        #If a move takes ou

        #User can't move in a position that's already taken up
        if self.board[row][col] != ' ':
            return False

        #Boolean to check if the current move can join up to a connection
        found_connection_point = False
        
        self.board[row][col] = colour
        connection_point = None

        #Check if the move can join up to an already existing connection
        for i in self.connections:
            for coord in i.connection:
                diff_row == coord.row - row
                diff_col == coord.col - col

                #No way this can be adjacent to a piece
                if abs(diff_row) > 1 or abs(diff_col) > 1:
                    continue

                if diff_row in (-1,1) and diff_col in (-1,1):
                    continue

                found_connection_point = True
                #Add move to the connection
                i.connection += [Coordinate(row,col)]
                connection_point = i

                break
            
        #At this point, we've found a connection that the move connects to

    
             
        #We need to check whether creating this connection has caused the connection to have no liberties
        #If the connection has no liberties, then the move is invalid
        #However, if the connection causes opponent pieces to not have any liberties, then it is valid
        #If a move takes out a piece(s), then a key of 1 is returned, the number of pieces taken out will be the following number
        #If the move doesn't take out any pieces, then it's a 2

        #The stone played will be its own single string
        if  not found_connection_point:
            connection_point = Connection()
            connection_point.add_connection (Coordinate(row,col))
            connection_point.identify_liberties()

        all_liberties_taken = False
        move_removes_enemies = False
        pieces_taken_out = 0

        connection_point.blocked_liberties()

        if connection_point.all_liberties_taken():
            all_liberties_taken = True

        #Assume all enemy pieces are currently safe, now check if when the move has been made

        enemy_connection = None

        if colour == 'W':
            enemy_connection = self.black_connections

        elif colour == 'B':
            enemy_connection = self.white_connections

        last_index = 0

        for i in enemy_connection:
            i.blocked_liberties()

            #Conjecture: it's impossible to take out more than one string of stones in one move
            #If this conjecture turns out to be false I'll have to edit this
            if i.all_liberties_taken():
                move_removes_enemies = True
                pieces_taken_out = len(i.connection)
                break

            last_index += 1

        #Reset everything to how it was
        if found_connection_point:
            del connection_point[-1]
            
            
        if all_liberties_taken and not move_removes_enemies:
            return False
