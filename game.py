from functools import singledispatchmethod

from models.Field import BaseField, OwnField, EnemyField
from models.FieldState import FieldState
from models.Ship import Ship
from models.ShipOrientation import ShipOrientation
from models.User import User
from bots.Bot import Bot


class Game:
    def __init__(self, user: User | None = None, enemy: User | None = None, bot: Bot | None = None):
        self.user: User | None = user
        self.enemy: User | None = enemy
        self.bot: Bot | None = bot  # ◆ Композиция (Game создаёт Bot)
        self.turn: bool = True

    """
    здесь инты обозначают размер корабля
    0 - пусто 
    1 - однопалубный корабль
    2 - двухпалубный
    3 - трехпалубный
    4 - четырехпалубный
    """

    @staticmethod
    def field_to_ship_list(field: list[list[int]]) -> list[Ship]:
        if not field or not field[0]:
            return []

        rows = len(field)
        cols = len(field[0])
        visited = [[False] * cols for _ in range(rows)]
        ships = []

        for y in range(rows):
            for x in range(cols):
                if field[y][x] == 0 or visited[y][x]:
                    continue

                length = field[y][x]

                # Проверяем горизонтальное направление (вправо)
                if x + length <= cols and all(
                        field[y][x + i] == length and not visited[y][x + i] for i in range(length)):
                    is_valid = True
                    if x > 0 and field[y][x - 1] == length:
                        is_valid = False
                    if x + length < cols and field[y][x + length] == length:
                        is_valid = False

                    if is_valid:
                        vertical_check = True
                        for i in range(length):
                            if y > 0 and field[y - 1][x + i] == length:
                                vertical_check = False
                                break
                            if y < rows - 1 and field[y + 1][x + i] == length:
                                vertical_check = False
                                break

                        if vertical_check:
                            ship = Ship(x, y, length, ShipOrientation.RIGHT)
                            ships.append(ship)
                            for i in range(length):
                                visited[y][x + i] = True
                            continue

                # Проверяем вертикальное направление (вниз)
                if y + length <= rows and all(
                        field[y + i][x] == length and not visited[y + i][x] for i in range(length)):
                    ship = Ship(x, y, length, ShipOrientation.DOWN)
                    ships.append(ship)
                    for i in range(length):
                        visited[y + i][x] = True

        return ships

    def add_ships(self, ships: list[Ship]):
        for ship in ships:
            self.user.own_field.add_ship(ship)

    def add_ships_int(self, field: list[list[int]]):
        ships: list[Ship] = self.field_to_ship_list(field)
        for ship in ships:
            self.user.own_field.add_ship(ship)

    def shoot(self, row: int, col: int):
        self.user.own_field.shoot(row, col)