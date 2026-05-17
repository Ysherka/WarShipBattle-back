import random
from typing import List, Optional
from models.Ship import Ship
from models.ShipOrientation import ShipOrientation
from models.FieldState import FieldState


class ShipPlacer:

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
    
    @staticmethod
    def place_ships(method: str = "random", field_size: int = 10) -> List[Ship]:
        """Фабричный метод: выбирает способ расстановки"""
        placer = ShipPlacer(field_size)
        
        if method == "random":
            return placer._place_randomly()
        elif method == "perelman":
            return placer._place_perelman()
        else:
            raise ValueError(f"Unknown placement method: {method}")
    
    # ==================== СЛУЧАЙНАЯ РАССТАНОВКА ====================
    
    def _place_randomly(self) -> List[Ship]:
        """Случайная расстановка кораблей"""
        self.ships = []
        self.field = [[FieldState.EMPTY for _ in range(self.field_size)] for _ in range(self.field_size)]
        self.forbidden_cells = set()
        
        # Размещаем корабли от большего к меньшему
        for ship_size, count in sorted(self.SHIPS_CONFIG, reverse=True):
            for _ in range(count):
                ship = self._try_place_ship_random(ship_size)
                if ship is None:
                    return self._place_randomly()  # Перезапуск при неудаче
                self.ships.append(ship)
        
        return self.ships
    
    def _try_place_ship_random(self, size: int, max_attempts: int = 100) -> Optional[Ship]:
        """Пытается разместить один корабль случайным образом"""
        for _ in range(max_attempts):
            orientation = random.choice([ShipOrientation.RIGHT, ShipOrientation.DOWN])
            x = random.randint(0, self.field_size - 1)
            y = random.randint(0, self.field_size - 1)
            
            temp_ship = Ship(x, y, size, orientation)
            if self._is_valid_placement(temp_ship):
                self._place_ship_on_field(temp_ship)
                return temp_ship
        
        return None
    
    # ==================== РАССТАНОВКА ПЕРЕЛЬМАНА ====================
    
    def _place_perelman(self) -> List[Ship]:
        """
        Расстановка Перельмана:
        - Большие корабли (4, 3, 3) — близко к одному из краёв поля
        - Малые корабли (2, 2, 2, 1, 1, 1, 1) — рассредоточены в оставшемся пространстве
        """
        self.ships = []
        self.field = [[FieldState.EMPTY for _ in range(self.field_size)] for _ in range(self.field_size)]
        self.forbidden_cells = set()
        
        # Выбираем край для больших кораблей (0=верх, 1=право, 2=низ, 3=левая)
        edge = random.randint(0, 3)
        
        # Сначала размещаем большие корабли (4 и 3-палубные) у края
        big_ships_config = [(size, count) for size, count in self.SHIPS_CONFIG if size >= 3]
        small_ships_config = [(size, count) for size, count in self.SHIPS_CONFIG if size < 3]
        
        # Размещаем большие корабли у края
        for ship_size, count in big_ships_config:
            for _ in range(count):
                ship = self._try_place_near_edge(ship_size, edge)
                if ship is None:
                    # Если не удалось у края — пробуем случайно
                    ship = self._try_place_ship_random(ship_size)
                if ship is None:
                    return self._place_perelman()  # Перезапуск
                self.ships.append(ship)
        
        # Размещаем малые корабли в оставшемся пространстве (подальше от края)
        for ship_size, count in small_ships_config:
            for _ in range(count):
                ship = self._try_place_away_from_edge(ship_size, edge)
                if ship is None:
                    ship = self._try_place_ship_random(ship_size)
                if ship is None:
                    return self._place_perelman()  # Перезапуск
                self.ships.append(ship)
        
        return self.ships
    
    def _try_place_near_edge(self, size: int, edge: int, max_attempts: int = 50) -> Optional[Ship]:
        """
        Пытается разместить корабль близко к указанному краю.
        edge: 0=верх, 1=право, 2=низ, 3=левая
        """
        margin = 3  # Насколько близко к краю (0-2 клетки от края)
        
        for _ in range(max_attempts):
            # Выбираем ориентацию в зависимости от края
            if edge in (0, 2):  # Верх/низ — горизонтальные корабли лучше
                orientation = random.choice([ShipOrientation.RIGHT, ShipOrientation.DOWN])
            else:  # Лево/право — вертикальные корабли лучше
                orientation = random.choice([ShipOrientation.RIGHT, ShipOrientation.DOWN])
            
            # Генерируем координаты близко к краю
            if edge == 0:  # Верхний край (y = 0..margin)
                x = random.randint(0, self.field_size - 1)
                y = random.randint(0, margin)
            elif edge == 1:  # Правый край (x = size-margin..size-1)
                x = random.randint(self.field_size - margin - size, self.field_size - 1)
                y = random.randint(0, self.field_size - 1)
            elif edge == 2:  # Нижний край (y = size-margin..size-1)
                x = random.randint(0, self.field_size - 1)
                y = random.randint(self.field_size - margin - size, self.field_size - 1)
            else:  # Левый край (x = 0..margin)
                x = random.randint(0, margin)
                y = random.randint(0, self.field_size - 1)
            
            temp_ship = Ship(x, y, size, orientation)
            if self._is_valid_placement(temp_ship):
                self._place_ship_on_field(temp_ship)
                return temp_ship
        
        return None
    
    def _try_place_away_from_edge(self, size: int, edge: int, max_attempts: int = 100) -> Optional[Ship]:
        """
        Пытается разместить корабль подальше от указанного края.
        """
        safe_zone = 4  # Минимальное расстояние от края
        
        for _ in range(max_attempts):
            orientation = random.choice([ShipOrientation.RIGHT, ShipOrientation.DOWN])
            
            # Генерируем координаты подальше от края
            if edge == 0:  # Далеко от верха (y >= safe_zone)
                x = random.randint(0, self.field_size - 1)
                y = random.randint(safe_zone, self.field_size - 1)
            elif edge == 1:  # Далеко от правого края (x <= size - safe_zone - size)
                x = random.randint(0, self.field_size - safe_zone - size)
                y = random.randint(0, self.field_size - 1)
            elif edge == 2:  # Далеко от низа (y <= size - safe_zone - size)
                x = random.randint(0, self.field_size - 1)
                y = random.randint(0, self.field_size - safe_zone - size)
            else:  # Далеко от левого края (x >= safe_zone)
                x = random.randint(safe_zone, self.field_size - 1)
                y = random.randint(0, self.field_size - 1)
            
            # Проверяем, что не вышли за границы
            temp_ship = Ship(x, y, size, orientation)
            if self._is_valid_placement(temp_ship):
                self._place_ship_on_field(temp_ship)
                return temp_ship
        
        return None
    
    # ==================== ОБЩИЕ МЕТОДЫ ====================
    
    def _is_valid_placement(self, ship: Ship) -> bool:
        """Проверяет, можно ли разместить корабль"""
        for x, y in ship.decks_coordinates:
            # Проверка границ
            if not (0 <= x < self.field_size and 0 <= y < self.field_size):
                return False
            
            # Проверка запретных клеток (включая соседние)
            if not self._can_place_deck(x, y):
                return False
        
        return True
    
    def _can_place_deck(self, x: int, y: int) -> bool:
        """Проверяет, можно ли поставить одну палубу в клетку"""
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
        """Размещает корабль на поле и помечает окрестности"""
        for x, y in ship.decks_coordinates:
            self.field[x][y] = FieldState.UNDAMAGED
            
            # Добавляем в запретные все клетки вокруг палубы
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.field_size and 0 <= ny < self.field_size:
                        self.forbidden_cells.add((nx, ny))