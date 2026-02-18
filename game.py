from models.Field import Field
from models.Ship import Ship
from models.ShipOrientation import ShipOrientation


class Game:
    def __init__(self):
        self.field = Field()

    def add_ship(self, x: int, y: int, length: int, orientation: ShipOrientation):
        ship = Ship(x, y, length, orientation)
        self.field.add_ship(ship)

    def shoot(self, x: int, y: int):
        self.field.check_shoot(x, y)