import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from typing import List, Optional
from models.Ship import Ship
from models.ShipOrientation import ShipOrientation
from models.FieldState import FieldState

class RandomShipPlacer:

    SHIPS_CONFIG = [
        (4, 1),  # 1 корабль на 4 палубы
        (3, 2),  # 2 корабля на 3 палубы
        (2, 3),  # 3 корабля на 2 палубы
        (1, 4),  # 4 корабля на 1 палубу
    ]
    
    def __init__(self, field_size: int = 10):
        self.field_size = field_size
        self.field = [[FieldState.EMPTY for _ in range(field_size)] for _ in range(field_size)]
        self.ships: List[Ship] = []
        self.forbidden_cells = set()
    
    def place_ships_randomly(self) -> List[Ship]:
        """Размещает все корабли случайным образом"""
        self.ships = []
        self.field = [[FieldState.EMPTY for _ in range(self.field_size)] for _ in range(self.field_size)]
        self.forbidden_cells = set()
        
        # Размещаем корабли от большего к меньшему
        for ship_size, count in sorted(self.SHIPS_CONFIG, reverse=True):
            for _ in range(count):
                ship = self._try_place_ship(ship_size)
                if ship is None:
                    # Если не получилось разместить, пробуем заново
                    return self.place_ships_randomly()
                self.ships.append(ship)
        
        return self.ships
    
    def _try_place_ship(self, size: int, max_attempts: int = 100) -> Optional[Ship]:
        """Пытается разместить один корабль заданного размера"""
        for _ in range(max_attempts):
            # Случайно выбираем ориентацию
            orientation = random.choice([
                ShipOrientation.UP,
                ShipOrientation.RIGHT,
                ShipOrientation.DOWN,
                ShipOrientation.LEFT
            ])
            
            # Случайно выбираем начальные координаты
            x = random.randint(0, self.field_size - 1)
            y = random.randint(0, self.field_size - 1)
            
            # Создаем временный корабль для получения координат палуб
            temp_ship = Ship(x, y, size, orientation)
            valid = True
            
            # Проверяем все палубы корабля
            for nx, ny in temp_ship.decks_coordinates:
                # Проверяем границы поля
                if nx < 0 or nx >= self.field_size or ny < 0 or ny >= self.field_size:
                    valid = False
                    break
                
                # Проверяем, можно ли поставить палубу здесь
                if not self._can_place_deck(nx, ny):
                    valid = False
                    break
            
            if valid:
                # Размещаем корабль
                self._place_ship_on_field(temp_ship)
                return temp_ship
        
        return None
    
    def _can_place_deck(self, x: int, y: int) -> bool:
        # Проверяем, не запрещена ли клетка
        if (x, y) in self.forbidden_cells:
            return False
        
        # Проверяем все соседние клетки (включая диагональные)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.field_size and 0 <= ny < self.field_size:
                    if self.field[nx][ny] != FieldState.EMPTY:
                        return False
        return True
    
    def _place_ship_on_field(self, ship: Ship) -> None:
        """Размещает корабль на поле"""
        for x, y in ship.decks_coordinates:
            self.field[x][y] = FieldState.UNDAMAGED
            
            # Добавляем в запретные все клетки вокруг палубы
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.field_size and 0 <= ny < self.field_size:
                        self.forbidden_cells.add((nx, ny))
    

def create_ships_for_field() -> List[Ship]:

    placer = RandomShipPlacer(10)
    return placer.place_ships_randomly()
