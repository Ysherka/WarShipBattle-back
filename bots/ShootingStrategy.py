import random
from typing import List, Tuple, Optional, Set
from models.Field import EnemyField
from models.FieldState import FieldState


class ShootingStrategy:
    """Утилитарный класс со стратегиями стрельбы бота"""
    
    @staticmethod
    def make_move_random(enemy_field: EnemyField) -> Tuple[int, int]:
        """Случайный выстрел по неизвестным клеткам"""
        available = []
        for x in range(enemy_field.FIELD_SIZE):
            for y in range(enemy_field.FIELD_SIZE):
                if enemy_field.get_shot_available(x, y):
                    available.append((x, y))
        
        if not available:
            raise ValueError("No available shots")
        
        return random.choice(available)
    
    @staticmethod
    def make_move_diagonal(enemy_field: EnemyField, history: List[Tuple[int, int]] = None) -> Tuple[int, int]:
        """Выстрел по диагонали (заглушка)"""
        # TODO: реализовать диагональную стратегию
        # Пока делегируем случайной
        return ShootingStrategy.make_move_random(enemy_field)
    
    @staticmethod
    def make_move_hunter(enemy_field: EnemyField, history: List[Tuple[int, int]] = None) -> Tuple[int, int]:
        """Охота на большие корабли (заглушка)"""
        # TODO: реализовать охоту на большие корабли
        # Пока делегируем случайной
        return ShootingStrategy.make_move_random(enemy_field)