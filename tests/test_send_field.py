from game import Game
from models.User import User


def test_send_field():
    field = [
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 4, 4, 4, 4, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 2, 2],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [2, 2, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [2, 2, 0, 0, 3, 3, 3, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 3, 3, 3, 0, 0]
    ]

    user: User = User()
    game = Game(user)
    game.add_ships_int(field)
    print()
    for row in user.own_field.cells:
        print([j.value for j in row])
