from Bot import *
import random
#TODO Ебаклаки стреляют по разным координатам
class RandomBot(Bot):
    
    def __init__(self, name: str = "RandomBot", difficulty=1, field_size: int = 10):
        super().__init__(name, field_size)
        self.available_shots: List[Tuple[int, int]] = []
        for x in range(field_size):
            for y in range(field_size):
                self.available_shots.append((x, y))
        # Убираем инициализацию enemy_coords из __init__
    
    def _update_enemy_coords(self):
        """Обновляет список координат, где предположительно есть корабли противника"""
        self.enemy_coords = []
        for x in range(self.enemy_view.FIELD_SIZE):
            for y in range(self.enemy_view.FIELD_SIZE):
                state = self.enemy_view.get_cell_display(x, y)
                # Если клетка не повреждена и не было промаха - там может быть корабль
                if state == FieldState.UNDAMAGED:
                    self.enemy_coords.append((x, y))
    
    def make_move(self) -> Tuple[int, int]:
        if not self.available_shots:
            raise ValueError("Нет доступных клеток для выстрела")
        
        # Обновляем информацию о возможных кораблях противника
        self._update_enemy_coords()
        
        if self.difficulty == 1 and random.randint(1, 10) <= 2:
            # Стреляем только по клеткам, где могут быть корабли
            enemy_ship_coords = [coord for coord in self.enemy_coords 
                                if coord in self.available_shots]
            if enemy_ship_coords:
                x, y = random.choice(enemy_ship_coords)
            else:
                x, y = random.choice(self.available_shots)
        else:
            x, y = random.choice(self.available_shots)
        
        self.available_shots.remove((x, y))
        return x, y