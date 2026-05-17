from typing import Tuple
from models.Field import OwnField, EnemyField
from models.Ship import Ship
from placements.ShipPlacer import ShipPlacer
from bots.ShootingStrategy import ShootingStrategy


class Bot:
    
    def __init__(self, name: str = "Bot", difficulty: int = 1, field_size: int = 10):
        self.name = name
        self.field_size = field_size
        self.own_field = OwnField(field_size)       # ◆ Композиция
        self.enemy_field = EnemyField(field_size)   # ◆ Композиция
        self.ships_placed = False
        self.difficulty = difficulty
        
    def place_ships(self, method: str = "random") -> None:
        ships = ShipPlacer.place_ships(method, self.field_size)
        
        for ship in ships:
            self.own_field.add_ship(ship)
        
        self.ships_placed = True
        print(f"🤖 {self.name} расставил корабли")
    
    def make_move(self) -> Tuple[int, int]:
        """Делает ход в зависимости от сложности"""
        if self.difficulty == 1:
            return ShootingStrategy.make_move_random(self.enemy_field)
        elif self.difficulty == 2:
            return ShootingStrategy.make_move_diagonal(self.enemy_field)
        elif self.difficulty == 3:
            return ShootingStrategy.make_move_hunter(self.enemy_field)
        else:
            return ShootingStrategy.make_move_random(self.enemy_field)