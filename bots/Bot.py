

import random
from typing import List, Tuple, Optional, Set
from models.Field import OwnField
from models.Field import EnemyField
from models.Ship import Ship
from models.ShipOrientation import ShipOrientation
from models.FieldState import FieldState
from placements.RandomShipPlacer import RandomShipPlacer


class Bot:
    
    def __init__(self, name: str = "Bot", difficulty = 1, field_size: int = 10):
        self.name = name
        self.field_size = field_size
        self.my_field = OwnField(field_size)
        self.enemy_view = EnemyField(field_size) 
        self.ships_placed = False
        self.difficulty = 0
        
    def place_ships(self) -> None:
        placer = RandomShipPlacer(self.field_size)
        ships = placer.place_ships_randomly()
        
        for ship in ships:
            self.my_field.add_ship(ship)
        
        self.ships_placed = True
        print(f"🤖 {self.name} расставил корабли")
    
    def make_move(self) -> Tuple[int, int]:

        raise NotImplementedError
    
