from typing import Tuple, List
from models.Field import OwnField, EnemyField
from models.Ship import Ship
from placements.ShipPlacer import ShipPlacer
from bots.ShootingStrategy import ShootingStrategy


class Bot:

    def __init__(self, name: str = "Bot", difficulty: int = 1, field_size: int = 10):
        self.name = name
        self.field_size = field_size
        self.own_field = OwnField(field_size)
        self.enemy_field = EnemyField(field_size)
        self.ships_placed = False
        self.difficulty = difficulty

        # Для стратегии охотника
        self._hits: List[Tuple[int, int]] = []
        self._hunter_phase: int = 4

    def place_ships(self, method: str = "random") -> None:
        ships = ShipPlacer.place_ships(method, self.field_size)

        for ship in ships:
            self.own_field.add_ship(ship)

        self.ships_placed = True
        print(f"🤖 {self.name} расставил корабли")

    def make_move(self) -> Tuple[int, int]:
        """Делает ход в зависимости от сложности"""
        if self.difficulty == 1:
            return ShootingStrategy.make_move_random(self.enemy_field, self._hits)
        elif self.difficulty == 2:
            return ShootingStrategy.make_move_diagonal(self.enemy_field, self._hits)
        elif self.difficulty == 3:
            return ShootingStrategy.make_move_hunter(
                self.enemy_field,
                hits=self._hits,
                phase=self._hunter_phase
            )
        else:
            return ShootingStrategy.make_move_random(self.enemy_field, self._hits)

    def register_shot_result(self, x: int, y: int, is_hit: bool, is_destroyed: bool = False) -> None:
        """
        Регистрирует результат выстрела (для стратегии охотника).
        Вызывай этот метод ПОСЛЕ make_move, когда узнал результат.
        """
        # Обновляем поле зрения
        self.enemy_field.shoot_result(x, y, is_hit, is_destroyed)

        # Обновляем список попаданий для охотника
        if self.difficulty == 3:
            self._hits = ShootingStrategy.update_hits(
                self._hits, x, y, is_hit, is_destroyed
            )

            # Если корабль уничтожен — сбрасываем фазу или понижаем
            if is_destroyed:
                # Можно добавить логику понижения фазы при уничтожении больших кораблей
                pass