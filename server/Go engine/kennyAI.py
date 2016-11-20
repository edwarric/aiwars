import random, time
random.seed(time.time())

def sort_moves(moves):

    while True:
        did_sort = False
        for i in range(len(moves)-1):
            current = moves[i]
            if isinstance (current,str):
                moves[i] = moves[i + 1]
                moves[i + 1] = current
                sorted = True
                continue

            if current[1].num_enemies_taken_out < moves[i+1][1].num_enemies_taken_out:
                moves[i] = moves[i+1]
                moves[i+1] = current
                sorted = True

        if not did_sort:
            break



def AI (board_ref, colour):
    possible_moves = board_ref.get_possible_moves(colour)

    sort_moves(possible_moves)

    num =  random.randint(1,10)

    if num < 8:
        return random.choice(possible_moves[0:3])


    return random.choice(possible_moves)

