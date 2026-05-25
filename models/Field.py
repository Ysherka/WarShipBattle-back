from typing import Final, List, Tuple, Optional
from abc import ABC, abstractmethod
from models.FieldState import FieldState
from models.Ship import Ship
from models.ShipOrientation import ShipOrientation


class BaseField(ABC):
    
    def __init__(self, field_size: int = 10):
        self.FIELD_SIZE: Final[int] = field_size
        self.cells: List[List[FieldState]] = [
            [FieldState.EMPTY for _ in range(self.FIELD_SIZE)] 
            for _ in range(self.FIELD_SIZE)
        ]
    
    @abstractmethod
    def get_cell_display(self, row: int, col: int) -> FieldState:
        pass


class EnemyField(BaseField):

    def __init__(self, field_size: int = 10):
        super().__init__(field_size)
        self.known_cells: List[List[bool]] = [
            [False for _ in range(self.FIELD_SIZE)]
            for _ in range(self.FIELD_SIZE)
        ]

    def shoot_result(self, row: int, col: int, is_hit: bool, is_destroyed: bool = False) -> None:
        self.known_cells[row][col] = True

        if is_destroyed:
            self.cells[row][col] = FieldState.DESTROYED
        elif is_hit:
            self.cells[row][col] = FieldState.DAMAGED
        else:
            self.cells[row][col] = FieldState.MISS

    def get_cell_display(self, row: int, col: int) -> FieldState:
        if self.known_cells[row][col]:
            return self.cells[row][col]
        return FieldState.EMPTY

    def get_shot_available(self, row: int, col: int) -> bool:
        return not self.known_cells[row][col]

class OwnField(BaseField):
    
    def __init__(self, field_size: int = 10):
        super().__init__(field_size)
        self.ships: List[Ship] = []
    
    def add_ship(self, ship: Ship) -> bool:
        #######################################################
        # эта проверка есть на фронте поэтому я ее закоментил #
        #######################################################
        # if not self.__can_place_ship(ship):
        #     return False
        
        self.ships.append(ship)
        for row, col in ship.decks_coordinates:
            self.cells[row][col] = FieldState.UNDAMAGED
        return True

    def __can_place_ship(self, ship: Ship) -> bool:
        # Проверка границ поля
        for row, col in ship.decks_coordinates:
            if not (0 <= row < self.FIELD_SIZE and 0 <= col < self.FIELD_SIZE):
                return False
        
        # Проверка соседних клеток (корабли не должны касаться)
        for row, col in ship.decks_coordinates:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = row + dx, col + dy
                    if (0 <= nx < self.FIELD_SIZE and 0 <= ny < self.FIELD_SIZE
                            and self.cells[ny][nx] != FieldState.EMPTY):
                        return False
        return True

    def shoot(self, row: int, col: int, enemy_field: EnemyField | None = None) -> Tuple[bool, Optional[Ship]]:
        if self.cells[row][col] == FieldState.UNDAMAGED:
            self.cells[row][col] = FieldState.DAMAGED
            
            # Проверяем, уничтожен ли корабль
            ship = self.__get_ship_at(row, col)
            print(f"inner {ship}")
            if ship:
                print(f"inner {self.__is_ship_destroyed(ship)=}")
            if ship and self.__is_ship_destroyed(ship):
                self.__mark_ship_as_destroyed(ship, enemy_field)
                return True, ship
            return True, None

        elif self.cells[row][col] == FieldState.EMPTY:
            self.cells[row][col] = FieldState.MISS
            return False, None
        
        return False, None  # Повторный выстрел по той же клетке

    def __get_ship_at(self, row: int, col: int) -> Optional[Ship]:
        for ship in self.ships:
            if (row, col) in ship.decks_coordinates:
                return ship
        return None

    def __is_ship_destroyed(self, ship: Ship) -> bool:
        return all(self.cells[row][col] == FieldState.DAMAGED
                   for row, col in ship.decks_coordinates)

    def __mark_ship_as_destroyed(self, ship: Ship, enemy_field: EnemyField | None) -> None:
        # 1. Помечаем все палубы корабля как уничтоженные
        for r, c in ship.decks_coordinates:
            self.cells[r][c] = FieldState.DESTROYED
            if enemy_field is not None:
                enemy_field.known_cells[r][c] = True

        # 2. Определяем границы прямоугольника вокруг корабля
        if ship.orientation == ShipOrientation.RIGHT:
            # Горизонтальный: строки от row-1 до row+1, столбцы от col-1 до col+length
            min_row, max_row = ship.row - 1, ship.row + 1
            min_col, max_col = ship.col - 1, ship.col + ship.length
        else:
            # Вертикальный: строки от row-1 до row+length, столбцы от col-1 до col+1
            min_row, max_row = ship.row - 1, ship.row + ship.length
            min_col, max_col = ship.col - 1, ship.col + 1

        # 3. Обходим клетки вокруг корабля (включая диагонали)
        for r in range(max(0, min_row), min(self.FIELD_SIZE, max_row + 1)):
            for c in range(max(0, min_col), min(self.FIELD_SIZE, max_col + 1)):
                # Если это не клетка самого корабля — помечаем промахом
                if self.cells[r][c] != FieldState.DESTROYED:
                    self.cells[r][c] = FieldState.MISS

                if enemy_field is not None:
                    enemy_field.known_cells[r][c] = True

    def get_cell_display(self, row: int, col: int) -> FieldState:
        return self.cells[row][col]
