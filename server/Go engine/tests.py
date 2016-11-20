def test1():

        board = [ [' ','W','W'],
          [' ','W','W'],
          ['W','B','B']]


        b = Board(3)
        b.init_board(board)

        b.update_connections()

        for i in b.connections:
            for j in i.connection:
                print ([j.row,j.col], end = " ")

        print("\nLiberties: ", end = " ")
        for j in i.liberties:
            print ([j.row,j.col], end = " ")

        print()

def kennyAi (board,stone):
    moves = board.get_possible_moves(stone)

    choice = random.choice(moves)

    return choice

def display_board(board):

    for i in range(board.board_size):
        for j in range(board.board_size):
            if board.board[i][j] == " ":
                print(".",end = " ")
            else:
                print(board.board[i][j], end = " ")

        print()
        
def test2Game():
    board_size = 9
    board =  Board(board_size)

    board.init_board()
    display_board(board)
    print("\n\n")
    
    human_stone = random.choice (["W","B"])
    enemy_stone = ""

    if human_stone == "W":
        enemy_stone = "B"

    else:
        enemy_stone = "W"

    turn = "B"

    gameOver = False

    while True:
        if turn == enemy_stone:
            move = kennyAi(board,enemy_stone)

        elif turn == human_stone:
            row = int(input("Please enter a row: "))
            col = int(input("Please enter a column: "))

            validity = board.is_move_legal(row,col,human_stone)

            while not validity:
                row = int(input("Please enter a valid row: "))
                col = int(input("Please enter a column: "))

                validity = board.is_move_legal(row, col, human_stone)

            move = [Coordinate(row,col),validity]
        
        board.place_stone (move[0].row,move[0].col,turn,move[1],True)
        display_board(board)
        print("\n\n")

        if turn == "B":
            turn = "W"
        else:
            turn = "B"



    
#test2Game()
def ko_rule_test():
    b = [['.', '.', '.', '.', '.', '.', '.', '.', '.'],
         ['.', '.', '.', '.', '.', 'B', 'W', '.', '.'],
         ['.', '.', '.', '.', 'B', 'W', '.', 'W', '.'],
         ['.', '.', '.', '.', '.', 'B', 'W', '.', '.'],
         ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
         ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
         ['.', '.', '.', '.', '.', '.', '.', '.', 'W'],
         ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
         ['.', '.', '.', '.', '.', '.', '.', '.', '.']]

    for i in range(9):
        for j in range(9):
            if b[i][j] == '.':
                b[i][j] = " "

    board = Board(9)

    board.init_board(b)
    display_board(board)
    print("\n\n")
    turn = "B"

    p1 = "B"
    p2 = "W"

    while True:

        row = int(input("Please enter a row: "))
        col = int(input("Please enter a column: "))

        validity = board.is_move_legal(row, col, turn)

        while not validity:
            row = int(input("Please enter a valid row: "))
            col = int(input("Please enter a column: "))

            validity = board.is_move_legal(row, col, turn)

        move = [Coordinate(row, col), validity]

        board.place_stone(move[0].row, move[0].col, turn, move[1], True)
        display_board(board)
        print("\n\n")

        if turn == "B":
            turn = "W"
        else:
            turn = "B"

ko_rule_test()

def testn():
    c = Board(9)
    b = [['B', 'W', 'B', '.', '.', '.', '.', '.', 'W'],
         ['W', '.', '.', '.', '.', 'B', '.', '.', '.'],
         ['.', '.', '.', '.', 'B', 'W', 'B', 'W', '.'],
         ['.', '.', '.', '.', 'B', 'W', 'B', '.', '.'],
         ['.', '.', '.', '.', 'B', 'W', 'B', '.', '.'],
         ['.', '.', '.', '.', '.', 'B', '.', '.', '.'],
         ['.', '.', '.', '.', '.', '.', '.', 'W', 'W'],
         ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
         ['W', '.', '.', '.', '.', '.', '.', '.', '.']]

    for i in range(9):
        for j in range(9):
            if b[i][j] == '.':
                b[i][j] = " "
    c.init_board(b)

    c.update_connections()

    for i in c.white_connections:
        if i.all_liberties_taken():
            print("Yes ", i.connection[0].row,i.connection[0].col)
#Now I have tested everything, I must verify a move, by ensuring that when a 
