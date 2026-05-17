from fastapi import WebSocket

from models.Field import OwnField, EnemyField
from placements.ShipPlacer import ShipPlacer


class User:
    def __init__(self):
        self.username: str | None = None
        self.websocket: WebSocket | None = None
        self.own_field: OwnField = OwnField()
        self.enemy_field: EnemyField = EnemyField()

    def auto_place_ships(self, method: str = "random") -> None:
        ships = ShipPlacer.place_ships(method, self.own_field.FIELD_SIZE)
        for ship in ships:
            self.own_field.add_ship(ship)