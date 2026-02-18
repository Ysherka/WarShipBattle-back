from typing import Final


from models.FieldState import FieldState
from models.Ship import Ship


class Field:
    def __init__(self, field_size: int = 10):
        self.FIELD_SIZE: Final[int] = field_size
        self.cells: list[list[FieldState]] = \
            [[FieldState.EMPTY for _ in range(self.FIELD_SIZE)] for _ in range(self.FIELD_SIZE)]
        self.ships: list[Ship] = []


    def add_ship(self, ship: Ship) -> None:
        self.ships.append(ship)
        for x, y in ship.decks_coordinates:
            self.cells[x][y] = FieldState.UNDAMAGED


    def check_shoot(self, x: int, y: int) -> None:
        if self.cells[x][y] == FieldState.UNDAMAGED:
            self.cells[x][y] = FieldState.DAMAGED
        elif self.cells[x][y] == FieldState.EMPTY:
            self.cells[x][y] = FieldState.MISS
