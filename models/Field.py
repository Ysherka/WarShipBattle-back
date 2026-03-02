from typing import Final, List, Tuple, Optional
from abc import ABC, abstractmethod
from models.FieldState import FieldState
from models.Ship import Ship

class BaseField(ABC):
    
    def __init__(self, field_size: int = 10):
        self.FIELD_SIZE: Final[int] = field_size
        self.cells: List[List[FieldState]] = [
            [FieldState.EMPTY for _ in range(self.FIELD_SIZE)] 
            for _ in range(self.FIELD_SIZE)
        ]
    
    @abstractmethod
    def get_cell_display(self, x: int, y: int) -> FieldState:
        pass


class OwnField(BaseField):
    
    def __init__(self, field_size: int = 10):
        super().__init__(field_size)
        self.ships: List[Ship] = []
    
    def add_ship(self, ship: Ship) -> bool:
        if not self.__can_place_ship(ship):
            return False
        
        self.ships.append(ship)
        for x, y in ship.decks_coordinates:
            self.cells[x][y] = FieldState.UNDAMAGED
        return True

    def __can_place_ship(self, ship: Ship) -> bool:
        # Проверка границ поля
        for x, y in ship.decks_coordinates:
            if not (0 <= x < self.FIELD_SIZE and 0 <= y < self.FIELD_SIZE):
                return False
        
        # Проверка соседних клеток (корабли не должны касаться)
        for x, y in ship.decks_coordinates:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < self.FIELD_SIZE and 0 <= ny < self.FIELD_SIZE 
                            and self.cells[nx][ny] != FieldState.EMPTY):
                        return False
        return True
    
    def shoot(self, x: int, y: int) -> Tuple[bool, Optional[Ship]]:
        if self.cells[x][y] == FieldState.UNDAMAGED:
            self.cells[x][y] = FieldState.DAMAGED
            
            # Проверяем, уничтожен ли корабль
            ship = self.__get_ship_at(x, y)
            if ship and self.__is_ship_destroyed(ship):
                self.__mark_ship_as_destroyed(ship)
                return True, ship
            return True, None
            
        elif self.cells[x][y] == FieldState.EMPTY:
            self.cells[x][y] = FieldState.MISS
            return False, None
        
        return False, None  # Повторный выстрел по той же клетке

    def __get_ship_at(self, x: int, y: int) -> Optional[Ship]:
        for ship in self.ships:
            if (x, y) in ship.decks_coordinates:
                return ship
        return None

    def __is_ship_destroyed(self, ship: Ship) -> bool:
        return all(self.cells[x][y] == FieldState.DAMAGED 
                  for x, y in ship.decks_coordinates)

    def __mark_ship_as_destroyed(self, ship: Ship) -> None:
        for x, y in ship.decks_coordinates:
            self.cells[x][y] = FieldState.DESTROYED
    
    def get_cell_display(self, x: int, y: int) -> FieldState:
        return self.cells[x][y]

class EnemyField(BaseField):
    
    def __init__(self, field_size: int = 10):
        super().__init__(field_size)
        self._known_cells: List[List[bool]] = [
            [False for _ in range(self.FIELD_SIZE)] 
            for _ in range(self.FIELD_SIZE)
        ]
    
    def shoot_result(self, x: int, y: int, is_hit: bool, is_destroyed: bool = False) -> None:
        self._known_cells[x][y] = True
        
        if is_destroyed:
            self.cells[x][y] = FieldState.DESTROYED
        elif is_hit:
            self.cells[x][y] = FieldState.DAMAGED
        else:
            self.cells[x][y] = FieldState.MISS
    
    def get_cell_display(self, x: int, y: int) -> FieldState:
        if self._known_cells[x][y]:
            return self.cells[x][y]
        return FieldState.EMPTY
    
    def get_shot_available(self, x: int, y: int) -> bool:
        return not self._known_cells[x][y]