import random, time
random.seed(time.time())

def AI (board_ref, colour):
    possible_moves = board_ref.get_possible_moves(colour)

    return random.choice(possible_moves)

